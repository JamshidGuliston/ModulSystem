from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    StudentModuleEnrollmentViewSet,
    StudentLessonProgressViewSet,
    AssignmentAttemptViewSet,
    QuestionAnswerViewSet,
    StudentSessionLogViewSet,
)

router = DefaultRouter()
router.register(r'enrollments', StudentModuleEnrollmentViewSet)
router.register(r'lesson-progress', StudentLessonProgressViewSet)
router.register(r'attempts', AssignmentAttemptViewSet)
router.register(r'answers', QuestionAnswerViewSet)
router.register(r'session-logs', StudentSessionLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
