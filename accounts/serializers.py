from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import Teacher, Student, Level


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ['id', 'teacher', 'name', 'description', 'order_index', 'created_at']
        read_only_fields = ['id', 'teacher', 'created_at']

    def get_validators(self):
        return [
            v for v in super().get_validators()
            if not isinstance(v, UniqueTogetherValidator)
        ]

    def validate(self, attrs):
        request = self.context.get('request')
        if request and hasattr(request, 'teacher') and request.teacher:
            teacher = request.teacher
            name = attrs.get('name', getattr(self.instance, 'name', None))
            qs = Level.objects.filter(teacher=teacher, name=name)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({'name': 'Bu daraja nomi allaqachon mavjud.'})
        return attrs


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
