import uuid

from django.db import models


class StudentModuleEnrollment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        'accounts.Student',
        on_delete=models.CASCADE,
        related_name='enrollments',
    )
    module = models.ForeignKey(
        'courses.Module',
        on_delete=models.CASCADE,
        related_name='enrollments',
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    progress_percent = models.IntegerField(default=0)

    class Meta:
        db_table = 'student_module_enrollment'
        unique_together = ['student', 'module']

    def __str__(self):
        return f"{self.student.full_name} - {self.module.title}"


class StudentLessonProgress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        'accounts.Student',
        on_delete=models.CASCADE,
        related_name='lesson_progress',
    )
    lesson = models.ForeignKey(
        'courses.Lesson',
        on_delete=models.CASCADE,
        related_name='student_progress',
    )
    is_unlocked = models.BooleanField(default=False)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    completion_percent = models.IntegerField(default=0)

    class Meta:
        db_table = 'student_lesson_progress'
        unique_together = ['student', 'lesson']

    def __str__(self):
        return f"{self.student.full_name} - {self.lesson.title}"


class AssignmentAttempt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        'accounts.Student',
        on_delete=models.CASCADE,
        related_name='attempts',
    )
    assignment = models.ForeignKey(
        'assignments.Assignment',
        on_delete=models.CASCADE,
        related_name='attempts',
    )
    attempt_number = models.IntegerField(default=1)
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(blank=True, null=True)
    score = models.IntegerField(blank=True, null=True)
    max_score = models.IntegerField()
    percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    is_passed = models.BooleanField(blank=True, null=True)

    class Meta:
        db_table = 'assignment_attempt'
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.student.full_name} - {self.assignment.title} (#{self.attempt_number})"


class QuestionAnswer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attempt = models.ForeignKey(
        AssignmentAttempt,
        on_delete=models.CASCADE,
        related_name='answers',
    )
    question = models.ForeignKey(
        'assignments.Question',
        on_delete=models.CASCADE,
        related_name='answers',
    )
    answer_data = models.JSONField(help_text='Talaba javobi')
    is_correct = models.BooleanField(blank=True, null=True)
    points_earned = models.IntegerField(default=0)
    feedback = models.TextField(blank=True, null=True)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'question_answer'

    def __str__(self):
        return f"Javob - {self.question_id}"
