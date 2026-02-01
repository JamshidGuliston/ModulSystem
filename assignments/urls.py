from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AssignmentTypeViewSet, AssignmentViewSet, QuestionViewSet

router = DefaultRouter()
router.register(r'assignment-types', AssignmentTypeViewSet)
router.register(r'assignments', AssignmentViewSet)
router.register(r'questions', QuestionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
