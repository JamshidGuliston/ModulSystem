from django.contrib import admin

from .models import (
    StudentModuleEnrollment,
    StudentLessonProgress,
    AssignmentAttempt,
    QuestionAnswer,
)


@admin.register(StudentModuleEnrollment)
class StudentModuleEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'module', 'progress_percent', 'enrolled_at', 'completed_at']
    list_filter = ['module', 'enrolled_at']
    search_fields = ['student__full_name', 'module__title']
    readonly_fields = ['id', 'enrolled_at']
    list_select_related = ['student', 'module']


@admin.register(StudentLessonProgress)
class StudentLessonProgressAdmin(admin.ModelAdmin):
    list_display = ['student', 'lesson', 'is_unlocked', 'completion_percent', 'started_at', 'completed_at']
    list_filter = ['is_unlocked', 'lesson__module']
    search_fields = ['student__full_name', 'lesson__title']
    readonly_fields = ['id']
    list_select_related = ['student', 'lesson']


class QuestionAnswerInline(admin.TabularInline):
    model = QuestionAnswer
    extra = 0
    fields = ['question', 'is_correct', 'points_earned', 'answered_at']
    readonly_fields = ['answered_at']


@admin.register(AssignmentAttempt)
class AssignmentAttemptAdmin(admin.ModelAdmin):
    list_display = [
        'student', 'assignment', 'attempt_number',
        'score', 'max_score', 'percentage', 'is_passed', 'started_at',
    ]
    list_filter = ['is_passed', 'assignment__lesson__module']
    search_fields = ['student__full_name', 'assignment__title']
    readonly_fields = ['id', 'started_at']
    list_select_related = ['student', 'assignment']
    inlines = [QuestionAnswerInline]


@admin.register(QuestionAnswer)
class QuestionAnswerAdmin(admin.ModelAdmin):
    list_display = ['attempt', 'question', 'is_correct', 'points_earned', 'answered_at']
    list_filter = ['is_correct']
    readonly_fields = ['id', 'answered_at']
    list_select_related = ['attempt', 'question']
