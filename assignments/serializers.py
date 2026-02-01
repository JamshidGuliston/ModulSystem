from rest_framework import serializers

from .models import AssignmentType, Assignment, Question


class AssignmentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentType
        fields = ['id', 'name', 'description', 'config_schema', 'is_auto_graded']
        read_only_fields = ['id']


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            'id', 'assignment', 'question_text', 'question_data',
            'correct_answer', 'points', 'order_index', 'explanation',
        ]
        read_only_fields = ['id']


class QuestionStudentSerializer(serializers.ModelSerializer):
    """Talaba uchun - correct_answer ko'rinmaydi"""
    class Meta:
        model = Question
        fields = [
            'id', 'assignment', 'question_text', 'question_data',
            'points', 'order_index',
        ]
        read_only_fields = ['id']


class AssignmentSerializer(serializers.ModelSerializer):
    assignment_type_name = serializers.CharField(
        source='assignment_type.name', read_only=True,
    )
    questions_count = serializers.IntegerField(source='questions.count', read_only=True)

    class Meta:
        model = Assignment
        fields = [
            'id', 'lesson', 'assignment_type', 'assignment_type_name',
            'title', 'description', 'total_points', 'time_limit',
            'attempts_allowed', 'order_index', 'is_published',
            'questions_count', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AssignmentDetailSerializer(serializers.ModelSerializer):
    """Topshiriq bilan birga savollarni qaytaradi"""
    assignment_type_name = serializers.CharField(
        source='assignment_type.name', read_only=True,
    )
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Assignment
        fields = [
            'id', 'lesson', 'assignment_type', 'assignment_type_name',
            'title', 'description', 'total_points', 'time_limit',
            'attempts_allowed', 'order_index', 'is_published',
            'questions', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
