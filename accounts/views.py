from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

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

    @action(detail=False, methods=['post'])
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {'detail': 'Email va parol kiritilishi shart'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            teacher = Teacher.objects.get(
                email=email, password=password, is_active=True
            )
        except Teacher.DoesNotExist:
            return Response(
                {'detail': 'Email yoki parol noto\'g\'ri'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = TeacherSerializer(teacher)
        return Response(serializer.data)


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

    @action(detail=False, methods=['post'])
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {'detail': 'Email va parol kiritilishi shart'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            student = Student.objects.select_related('teacher').get(
                email=email, password=password, is_active=True
            )
        except Student.DoesNotExist:
            return Response(
                {'detail': 'Email yoki parol noto\'g\'ri'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = StudentSerializer(student)
        return Response(serializer.data)
