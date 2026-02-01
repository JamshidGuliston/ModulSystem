import uuid

from django.db import models


class ContentType(models.Model):
    """Kontent turi: text, video, book, presentation"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    icon = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'content_type'

    def __str__(self):
        return self.name


class Module(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey(
        'accounts.Teacher',
        on_delete=models.CASCADE,
        related_name='modules',
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    thumbnail = models.CharField(max_length=500, blank=True, null=True)
    order_index = models.IntegerField(default=0)
    is_sequential = models.BooleanField(default=False, help_text='Darslar tartib bilan')
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'module'
        ordering = ['order_index']

    def __str__(self):
        return self.title


class Lesson(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='lessons',
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    order_index = models.IntegerField(default=0)
    is_sequential = models.BooleanField(default=False)
    required_completion_percent = models.IntegerField(
        default=80,
        help_text="Keyingi darsga o'tish uchun talab qilinadigan foiz",
    )
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'lesson'
        ordering = ['order_index']

    def __str__(self):
        return self.title


class ModuleContent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='contents',
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        related_name='module_contents',
    )
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True, help_text='Matn uchun')
    file_url = models.CharField(max_length=500, blank=True, null=True)
    video_url = models.CharField(max_length=500, blank=True, null=True)
    order_index = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'module_content'
        ordering = ['order_index']

    def __str__(self):
        return self.title


class LessonContent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='contents',
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        related_name='lesson_contents',
    )
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)
    file_url = models.CharField(max_length=500, blank=True, null=True)
    video_url = models.CharField(max_length=500, blank=True, null=True)
    order_index = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'lesson_content'
        ordering = ['order_index']

    def __str__(self):
        return self.title
