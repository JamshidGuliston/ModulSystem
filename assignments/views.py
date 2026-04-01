from rest_framework import viewsets, status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from .models import AssignmentType, Assignment, AssignmentPart, Question, DiscussionMessage
from .serializers import (
    AssignmentTypeSerializer,
    AssignmentSerializer,
    AssignmentDetailSerializer,
    AssignmentPartSerializer,
    AssignmentPartDetailSerializer,
    QuestionSerializer,
    DiscussionMessageSerializer,
)
from .docx_parser import parse_docx


class AssignmentTypeViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentTypeSerializer

    def get_queryset(self):
        if hasattr(self.request, 'teacher') and self.request.teacher:
            return AssignmentType.objects.filter(
                teacher=self.request.teacher
            ).select_related('teacher')
        return AssignmentType.objects.all().select_related('teacher')


class AssignmentPartViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentPartSerializer

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AssignmentPartDetailSerializer
        return AssignmentPartSerializer

    def get_queryset(self):
        qs = AssignmentPart.objects.select_related('assignment', 'assignment_type').all()
        if hasattr(self.request, 'teacher') and self.request.teacher:
            qs = qs.filter(assignment__lesson__module__teacher=self.request.teacher)
        assignment_id = self.request.query_params.get('assignment_id')
        if assignment_id:
            qs = qs.filter(assignment_id=assignment_id)
        return qs


class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.select_related('assignment_type').prefetch_related('parts', 'questions').all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AssignmentDetailSerializer
        return AssignmentSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        # Teacher faqat o'z darslaridagi topshiriqlarni ko'radi
        if hasattr(self.request, 'teacher') and self.request.teacher:
            qs = qs.filter(lesson__module__teacher=self.request.teacher)
        lesson_id = self.request.query_params.get('lesson_id')
        if lesson_id:
            qs = qs.filter(lesson_id=lesson_id)
        return qs


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.select_related('assignment', 'level').all()
    serializer_class = QuestionSerializer
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request, 'teacher') and self.request.teacher:
            qs = qs.filter(assignment__lesson__module__teacher=self.request.teacher)
        assignment_id = self.request.query_params.get('assignment_id')
        if assignment_id:
            qs = qs.filter(assignment_id=assignment_id)
        level_id = self.request.query_params.get('level_id')
        if level_id:
            from django.db.models import Q
            qs = qs.filter(Q(level_id=level_id) | Q(level__isnull=True))
        randomize = self.request.query_params.get('randomize')
        if randomize == 'true':
            if not assignment_id:
                return qs.none()
            try:
                asgn = Assignment.objects.get(pk=assignment_id)
                if asgn.is_randomized and asgn.question_count:
                    import random
                    pks = list(qs.values_list('pk', flat=True))
                    selected = random.sample(pks, min(asgn.question_count, len(pks)))
                    qs = qs.filter(pk__in=selected)
            except Assignment.DoesNotExist:
                pass
        return qs


class DiscussionMessageViewSet(viewsets.ModelViewSet):
    """
    GET  /api/discussion-messages/?question_id=<uuid>  — xabarlar ro'yxati
    POST /api/discussion-messages/                      — xabar yuborish
    """
    serializer_class = DiscussionMessageSerializer
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        qs = DiscussionMessage.objects.select_related('student').all()
        # Teacher scope: faqat o'z studentlarining xabarlarini ko'radi
        if hasattr(self.request, 'teacher') and self.request.teacher:
            qs = qs.filter(question__assignment__lesson__module__teacher=self.request.teacher)
        question_id = self.request.query_params.get('question_id')
        if question_id:
            qs = qs.filter(question_id=question_id)
        student_id = self.request.query_params.get('student_id')
        if student_id:
            qs = qs.filter(student_id=student_id)
        return qs


@api_view(['POST'])
@parser_classes([MultiPartParser])
def import_questions_from_docx(request):
    """
    POST /api/questions/import-docx/
    Body (multipart/form-data):
      file          — .docx fayl
      assignment_id — Assignment UUID
    """
    file_obj      = request.FILES.get('file')
    assignment_id = request.data.get('assignment_id', '').strip()

    # --- validatsiya ---
    if not file_obj:
        return Response({'detail': 'file maydoni kerak.'}, status=400)
    if not file_obj.name.lower().endswith('.docx'):
        return Response({'detail': 'Faqat .docx format qabul qilinadi.'}, status=400)
    if not assignment_id:
        return Response({'detail': 'assignment_id maydoni kerak.'}, status=400)

    try:
        assignment = Assignment.objects.get(pk=assignment_id)
    except Assignment.DoesNotExist:
        return Response({'detail': 'Assignment topilmadi.'}, status=404)

    # Teacher scope tekshiruvi
    if hasattr(request, 'teacher') and request.teacher:
        if assignment.lesson.module.teacher_id != request.teacher.pk:
            return Response({'detail': 'Bu assignment sizga tegishli emas.'}, status=403)

    # --- parse ---
    try:
        questions, errors = parse_docx(file_obj)
    except Exception as exc:
        return Response({'detail': f'Faylni o\'qishda xatolik: {exc}'}, status=400)

    # --- savollarni bazaga yozish ---
    # Mavjud tartib raqamidan davom ettirish
    existing_count = Question.objects.filter(assignment=assignment).count()

    created = []
    for q in questions:
        q['order_index'] += existing_count
        obj = Question.objects.create(
            assignment=assignment,
            question_text=q['question_text'],
            question_data=q['question_data'],
            correct_answer=q['correct_answer'],
            points=q['points'],
            order_index=q['order_index'],
            explanation=q.get('explanation', ''),
        )
        created.append(QuestionSerializer(obj).data)

    return Response({
        'imported': len(created),
        'errors':   errors,
        'questions': created,
    }, status=status.HTTP_201_CREATED)
