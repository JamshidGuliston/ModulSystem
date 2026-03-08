from rest_framework import viewsets

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
    queryset = LessonContent.objects.select_related('content_type').all()
    serializer_class = LessonContentSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request, 'teacher') and self.request.teacher:
            qs = qs.filter(lesson__module__teacher=self.request.teacher)
        lesson_id = self.request.query_params.get('lesson_id')
        if lesson_id:
            qs = qs.filter(lesson_id=lesson_id)
        return qs
