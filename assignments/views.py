from rest_framework import viewsets

from .models import AssignmentType, Assignment, Question
from .serializers import (
    AssignmentTypeSerializer,
    AssignmentSerializer,
    AssignmentDetailSerializer,
    QuestionSerializer,
)


class AssignmentTypeViewSet(viewsets.ModelViewSet):
    queryset = AssignmentType.objects.all()
    serializer_class = AssignmentTypeSerializer


class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.select_related('assignment_type').prefetch_related('questions').all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AssignmentDetailSerializer
        return AssignmentSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        lesson_id = self.request.query_params.get('lesson_id')
        if lesson_id:
            qs = qs.filter(lesson_id=lesson_id)
        return qs


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.select_related('assignment').all()
    serializer_class = QuestionSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        assignment_id = self.request.query_params.get('assignment_id')
        if assignment_id:
            qs = qs.filter(assignment_id=assignment_id)
        return qs
