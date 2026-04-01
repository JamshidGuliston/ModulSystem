import uuid

from django.db import models


class AssignmentType(models.Model):
    """Topshiriq turi: multiple_choice, text_answer, matching, fill_blank, ordering, true_false, etc."""

    GRADER_TYPES = [
        ('auto',    'Avtomatik'),     # MCQ, matching, true_false
        ('ai',      'AI'),            # essay, short_answer, swot
        ('teacher', "O'qituvchi"),    # file_upload, goal_setting
        ('peer',    'Peer'),          # peer_assessment
        ('self',    "O'zi"),          # self_evaluation
        ('none',    'Baholanmaydi'),  # video_watch, reading
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey(
        'accounts.Teacher',
        on_delete=models.CASCADE,
        related_name='assignment_types',
        null=True,
        blank=True,
        help_text="Bo'sh (null) bo'lsa — barcha o'qituvchilar uchun umumiy",
    )
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255, blank=True, null=True)
    config_schema = models.JSONField(
        blank=True,
        null=True,
        help_text='Topshiriq turi uchun sozlamalar sxemasi (JSON)',
    )
    grader_type = models.CharField(
        max_length=20,
        choices=GRADER_TYPES,
        default='auto',
    )

    class Meta:
        db_table = 'assignment_type'

    def __str__(self):
        teacher_label = f' [{self.teacher.full_name}]' if self.teacher else ' [Global]'
        return f'{self.name}{teacher_label}'


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
    is_randomized = models.BooleanField(
        default=False,
        help_text="True bo'lsa savollar tasodifiy tartibda chiqariladi",
    )
    question_count = models.IntegerField(
        null=True,
        blank=True,
        help_text="Tasodifiy tanlanadigan savollar soni (is_randomized=True bo'lsa)",
    )
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'assignment'
        ordering = ['order_index']

    def __str__(self):
        return self.title


class AssignmentPart(models.Model):
    """Assignment ichidagi qism (Part 1: Listening, Part 2: Reading, ...)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='parts',
    )
    title = models.CharField(max_length=200)
    instructions = models.TextField(blank=True, null=True)
    grading_prompt = models.TextField(
        blank=True, null=True,
        help_text="AI ga yuboriladigan baholash mezoni (Speaking uchun)'",
    )
    max_score = models.IntegerField(
        default=5,
        help_text="Bu part uchun maksimal ball (masalan Part 3 uchun 6)",
    )
    order_index = models.IntegerField(default=0)
    assignment_type = models.ForeignKey(
        AssignmentType,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='parts',
        help_text="Part uchun alohida topshiriq turi (bo'sh bo'lsa — assignment turidan foydalaniladi)",
    )

    class Meta:
        db_table = 'assignment_part'
        ordering = ['order_index']

    def __str__(self):
        return f'{self.assignment.title} — {self.title}'


class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='questions',
    )
    part = models.ForeignKey(
        AssignmentPart,
        on_delete=models.CASCADE,
        related_name='questions',
        null=True,
        blank=True,
        help_text="Qaysi partga tegishli (bo'sh bo'lsa — partlarsiz assignment)",
    )
    question_text = models.TextField()
    question_data = models.JSONField(help_text='Variantlar, juftliklar va h.k.')
    correct_answer = models.JSONField(blank=True, null=True, help_text="To'g'ri javob(lar). AI/teacher grader uchun null bo'lishi mumkin")
    points = models.IntegerField(default=1)
    order_index = models.IntegerField(default=0)
    level = models.ForeignKey(
        'accounts.Level',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='questions',
    )
    explanation = models.TextField(blank=True, null=True, help_text='Javobdan keyin tushuntirish')

    class Meta:
        db_table = 'question'
        ordering = ['order_index']

    def __str__(self):
        return f"Savol #{self.order_index} - {self.assignment.title}"


class DiscussionMessage(models.Model):
    """Discussion/chat topshirig'idagi xabarlar."""

    SENDER_TYPES = [
        ('student', 'Student'),
        ('teacher', "O'qituvchi"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='discussion_messages',
    )
    student = models.ForeignKey(
        'accounts.Student',
        on_delete=models.CASCADE,
        related_name='discussion_messages',
    )
    sender_type = models.CharField(max_length=10, choices=SENDER_TYPES, default='student')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'discussion_message'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender_type} | {self.student.full_name} | {self.created_at:%Y-%m-%d %H:%M}"
