import os
import uuid as uuid_lib

from django.conf import settings
from rest_framework import viewsets
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from .models import ContentType, Module, Lesson, ModuleContent, LessonContent
from .serializers import (
    ContentTypeSerializer,
    ModuleSerializer,
    ModuleDetailSerializer,
    LessonSerializer,
    LessonDetailSerializer,
    ModuleContentSerializer,
    LessonContentSerializer,
)


@api_view(['POST'])
@parser_classes([MultiPartParser])
def upload_file(request):
    file = request.FILES.get('file')
    if not file:
        return Response({'error': 'Fayl yuklanmadi'}, status=400)

    ext = os.path.splitext(file.name)[1].lower()
    filename = f"{uuid_lib.uuid4()}{ext}"
    upload_dir = settings.MEDIA_ROOT / 'uploads'
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / filename
    with open(file_path, 'wb') as f:
        for chunk in file.chunks():
            f.write(chunk)

    url = request.build_absolute_uri(f"{settings.MEDIA_URL}uploads/{filename}")
    return Response({'url': url, 'name': file.name, 'size': file.size})


class ContentTypeViewSet(viewsets.ModelViewSet):
    queryset = ContentType.objects.all()
    serializer_class = ContentTypeSerializer


class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.select_related('teacher').prefetch_related('lessons').all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ModuleDetailSerializer
        return ModuleSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        # Token orqali kelgan teacher faqat o'z modullarini ko'radi
        if hasattr(self.request, 'teacher') and self.request.teacher:
            qs = qs.filter(teacher=self.request.teacher)
        teacher_id = self.request.query_params.get('teacher_id')
        if teacher_id:
            qs = qs.filter(teacher_id=teacher_id)
        return qs


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.select_related('module', 'parent').prefetch_related('children', 'assignments').all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return LessonDetailSerializer
        return LessonSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        # Teacher faqat o'z modullaridagi darslarni ko'radi
        if hasattr(self.request, 'teacher') and self.request.teacher:
            qs = qs.filter(module__teacher=self.request.teacher)
        module_id = self.request.query_params.get('module_id')
        if module_id:
            qs = qs.filter(module_id=module_id)

        parent_id = self.request.query_params.get('parent_id')
        if parent_id:
            # Berilgan lesson ning child larini (stage larini) qaytaradi
            qs = qs.filter(parent_id=parent_id)
        elif self.request.query_params.get('root') == 'true':
            # Faqat root lessonlarni qaytaradi (parent=None)
            qs = qs.filter(parent__isnull=True)

        return qs


class ModuleContentViewSet(viewsets.ModelViewSet):
    queryset = ModuleContent.objects.select_related('content_type').all()
    serializer_class = ModuleContentSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request, 'teacher') and self.request.teacher:
            qs = qs.filter(module__teacher=self.request.teacher)
        module_id = self.request.query_params.get('module_id')
        if module_id:
            qs = qs.filter(module_id=module_id)
        return qs


class LessonContentViewSet(viewsets.ModelViewSet):
    queryset = LessonContent.objects.select_related('lesson', 'content_type', 'level').all()
    serializer_class = LessonContentSerializer
    pagination_class = None

    def get_queryset(self):
        qs = LessonContent.objects.select_related('lesson', 'content_type', 'level').all()
        if hasattr(self.request, 'teacher') and self.request.teacher:
            qs = qs.filter(lesson__module__teacher=self.request.teacher)
        lesson_id = self.request.query_params.get('lesson_id')
        if lesson_id:
            qs = qs.filter(lesson_id=lesson_id)
        level_id = self.request.query_params.get('level_id')
        if level_id:
            from django.db.models import Q
            qs = qs.filter(Q(level_id=level_id) | Q(level__isnull=True))
        return qs
