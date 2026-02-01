import uuid

from django.db import models


class AssignmentType(models.Model):
    """Topshiriq turi: multiple_choice, text_answer, matching, fill_blank, ordering, true_false, etc."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255, blank=True, null=True)
    config_schema = models.JSONField(
        blank=True,
        null=True,
        help_text='Topshiriq turi uchun sozlamalar sxemasi',
    )
    is_auto_graded = models.BooleanField(default=True)

    class Meta:
        db_table = 'assignment_type'

    def __str__(self):
        return self.name


class Assignment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson = models.ForeignKey(
        'courses.Lesson',
        on_delete=models.CASCADE,
        related_name='assignments',
    )
    assignment_type = models.ForeignKey(
        AssignmentType,
        on_delete=models.PROTECT,
        related_name='assignments',
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    total_points = models.IntegerField(default=0, help_text='Avtomatik hisoblanadi')
    time_limit = models.IntegerField(blank=True, null=True, help_text='Daqiqalarda')
    attempts_allowed = models.IntegerField(default=1)
    order_index = models.IntegerField(default=0)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'assignment'
        ordering = ['order_index']

    def __str__(self):
        return self.title


class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='questions',
    )
    question_text = models.TextField()
    question_data = models.JSONField(help_text='Variantlar, juftliklar va h.k.')
    correct_answer = models.JSONField(help_text="To'g'ri javob(lar)")
    points = models.IntegerField(default=1)
    order_index = models.IntegerField(default=0)
    explanation = models.TextField(blank=True, null=True, help_text='Javobdan keyin tushuntirish')

    class Meta:
        db_table = 'question'
        ordering = ['order_index']

    def __str__(self):
        return f"Savol #{self.order_index} - {self.assignment.title}"
