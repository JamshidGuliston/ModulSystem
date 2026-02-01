from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ContentTypeViewSet,
    ModuleViewSet,
    LessonViewSet,
    ModuleContentViewSet,
    LessonContentViewSet,
)

router = DefaultRouter()
router.register(r'content-types', ContentTypeViewSet)
router.register(r'modules', ModuleViewSet)
router.register(r'lessons', LessonViewSet)
router.register(r'module-contents', ModuleContentViewSet)
router.register(r'lesson-contents', LessonContentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
