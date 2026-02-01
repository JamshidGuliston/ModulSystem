from django.contrib import admin

from .models import Teacher, Student


class StudentInline(admin.TabularInline):
    model = Student
    extra = 0
    fields = ['full_name', 'email', 'is_active', 'created_at']
    readonly_fields = ['created_at']


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['full_name', 'email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [StudentInline]
    fieldsets = (
        (None, {
            'fields': ('id', 'email', 'password', 'full_name'),
        }),
        ("Qo'shimcha", {
            'fields': ('avatar', 'bio', 'settings'),
            'classes': ('collapse',),
        }),
        ('Holati', {
            'fields': ('is_active', 'created_at', 'updated_at'),
        }),
    )


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'teacher', 'is_active', 'created_at']
    list_filter = ['is_active', 'teacher', 'created_at']
    search_fields = ['full_name', 'email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    list_select_related = ['teacher']
