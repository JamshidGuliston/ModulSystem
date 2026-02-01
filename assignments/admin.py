from django.contrib import admin

from .models import AssignmentType, Assignment, Question


@admin.register(AssignmentType)
class AssignmentTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_auto_graded', 'description']
    search_fields = ['name']


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    fields = ['question_text', 'points', 'order_index']


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'lesson', 'assignment_type', 'total_points',
        'time_limit', 'attempts_allowed', 'is_published',
    ]
    list_filter = ['is_published', 'assignment_type', 'lesson__module']
    search_fields = ['title', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    list_select_related = ['lesson', 'assignment_type']
    list_editable = ['is_published']
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['short_text', 'assignment', 'points', 'order_index']
    list_filter = ['assignment__assignment_type', 'assignment']
    search_fields = ['question_text']
    readonly_fields = ['id']
    list_select_related = ['assignment']

    @admin.display(description="Savol matni")
    def short_text(self, obj):
        return obj.question_text[:80] + '...' if len(obj.question_text) > 80 else obj.question_text
