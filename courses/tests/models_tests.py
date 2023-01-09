from django.test.testcases import TestCase
from fixtures.factories.courses import ExerciseFactory
from fixtures.factories.courses import LessonFactory
from fixtures.factories.courses import SubmissionFactory
from fixtures.factories.courses import UnitFactory


class ExerciseTests(TestCase):

    def test_is_complete_property(self):
        exercise = ExerciseFactory()
        self.assertFalse(exercise.is_complete)
        submission = SubmissionFactory()
        # Check if the submission is `passed = True`
        self.assertTrue(submission.passed)
        submission.exercise = exercise
        submission.save()
        # Check if the submission is `passed = True`
        # then is_complete is also True
        self.assertTrue(exercise.is_complete)


class LessonTests(TestCase):
    def setUp(self):
        exercise = ExerciseFactory()
        submission = SubmissionFactory()
        submission.exercise = exercise
        submission.save()
        self.complete_lesson = LessonFactory()
        exercise.lesson = self.complete_lesson
        exercise.save()

        self.incomplete_lesson = LessonFactory()
        incomplete_exercise = ExerciseFactory()
        incomplete_exercise.lesson = self.incomplete_lesson
        incomplete_exercise.save()

    def test_is_complete_property(self):
        self.assertTrue(self.complete_lesson.is_complete)
        self.assertFalse(self.incomplete_lesson.is_complete)


class UnitTests(TestCase):
    def setUp(self) -> None:
        exercise = ExerciseFactory()
        submission = SubmissionFactory()
        submission.exercise = exercise
        submission.save()
        complete_lesson = LessonFactory()
        exercise.lesson = complete_lesson
        exercise.save()

        self.complete_unit = UnitFactory()
        complete_lesson.unit = self.complete_unit
        complete_lesson.save()

        incomplete_lesson = LessonFactory()
        incomplete_exercise = ExerciseFactory()
        incomplete_exercise.lesson = incomplete_lesson
        incomplete_exercise.save()

        self.incomplete_unit = UnitFactory()
        incomplete_lesson.unit = self.incomplete_unit
        incomplete_lesson.save()
        
        return super().setUp()
    
    def test_is_complete_property(self):
        self.assertTrue(self.complete_unit.is_complete)
        self.assertFalse(self.incomplete_unit.is_complete)
