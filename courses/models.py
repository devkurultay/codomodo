from django.db import models
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from users.models import User


class Badge(models.Model):
    name = models.CharField(_('Name of a Badge'), max_length=255)
    is_published = models.BooleanField()
    date_time_created = models.DateTimeField(_('Badge Creation Date and Time'), auto_now_add=True, editable=False)
    date_time_modified = models.DateTimeField(_('Badge Modification Date and Time'), auto_now=True)


class Track(models.Model):
    name = models.CharField(_('Name of a Track'), max_length=255)
    description = models.CharField(_('Description of a Track'), max_length=255)
    is_published = models.BooleanField()
    date_time_created = models.DateTimeField(_('Track Creation Date and Time'), auto_now_add=True, editable=False)
    date_time_modified = models.DateTimeField(_('Track Modification Date and Time'), auto_now=True)
    programming_language = models.CharField(_('Programming language name'), max_length=255)

    def __str__(self):
        return self.name

    @property
    def unit_lessons_duration(self):
        return self.track_units.filter(is_published=True).aggregate(
            Sum('unit_lessons__lesson_exercises__duration'))['unit_lessons__lesson_exercises__duration__sum']

    @property
    def units_count(self):
        return self.track_units.filter(is_published=True).count()

    @property
    def lessons_count(self):
        units = self.track_units.filter(is_published=True)
        return sum([u.lesson_exercises_count for u in units])


class Unit(models.Model):
    name = models.CharField(_('Name of a Unit'), max_length=255)
    description = models.CharField(_('Description of a Unit'), max_length=255)
    is_published = models.BooleanField()
    track = models.ForeignKey(Track, related_name='track_units', on_delete=models.CASCADE)
    date_time_created = models.DateTimeField(_('Unit Creation Date and Time'), auto_now_add=True, editable=False)
    date_time_modified = models.DateTimeField(_('Unit Modification Date and Time'), auto_now=True)

    def __str__(self):
        return self.name

    @property
    def lessons_exercises_duration(self):
        return self.unit_lessons.filter(is_published=True).aggregate(
            Sum('lesson_exercises__duration'))['lesson_exercises__duration__sum']

    @property
    def lesson_exercises_count(self):
        return self.unit_lessons.filter(is_published=True).count()


class Lesson(models.Model):
    name = models.CharField(_('Name of a Lesson'), max_length=255)
    is_published = models.BooleanField()
    unit = models.ForeignKey(Unit, related_name='unit_lessons', on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, null=True, blank=True, related_name='lesson_badge', on_delete=models.CASCADE)
    date_time_created = models.DateTimeField(_('Lesson Creation Date and Time'), auto_now_add=True, editable=False)
    date_time_modified = models.DateTimeField(_('Lesson Modification Date and Time'), auto_now=True)

    def __str__(self):
        return self.name

    @property
    def exercises_duration(self):
        return self.lesson_exercises.filter(is_published=True).aggregate(Sum('duration'))['duration__sum']

    @property
    def exercises_number(self):
        return self.lesson_exercises.filter(is_published=True).count()


CHECKER_HELP_TEXT = _('separate with comma, without spaces, like this: my_var,hello world')


class Exercise(models.Model):
    name = models.CharField(_('Name of an Exercise'), max_length=255)
    lecture = models.TextField(_('Lecture Text'))
    instruction = models.TextField(_('Instruction Text'))
    hint = models.TextField(_('Hint on how to solve the task'), blank=True, null=True)
    default_code = models.TextField(_('Default Code'), blank=True)
    duration = models.PositiveSmallIntegerField(_('Exercise duration in minutes'), default=0, blank=True)
    input_should_contain = models.CharField(
        _('List of keywords which should be presented in the submitted code'),
        help_text=CHECKER_HELP_TEXT,
        blank=True,
        max_length=255)
    input_should_contain_error_msg = models.CharField(
        _("Error text shown when the input does not contain a required item"), blank=True, max_length=255)
    input_should_not_contain = models.CharField(
        _('List of keywords which should NOT be presented in the submitted code'),
        help_text=CHECKER_HELP_TEXT,
        blank=True,
        max_length=255)
    input_should_not_contain_error_msg = models.CharField(
        _("Error text shown when the input contains an unwanted item"), blank=True, max_length=255)
    # TODO(murat): remove this field after migration
    input_error_text = models.CharField(
        _("Error text shown when expected input was not found in the written code"), blank=True, max_length=255)
    output_should_contain = models.CharField(
        _("List of keywords which should be presented in the output"),
        help_text=CHECKER_HELP_TEXT,
        blank=True,
        max_length=255)
    output_should_contain_error_msg = models.CharField(
        _("Error text shown when the output does not contain a required item"), blank=True, max_length=255)
    output_should_not_contain = models.CharField(
        _("List of keywords which should NOT be presented in the output"),
        help_text=CHECKER_HELP_TEXT,
        blank=True,
        max_length=255)
    output_should_not_contain_error_msg = models.CharField(
        _("Error text shown when the output contains an unwanted item"), blank=True, max_length=255)
    # TODO(murat): remove this field after migration
    output_error_text = models.CharField(
        _("Error text shown when expected output doesn't show up"), blank=True, max_length=255)
    unit_test = models.TextField(_('Code for testing with unit tests'), blank=True)
    next_exercise = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE)
    karma = models.PositiveSmallIntegerField(_('Point to be given for passing the current exercise'), default=1)
    is_published = models.BooleanField()
    lesson = models.ForeignKey(Lesson, related_name='lesson_exercises', on_delete=models.CASCADE)
    date_time_created = models.DateTimeField(_('Exercise Creation Date and Time'), auto_now_add=True, editable=False)
    date_time_modified = models.DateTimeField(_('Exercise Modification Date and Time'), auto_now=True)
    text_file_content = models.TextField(_('If this field has a content, file.txt tab will be shown'), blank=True)

    def __str__(self):
        return self.name

    @property
    def unit_id(self):
        return self.lesson.unit.id

    @property
    def track_id(self):
        return self.lesson.unit.track.id


class SubmissionCreationException(Exception):
    pass


class Submission(models.Model):
    user = models.ForeignKey(User, related_name='user_submission', on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, related_name='exercise_submission', on_delete=models.CASCADE)
    submitted_code = models.TextField(_('Submitted code'), blank=True)
    console_output = models.TextField(_('Result'), blank=True)
    karma = models.PositiveSmallIntegerField(_('Gained points'), default=0)
    failed_attempts = models.PositiveIntegerField(_('Amount of attempts user failed to pass the exercise'),
                                                  blank=True, default=0)
    date_time_created = models.DateTimeField(_('Submission Date and Time'), auto_now_add=True, editable=False)
    date_time_modified = models.DateTimeField(_('Submission Modification Date and Time'), auto_now=True)
    passed = models.BooleanField()
    error_message = models.TextField(_('Error message'), blank=True)

    def __str__(self):
        return '{0} submission'.format(self.user)

    @classmethod
    def create_from_exercise(cls, user, exercise, submitted_code, text_file_content, passed):
        try:
            obj = cls.objects.create(user=user, exercise=exercise)
            obj.submitted_code = submitted_code
            obj.text_file_content = text_file_content
            obj.karma = exercise.karma if passed else 0
            obj.failed_attempts += 0 if passed else 1
            obj.save()
        except Exception as e:
            raise SubmissionCreationException(e)
