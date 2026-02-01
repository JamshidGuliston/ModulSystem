from rest_framework import viewsets

from .models import (
    StudentModuleEnrollment,
    StudentLessonProgress,
    AssignmentAttempt,
    QuestionAnswer,
)
from .serializers import (
    StudentModuleEnrollmentSerializer,
    StudentLessonProgressSerializer,
    AssignmentAttemptSerializer,
    AssignmentAttemptDetailSerializer,
    QuestionAnswerSerializer,
)


class StudentModuleEnrollmentViewSet(viewsets.ModelViewSet):
    queryset = StudentModuleEnrollment.objects.select_related('student', 'module').all()
    serializer_class = StudentModuleEnrollmentSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        student_id = self.request.query_params.get('student_id')
        module_id = self.request.query_params.get('module_id')
        if student_id:
            qs = qs.filter(student_id=student_id)
        if module_id:
            qs = qs.filter(module_id=module_id)
        return qs


class StudentLessonProgressViewSet(viewsets.ModelViewSet):
    queryset = StudentLessonProgress.objects.select_related('student', 'lesson').all()
    serializer_class = StudentLessonProgressSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        student_id = self.request.query_params.get('student_id')
        lesson_id = self.request.query_params.get('lesson_id')
        if student_id:
            qs = qs.filter(student_id=student_id)
        if lesson_id:
            qs = qs.filter(lesson_id=lesson_id)
        return qs


class AssignmentAttemptViewSet(viewsets.ModelViewSet):
    queryset = AssignmentAttempt.objects.select_related('student', 'assignment').all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AssignmentAttemptDetailSerializer
        return AssignmentAttemptSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        student_id = self.request.query_params.get('student_id')
        assignment_id = self.request.query_params.get('assignment_id')
        if student_id:
            qs = qs.filter(student_id=student_id)
        if assignment_id:
            qs = qs.filter(assignment_id=assignment_id)
        return qs


class QuestionAnswerViewSet(viewsets.ModelViewSet):
    queryset = QuestionAnswer.objects.select_related('attempt', 'question').all()
    serializer_class = QuestionAnswerSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        attempt_id = self.request.query_params.get('attempt_id')
        if attempt_id:
            qs = qs.filter(attempt_id=attempt_id)
        return qs
