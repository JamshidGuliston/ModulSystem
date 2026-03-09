from django.contrib import admin
from django.utils.html import mark_safe

from .models import AssignmentType, Assignment, AssignmentPart, Question

CONFIG_SCHEMA_EXAMPLES = """
<style>
  .schema-hint { background:#f8f9fa; border:1px solid #dee2e6; border-radius:6px;
                 padding:12px; font-size:12px; margin-top:8px; }
  .schema-hint h4 { margin:8px 0 4px; color:#0d6efd; font-size:11px; text-transform:uppercase; letter-spacing:.5px; }
  .schema-hint pre { background:#fff; border:1px solid #e9ecef; border-radius:4px;
                     padding:8px; margin:4px 0 12px; overflow:auto; font-size:11px; white-space:pre-wrap; }
</style>
<div class="schema-hint">
<h4>video_watch</h4>
<pre>{"video_url": {"type": "string"}, "duration_minutes": {"type": "integer"}}</pre>

<h4>reading</h4>
<pre>{"word_count": {"type": "integer"}}</pre>

<h4>multiple_choice</h4>
<pre>{"options_count": {"type": "integer", "min": 2, "max": 6}, "allow_multiple": {"type": "boolean"}}</pre>

<h4>true_false</h4>
<pre>{"show_explanation": {"type": "boolean"}}</pre>

<h4>matching</h4>
<pre>{"pairs_count": {"type": "integer", "min": 2, "max": 10}}</pre>

<h4>fill_blank</h4>
<pre>{"case_sensitive": {"type": "boolean"}, "allow_synonyms": {"type": "boolean"}}</pre>

<h4>ordering</h4>
<pre>{"items_count": {"type": "integer", "min": 2, "max": 8}}</pre>

<h4>short_answer — AI tekshiradi</h4>
<pre>{"max_words": {"type": "integer"}, "language": {"type": "string", "default": "en"}}</pre>

<h4>essay — AI tekshiradi</h4>
<pre>{
  "min_words": {"type": "integer"},
  "max_words": {"type": "integer"},
  "rubric": {
    "content":    {"max_points": 10, "description": "Key ideas covered"},
    "vocabulary": {"max_points": 5,  "description": "Academic vocabulary used"},
    "grammar":    {"max_points": 5,  "description": "Grammar accuracy"}
  }
}</pre>

<h4>swot — AI tekshiradi</h4>
<pre>{"topic": {"type": "string"}, "min_points_each": {"type": "integer", "default": 2}}</pre>

<h4>discussion</h4>
<pre>{"prompt": {"type": "string"}, "min_words": {"type": "integer", "default": 50}}</pre>

<h4>file_upload</h4>
<pre>{"allowed_extensions": ["pdf", "docx", "pptx"], "max_size_mb": {"type": "integer", "default": 10}}</pre>

<h4>goal_setting</h4>
<pre>{"goal_count": {"type": "integer", "default": 4}, "format": "SMART"}</pre>

<h4>self_evaluation</h4>
<pre>{
  "scale": "likert",
  "options": [
    {"value": 1, "label": "Hech qachon"},
    {"value": 2, "label": "Ba'zan"},
    {"value": 3, "label": "Ko'pincha"},
    {"value": 4, "label": "Har doim"}
  ]
}</pre>

<h4>peer_assessment</h4>
<pre>{
  "rubric": {
    "content":      {"max_points": 10},
    "presentation": {"max_points": 5},
    "teamwork":     {"max_points": 5}
  }
}</pre>
</div>
"""


@admin.register(AssignmentType)
class AssignmentTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'teacher', 'grader_type', 'description']
    list_filter = ['grader_type', 'teacher']
    search_fields = ['name', 'teacher__full_name']
    readonly_fields = ['id', 'config_schema_hint']

    fieldsets = (
        (None, {
            'fields': ('id', 'teacher', 'name', 'description', 'grader_type'),
        }),
        ('Config Schema', {
            'fields': ('config_schema', 'config_schema_hint'),
        }),
    )

    @admin.display(description='Har bir tur uchun config_schema misollari')
    def config_schema_hint(self, obj):
        return mark_safe(CONFIG_SCHEMA_EXAMPLES)


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    fields = ['question_text', 'part', 'points', 'order_index']


class AssignmentPartInline(admin.TabularInline):
    model = AssignmentPart
    extra = 0
    fields = ['title', 'order_index', 'assignment_type', 'instructions']
    show_change_link = True


@admin.register(AssignmentPart)
class AssignmentPartAdmin(admin.ModelAdmin):
    list_display = ['title', 'assignment', 'order_index', 'assignment_type', 'questions_count']
    list_filter = ['assignment_type']
    search_fields = ['title', 'assignment__title']
    readonly_fields = ['id']
    list_select_related = ['assignment', 'assignment_type']
    inlines = [QuestionInline]

    @admin.display(description='Savollar soni')
    def questions_count(self, obj):
        return obj.questions.count()


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
    inlines = [AssignmentPartInline, QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['short_text', 'assignment', 'points', 'order_index']
    list_filter = ['assignment__assignment_type', 'assignment']
    search_fields = ['question_text']
    readonly_fields = ['id']
    list_select_related = ['assignment']

    @admin.display(description='Savol matni')
    def short_text(self, obj):
        return obj.question_text[:80] + '...' if len(obj.question_text) > 80 else obj.question_text
