from rest_framework import serializers

from django.db.models import Count
from django.db.models import Q
from django.db.models import Sum

from courses.models import Track
from courses.models import Unit
from courses.models import Lesson
from courses.models import Exercise
from courses.models import Submission


class PreviousExerciseSerializerField(serializers.Field):
    def to_representation(self, obj):
        prev = Exercise.objects.filter(next_exercise__id=obj.id).first()
        return prev.id if prev else ''

    def to_internal_value(self, data):
        if data:
            prev = Exercise.objects.get(id=data)
        else:
            prev = None
        return { 'previous_exercise': prev }


class ExerciseSerializer(serializers.ModelSerializer):
    entity_type = serializers.SerializerMethodField()
    previous_exercise = PreviousExerciseSerializerField(source='*', required=False)
    default_code = serializers.CharField(trim_whitespace=False, required=False, allow_blank=True)
    unit_test = serializers.CharField(trim_whitespace=False, required=False, allow_blank=True)

    class Meta:
        model = Exercise
        fields = (
            'id', 'name', 'entity_type', 'lecture', 'instruction', 'hint', 'default_code',
            'input_should_contain', 'input_should_not_contain', 'input_error_text',
            'input_should_contain_error_msg', 'input_should_not_contain_error_msg',
            'output_should_contain', 'output_should_not_contain', 'output_error_text',
            'output_should_contain_error_msg', 'output_should_not_contain_error_msg',
            'unit_test', 'previous_exercise', 'next_exercise', 'is_published',
            'lesson', 'unit_id', 'track_id', 'text_file_content'
        )
    
    def get_entity_type(self, obj):
        return Exercise.__name__
    

class UserExerciseSerializer(ExerciseSerializer):
    is_complete = serializers.SerializerMethodField()
    is_in_progress = serializers.SerializerMethodField()

    class Meta(ExerciseSerializer.Meta):
        fields = ExerciseSerializer.Meta.fields + (
            'is_complete', 'is_in_progress',)

    def get_is_complete(self, obj):
        user = self.context['user']
        sub = Submission.objects.filter(
            user=user, exercise=obj.id, passed=True)
        return sub.exists()

    def get_is_in_progress(self, exercise):
        user = self.context['user']
        not_passed_submissions_count = Count(
            'exercise_submission',
            filter=Q(
                exercise_submission__passed=False,
                exercise_submission__user=user,
            )
        )
        passed_submissions_count = Count(
            'exercise_submission',
            filter=Q(
                exercise_submission__passed=True,
                exercise_submission__user=user,
            )
        )
        ex = Exercise.objects.annotate(
            not_passed_submissions_count=not_passed_submissions_count
        ).annotate(
            passed_submissions_count=passed_submissions_count
        ).get(id=exercise.id)
        return (
            ex.not_passed_submissions_count > 0 and
            ex.passed_submissions_count == 0
        )


class SubmissionSerializer(serializers.ModelSerializer):
    passed = serializers.BooleanField(read_only=True, required=False)
    class Meta:
        model = Submission
        fields = [
            'id', 'submitted_code', 'exercise', 'passed', 'console_output', 'error_message'
        ]


class LessonSerializer(serializers.ModelSerializer):
    lesson_exercises = ExerciseSerializer(many=True, read_only=True)
    entity_type = serializers.SerializerMethodField()
    is_complete = serializers.BooleanField(default=False, read_only=True)

    class Meta:
        model = Lesson
        fields = (
            'id', 'name', 'entity_type', 'is_published',
            'lesson_exercises', 'unit', 'is_complete'
        )
    
    def get_entity_type(self, obj):
        return Lesson.__name__


class UserLessonSerializer(LessonSerializer):
    lesson_exercises = UserExerciseSerializer(many=True, read_only=True)
    is_complete = serializers.SerializerMethodField()
    is_in_progress = serializers.SerializerMethodField()

    class Meta(LessonSerializer.Meta):
        fields = LessonSerializer.Meta.fields + (
            'is_complete', 'is_in_progress',)

    # TODO(mutat): pass precalculated data to avoid repeated calculations
    # e.g. pass precalculated data to UserTrackSerializer, and make
    #  child serializers accept their portions as arguments
    def _progress_helper(self):
        user = self.context['user']
        completed_exercises_count = Count(
            'lesson_exercises',
            filter=Q(
                lesson_exercises__exercise_submission__passed=True,
                lesson_exercises__exercise_submission__user=user,
            ),
            distinct=True
        )
        all_exercises_count = Count('lesson_exercises', distinct=True)
        return Lesson.objects.annotate(
            completed_ex_count=completed_exercises_count
        ).annotate(
            all_ex_count=all_exercises_count
        )

    def get_is_complete(self, lesson):
        annotated_lesson = self._progress_helper().get(id=lesson.id)
        return (
            annotated_lesson.completed_ex_count == annotated_lesson.all_ex_count
        )

    def get_is_in_progress(self, lesson):
        user = self.context['user']
        not_passed_exercises_count = Count(
            'lesson_exercises',
            filter=Q(
                lesson_exercises__exercise_submission__passed=False,
                lesson_exercises__exercise_submission__user=user,
            ),
            distinct=True
        )
        annotated_lesson = self._progress_helper().annotate(
            not_passed_exercises_count=not_passed_exercises_count
        ).get(id=lesson.id)
        has_incomplete_ex = annotated_lesson.not_passed_exercises_count > 0
        return (
            has_incomplete_ex and
            annotated_lesson.completed_ex_count < annotated_lesson.all_ex_count
        )


class UnitSerializer(serializers.ModelSerializer):
    unit_lessons = LessonSerializer(many=True, read_only=True)
    entity_type = serializers.SerializerMethodField()

    class Meta:
        model = Unit
        fields = (
            'id', 'name', 'entity_type', 'description',
            'unit_lessons', 'is_published', 'track'
        )

    def get_entity_type(self, obj):
        return Unit.__name__


class UserUnitSerializer(UnitSerializer):
    unit_lessons = UserLessonSerializer(many=True, read_only=True)
    is_complete = serializers.SerializerMethodField()

    class Meta(UnitSerializer.Meta):
        fields = UnitSerializer.Meta.fields + ('is_complete',)

    def get_is_complete(self, obj):
        user = self.context['user']
        subs = Submission.objects.filter(
            exercise__lesson__unit__id=obj.id, user=user,
            passed=True
        ).distinct('exercise').count()
        exs = Exercise.objects.filter(
            lesson__unit__id=obj.id).count()
        return subs == exs


class TrackSerializer(serializers.ModelSerializer):
    track_units = UnitSerializer(many=True, read_only=True)
    entity_type = serializers.SerializerMethodField()

    class Meta:
        model = Track
        fields = (
            'id', 'name', 'entity_type', 'description',
            'track_units', 'is_published', 'programming_language'
        )

    def get_entity_type(self, obj):
        return Track.__name__


class UserTrackSerializer(TrackSerializer):
    track_units = UserUnitSerializer(many=True, read_only=True)
    is_complete = serializers.SerializerMethodField()

    class Meta(TrackSerializer.Meta):
        fields = TrackSerializer.Meta.fields + ('is_complete',)

    def get_is_complete(self, track):
        user = self.context['user']
        subs = Submission.objects.filter(
            exercise__lesson__unit__track__id=track.id,
            user=user, passed=True
        ).distinct('exercise').count()
        exs = Exercise.objects.filter(
            lesson__unit__track__id=track.id).count()
        return subs == exs
