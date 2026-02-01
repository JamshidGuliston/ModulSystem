from django.contrib import admin

from .models import ContentType, Module, Lesson, ModuleContent, LessonContent


@admin.register(ContentType)
class ContentTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'description']
    search_fields = ['name']


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ['title', 'order_index', 'is_sequential', 'required_completion_percent', 'is_published']


class ModuleContentInline(admin.TabularInline):
    model = ModuleContent
    extra = 0
    fields = ['title', 'content_type', 'order_index']


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'teacher', 'order_index', 'is_sequential', 'is_published', 'created_at']
    list_filter = ['is_published', 'is_sequential', 'teacher']
    search_fields = ['title', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    list_select_related = ['teacher']
    list_editable = ['order_index', 'is_published']
    inlines = [LessonInline, ModuleContentInline]


class LessonContentInline(admin.TabularInline):
    model = LessonContent
    extra = 0
    fields = ['title', 'content_type', 'order_index']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'module', 'order_index', 'is_sequential',
        'required_completion_percent', 'is_published',
    ]
    list_filter = ['is_published', 'is_sequential', 'module']
    search_fields = ['title', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    list_select_related = ['module']
    list_editable = ['order_index', 'is_published']
    inlines = [LessonContentInline]


@admin.register(ModuleContent)
class ModuleContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'content_type', 'order_index', 'created_at']
    list_filter = ['content_type', 'module']
    search_fields = ['title']
    readonly_fields = ['id', 'created_at']
    list_select_related = ['module', 'content_type']


@admin.register(LessonContent)
class LessonContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson', 'content_type', 'order_index', 'created_at']
    list_filter = ['content_type', 'lesson']
    search_fields = ['title']
    readonly_fields = ['id', 'created_at']
    list_select_related = ['lesson', 'content_type']
