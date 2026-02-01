import uuid

from django.db import models


class Teacher(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    avatar = models.CharField(max_length=500, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    settings = models.JSONField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'teacher'
        ordering = ['-created_at']

    def __str__(self):
        return self.full_name


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
