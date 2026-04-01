from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Teacher, Student, Level
from .serializers import (
    TeacherSerializer,
    TeacherCreateSerializer,
    StudentSerializer,
    StudentCreateSerializer,
    StudentUpdateSerializer,
    LevelSerializer,
)


class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()

    def get_queryset(self):
        # Teacher faqat o'zining ma'lumotlarini ko'ra oladi
        if hasattr(self.request, 'teacher') and self.request.teacher:
            return Teacher.objects.filter(pk=self.request.teacher.pk)
        return Teacher.objects.none()

    def get_serializer_class(self):
        if self.action == 'create':
            return TeacherCreateSerializer
        return TeacherSerializer

    @action(detail=False, methods=['post'], permission_classes=[AllowAny],
            authentication_classes=[])
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
        data = serializer.data
        # Token ni responsega qo'shish — faqat login vaqtida
        data['api_token'] = teacher.api_token
        return Response(data)

    @action(detail=False, methods=['post'])
    def regenerate_token(self, request):
        """Teacher tokenni qayta yaratish. Eski token ishlamay qoladi."""
        teacher = request.teacher
        new_token = teacher.regenerate_token()
        return Response({
            'detail': 'Token muvaffaqiyatli yangilandi.',
            'api_token': new_token,
        })

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Joriy teacher ma'lumotlarini qaytaradi (token orqali)."""
        serializer = TeacherSerializer(request.teacher)
        return Response(serializer.data)


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.select_related('teacher', 'level').all()

    def get_serializer_class(self):
        if self.action == 'create':
            return StudentCreateSerializer
        if self.action in ('update', 'partial_update'):
            return StudentUpdateSerializer
        return StudentSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        # Token orqali kelgan teacher faqat o'z studentlarini ko'radi
        if hasattr(self.request, 'teacher') and self.request.teacher:
            qs = qs.filter(teacher=self.request.teacher)
        teacher_id = self.request.query_params.get('teacher_id')
        if teacher_id:
            qs = qs.filter(teacher_id=teacher_id)
        return qs

    def _respond_with_student_serializer(self, instance):
        """update/partial_update dan keyin to'liq nested response qaytaradi."""
        serializer = StudentSerializer(instance, context=self.get_serializer_context())
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return self._respond_with_student_serializer(instance)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny],
            authentication_classes=[])
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        teacher_id = request.data.get('teacher_id')

        if not email or not password:
            return Response(
                {'detail': 'Email va parol kiritilishi shart'},
                status=status.HTTP_400_BAD_REQUEST
            )

        filters = {
            'email': email,
            'password': password,
            'is_active': True,
        }
        if teacher_id:
            filters['teacher_id'] = teacher_id

        try:
            student = Student.objects.select_related('teacher').get(**filters)
        except Student.DoesNotExist:
            return Response(
                {'detail': 'Email yoki parol noto\'g\'ri'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Student.MultipleObjectsReturned:
            return Response(
                {'detail': 'teacher_id ni ham yuboring.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = StudentSerializer(student)
        data = serializer.data
        # Student login bo'lganda teacher tokenini qaytarish
        # (frontend bu tokenni keyingi so'rovlarda ishlatadi)
        data['api_token'] = student.teacher.api_token
        return Response(data)


class LevelViewSet(viewsets.ModelViewSet):
    serializer_class = LevelSerializer
    pagination_class = None

    def get_queryset(self):
        if hasattr(self.request, 'teacher') and self.request.teacher:
            return Level.objects.filter(teacher=self.request.teacher)
        return Level.objects.none()

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.teacher)
