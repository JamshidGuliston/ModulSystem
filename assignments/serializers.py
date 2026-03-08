from rest_framework import serializers

from .models import AssignmentType, Assignment, Question


class AssignmentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentType
        fields = ['id', 'name', 'description', 'config_schema', 'grader_type']
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
    questions_count = serializers.IntegerField(source='questions.count', read_only=True)

    class Meta:
        model = Assignment
        fields = [
            'id', 'lesson', 'assignment_type',
            'title', 'description', 'total_points', 'time_limit',
            'attempts_allowed', 'order_index', 'is_published',
            'questions_count', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['assignment_type'] = AssignmentTypeSerializer(instance.assignment_type).data
        return data


class AssignmentDetailSerializer(serializers.ModelSerializer):
    """Topshiriq bilan birga savollarni qaytaradi"""
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Assignment
        fields = [
            'id', 'lesson', 'assignment_type',
            'title', 'description', 'total_points', 'time_limit',
            'attempts_allowed', 'order_index', 'is_published',
            'questions', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['assignment_type'] = AssignmentTypeSerializer(instance.assignment_type).data
        return data
