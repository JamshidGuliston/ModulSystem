from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TeacherViewSet, StudentViewSet, LevelViewSet

router = DefaultRouter()
router.register(r'teachers', TeacherViewSet)
router.register(r'students', StudentViewSet)
router.register(r'levels', LevelViewSet, basename='level')

urlpatterns = [
    path('', include(router.urls)),
]
