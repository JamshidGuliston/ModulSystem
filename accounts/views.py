from rest_framework import viewsets

from .models import Teacher, Student
from .serializers import (
    TeacherSerializer,
    TeacherCreateSerializer,
    StudentSerializer,
    StudentCreateSerializer,
)


class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return TeacherCreateSerializer
        return TeacherSerializer


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.select_related('teacher').all()

    def get_serializer_class(self):
        if self.action == 'create':
            return StudentCreateSerializer
        return StudentSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        teacher_id = self.request.query_params.get('teacher_id')
        if teacher_id:
            qs = qs.filter(teacher_id=teacher_id)
        return qs
