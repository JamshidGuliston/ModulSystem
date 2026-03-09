from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    AssignmentTypeViewSet,
    AssignmentViewSet,
    AssignmentPartViewSet,
    QuestionViewSet,
    import_questions_from_docx,
)

router = DefaultRouter()
router.register(r'assignment-types', AssignmentTypeViewSet, basename='assignmenttype')
router.register(r'assignments', AssignmentViewSet)
router.register(r'assignment-parts', AssignmentPartViewSet, basename='assignmentpart')
router.register(r'questions', QuestionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('questions/import-docx/', import_questions_from_docx),
]
