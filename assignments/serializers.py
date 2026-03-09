from rest_framework import serializers

from .models import AssignmentType, Assignment, AssignmentPart, Question


class AssignmentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentType
        fields = ['id', 'teacher', 'name', 'description', 'config_schema', 'grader_type']
        read_only_fields = ['id']


class AssignmentPartSerializer(serializers.ModelSerializer):
    questions_count = serializers.IntegerField(source='questions.count', read_only=True)

    class Meta:
        model = AssignmentPart
        fields = [
            'id', 'assignment', 'title', 'instructions',
            'order_index', 'assignment_type', 'questions_count',
        ]
        read_only_fields = ['id']


class AssignmentPartDetailSerializer(serializers.ModelSerializer):
    """Part bilan birga savollarini qaytaradi"""
    questions = serializers.SerializerMethodField()
    assignment_type_detail = serializers.SerializerMethodField()

    class Meta:
        model = AssignmentPart
        fields = [
            'id', 'assignment', 'title', 'instructions',
            'order_index', 'assignment_type', 'assignment_type_detail', 'questions',
        ]
        read_only_fields = ['id']

    def get_questions(self, obj):
        return QuestionSerializer(obj.questions.all(), many=True).data

    def get_assignment_type_detail(self, obj):
        if obj.assignment_type:
            return AssignmentTypeSerializer(obj.assignment_type).data
        return None


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            'id', 'assignment', 'part', 'question_text', 'question_data',
            'correct_answer', 'points', 'order_index', 'explanation',
        ]
        read_only_fields = ['id']


class QuestionStudentSerializer(serializers.ModelSerializer):
    """Talaba uchun - correct_answer ko'rinmaydi"""
    class Meta:
        model = Question
        fields = [
            'id', 'assignment', 'part', 'question_text', 'question_data',
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
    """Topshiriq bilan birga part va savollarni qaytaradi"""
    parts = AssignmentPartDetailSerializer(many=True, read_only=True)
    # Partsiz savollar (part=null bo'lganlar)
    questions = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = [
            'id', 'lesson', 'assignment_type',
            'title', 'description', 'total_points', 'time_limit',
            'attempts_allowed', 'order_index', 'is_published',
            'parts', 'questions', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_questions(self, obj):
        """Faqat partga biriktirilmagan savollar"""
        qs = obj.questions.filter(part__isnull=True)
        return QuestionSerializer(qs, many=True).data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['assignment_type'] = AssignmentTypeSerializer(instance.assignment_type).data
        return data
