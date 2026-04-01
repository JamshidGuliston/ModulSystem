from rest_framework import serializers

from .models import Teacher, Student, Level


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ['id', 'teacher', 'name', 'description', 'order_index', 'created_at']
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'teacher': {'required': False},
        }

    def get_validators(self):
        # UniqueTogetherValidator for (teacher, name) requires teacher in the
        # request body, but teacher is injected by perform_create.  Drop the
        # auto-generated unique-together validators here; the DB constraint
        # still enforces uniqueness.
        return []


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = [
            'id', 'email', 'full_name', 'avatar', 'bio',
            'settings', 'domain', 'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TeacherCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = [
            'id', 'email', 'password', 'full_name', 'avatar', 'bio', 'settings', 'domain',
        ]
        read_only_fields = ['id']
        extra_kwargs = {
            'password': {'write_only': True},
        }


class StudentSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)

    class Meta:
        model = Student
        fields = [
            'id', 'teacher', 'teacher_name', 'email', 'full_name',
            'avatar', 'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StudentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            'id', 'teacher', 'email', 'password', 'full_name', 'avatar',
        ]
        read_only_fields = ['id']
        extra_kwargs = {
            'password': {'write_only': True},
        }
