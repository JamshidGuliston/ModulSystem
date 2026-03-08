from rest_framework import serializers

from .models import ContentType, Module, Lesson, ModuleContent, LessonContent


class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = ['id', 'name', 'icon', 'description']
        read_only_fields = ['id']


class ModuleSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)
    lessons_count = serializers.IntegerField(source='lessons.count', read_only=True)

    class Meta:
        model = Module
        fields = [
            'id', 'teacher', 'teacher_name', 'title', 'description',
            'thumbnail', 'order_index', 'is_sequential', 'is_published',
            'lessons_count', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LessonSerializer(serializers.ModelSerializer):
    assignments_count = serializers.IntegerField(source='assignments.count', read_only=True)
    children_count = serializers.IntegerField(source='children.count', read_only=True)
    has_children = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            'id', 'module', 'parent',
            'title', 'description', 'order_index',
            'is_sequential', 'required_completion_percent', 'is_published',
            'assignments_count', 'children_count', 'has_children',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_has_children(self, obj):
        return obj.children.exists()


class LessonChildSerializer(serializers.ModelSerializer):
    """Stage (child lesson) uchun — assignments bilan"""
    assignments_count = serializers.IntegerField(source='assignments.count', read_only=True)

    class Meta:
        model = Lesson
        fields = [
            'id', 'parent', 'title', 'description', 'order_index',
            'is_sequential', 'required_completion_percent', 'is_published',
            'assignments_count', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ModuleContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModuleContent
        fields = [
            'id', 'module', 'content_type',
            'title', 'content', 'file_url', 'video_url',
            'order_index', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['content_type'] = ContentTypeSerializer(instance.content_type).data
        return data


class LessonContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonContent
        fields = [
            'id', 'lesson', 'content_type',
            'title', 'content', 'file_url', 'video_url',
            'order_index', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['content_type'] = ContentTypeSerializer(instance.content_type).data
        return data


class ModuleDetailSerializer(serializers.ModelSerializer):
    """Modul bilan birga darslar va kontentlarni qaytaradi"""
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)
    lessons = LessonSerializer(many=True, read_only=True)
    contents = ModuleContentSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = [
            'id', 'teacher', 'teacher_name', 'title', 'description',
            'thumbnail', 'order_index', 'is_sequential', 'is_published',
            'lessons', 'contents', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LessonDetailSerializer(serializers.ModelSerializer):
    """Dars bilan birga kontentlar, child lessonlar (stages) va topshiriqlarni qaytaradi"""
    contents = LessonContentSerializer(many=True, read_only=True)
    children = LessonChildSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = [
            'id', 'module', 'parent',
            'title', 'description', 'order_index',
            'is_sequential', 'required_completion_percent', 'is_published',
            'contents', 'children', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
