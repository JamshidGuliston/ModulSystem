from django.contrib import admin

from .models import Teacher, Student


class StudentInline(admin.TabularInline):
    model = Student
    extra = 0
    fields = ['full_name', 'email', 'is_active', 'created_at']
    readonly_fields = ['created_at']


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'domain', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['full_name', 'email', 'domain']
    readonly_fields = ['id', 'api_token', 'created_at', 'updated_at']
    inlines = [StudentInline]
    fieldsets = (
        (None, {
            'fields': ('id', 'email', 'password', 'full_name'),
        }),
        ("Domain va API Token", {
            'fields': ('domain', 'api_token'),
            'description': (
                "Domain: Teacher frontendining to'liq URL manzili (masalan: https://teacher.example.com). "
                "CORS tekshiruvida foydalaniladi.<br>"
                "API Token: Frontend bu tokenni <code>Authorization: Token &lt;token&gt;</code> "
                "headerida yuborishi kerak."
            ),
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
