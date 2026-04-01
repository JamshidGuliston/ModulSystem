import secrets
import uuid

from django.db import models


def generate_api_token():
    """64 belgili xavfsiz API token yaratadi."""
    return secrets.token_hex(32)


class Teacher(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    avatar = models.CharField(max_length=500, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    settings = models.JSONField(blank=True, null=True)
    domain = models.CharField(max_length=255, blank=True, null=True, unique=True,
                              help_text="Teacher saytining domeni, masalan: https://teacher.example.com")
    api_token = models.CharField(
        max_length=64, unique=True, default=generate_api_token,
        help_text="API ga kirish uchun token. Frontend bu tokenni Authorization headerda yuboradi."
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'teacher'
        ordering = ['-created_at']

    def __str__(self):
        return self.full_name

    def regenerate_token(self):
        """Tokenni qayta yaratadi va saqlaydi."""
        self.api_token = generate_api_token()
        self.save(update_fields=['api_token'])
        return self.api_token


class Level(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name='levels',
    )
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    order_index = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'level'
        ordering = ['order_index']
        unique_together = [('teacher', 'name')]

    def __str__(self):
        return self.name


class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name='students',
    )
    email = models.EmailField(max_length=255)
    password = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    avatar = models.CharField(max_length=500, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'student'
        ordering = ['-created_at']

    def __str__(self):
        return self.full_name
