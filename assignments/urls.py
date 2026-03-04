from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    AssignmentTypeViewSet,
    AssignmentViewSet,
    QuestionViewSet,
    import_questions_from_docx,
)

router = DefaultRouter()
router.register(r'assignment-types', AssignmentTypeViewSet)
router.register(r'assignments', AssignmentViewSet)
router.register(r'questions', QuestionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('questions/import-docx/', import_questions_from_docx),
]
