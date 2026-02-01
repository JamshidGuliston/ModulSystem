from rest_framework import serializers

from .models import (
    StudentModuleEnrollment,
    StudentLessonProgress,
    AssignmentAttempt,
    QuestionAnswer,
)


class StudentModuleEnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    module_title = serializers.CharField(source='module.title', read_only=True)

    class Meta:
        model = StudentModuleEnrollment
        fields = [
            'id', 'student', 'student_name', 'module', 'module_title',
            'enrolled_at', 'completed_at', 'progress_percent',
        ]
        read_only_fields = ['id', 'enrolled_at']


class StudentLessonProgressSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)

    class Meta:
        model = StudentLessonProgress
        fields = [
            'id', 'student', 'student_name', 'lesson', 'lesson_title',
            'is_unlocked', 'started_at', 'completed_at', 'completion_percent',
        ]
        read_only_fields = ['id']


class QuestionAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionAnswer
        fields = [
            'id', 'attempt', 'question', 'answer_data',
            'is_correct', 'points_earned', 'feedback', 'answered_at',
        ]
        read_only_fields = ['id', 'answered_at']


class AssignmentAttemptSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)

    class Meta:
        model = AssignmentAttempt
        fields = [
            'id', 'student', 'student_name', 'assignment', 'assignment_title',
            'attempt_number', 'started_at', 'submitted_at',
            'score', 'max_score', 'percentage', 'is_passed',
        ]
        read_only_fields = ['id', 'started_at']


class AssignmentAttemptDetailSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    answers = QuestionAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = AssignmentAttempt
        fields = [
            'id', 'student', 'student_name', 'assignment', 'assignment_title',
            'attempt_number', 'started_at', 'submitted_at',
            'score', 'max_score', 'percentage', 'is_passed', 'answers',
        ]
        read_only_fields = ['id', 'started_at']
