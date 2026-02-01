from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path('api/', include('courses.urls')),
    path('api/', include('assignments.urls')),
    path('api/', include('progress.urls')),
]
