from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (
    StudentModuleEnrollment,
    StudentLessonProgress,
    AssignmentAttempt,
    QuestionAnswer,
)
from .serializers import (
    StudentModuleEnrollmentSerializer,
    StudentLessonProgressSerializer,
    AssignmentAttemptSerializer,
    AssignmentAttemptDetailSerializer,
    QuestionAnswerSerializer,
)


def _auto_grade(question, answer_data):
    grader_type = question.assignment.assignment_type.grader_type
    if grader_type != 'auto':
        return None, 0

    correct = question.correct_answer
    qtype = question.assignment.assignment_type.name

    if qtype == 'multiple_choice':
        is_correct = answer_data.get('selected') == correct

    elif qtype == 'true_false':
        is_correct = bool(answer_data.get('selected')) == bool(correct)

    elif qtype == 'matching':
        student_answer = answer_data.get('selected')
        if isinstance(correct, list):
            is_correct = student_answer in correct
        else:
            is_correct = str(student_answer or '').strip().lower() == str(correct or '').strip().lower()
        return is_correct, question.points if is_correct else 0

    elif qtype == 'fill_blank':
        student_answers = answer_data.get('answers', [])
        if isinstance(correct, list):
            is_correct = (
                len(student_answers) == len(correct) and
                all(
                    str(s).strip().lower() == str(c).strip().lower()
                    for s, c in zip(student_answers, correct)
                )
            )
        else:
            first = str(student_answers[0]).strip().lower() if student_answers else ''
            is_correct = first == str(correct).strip().lower()

    else:
        return None, 0

    points_earned = question.points if is_correct else 0
    return is_correct, points_earned


def _update_lesson_progress(attempt):
    """Attempt submit bo'lgandan keyin lesson va module progressni yangilaydi."""
    try:
        from assignments.models import Assignment as Asgn
        from courses.models import Lesson

        lesson = attempt.assignment.lesson
        if not lesson:
            return

        total = Asgn.objects.filter(lesson=lesson, is_published=True).count()
        if total == 0:
            return

        completed = AssignmentAttempt.objects.filter(
            student=attempt.student,
            assignment__lesson=lesson,
            submitted_at__isnull=False,
        ).values('assignment').distinct().count()

        completion_pct = round(completed / total * 100)

        lp, _ = StudentLessonProgress.objects.get_or_create(
            student=attempt.student,
            lesson=lesson,
            defaults={'is_unlocked': True, 'started_at': timezone.now()}
        )
        lp.completion_percent = completion_pct
        lp.is_unlocked = True
        if completion_pct >= 100 and not lp.completed_at:
            lp.completed_at = timezone.now()
        lp.save(update_fields=['completion_percent', 'is_unlocked', 'completed_at'])

        # Module enrollment progressni yangilash
        module = lesson.module
        if not module:
            return

        total_lessons = Lesson.objects.filter(
            module=module, is_published=True, parent__isnull=True
        ).count()
        if total_lessons == 0:
            return

        done_lessons = StudentLessonProgress.objects.filter(
            student=attempt.student,
            lesson__module=module,
            completion_percent=100,
        ).count()

        mod_pct = round(done_lessons / total_lessons * 100)
        StudentModuleEnrollment.objects.filter(
            student=attempt.student, module=module
        ).update(progress_percent=mod_pct)
    except Exception:
        pass  # progress update failure shouldn't break submission


class StudentModuleEnrollmentViewSet(viewsets.ModelViewSet):
    queryset = StudentModuleEnrollment.objects.select_related('student', 'module').all()
    serializer_class = StudentModuleEnrollmentSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request, 'teacher') and self.request.teacher:
            qs = qs.filter(student__teacher=self.request.teacher)
        student_id = self.request.query_params.get('student_id')
        module_id = self.request.query_params.get('module_id')
        if student_id:
            qs = qs.filter(student_id=student_id)
        if module_id:
            qs = qs.filter(module_id=module_id)
        return qs


class StudentLessonProgressViewSet(viewsets.ModelViewSet):
    queryset = StudentLessonProgress.objects.select_related('student', 'lesson').all()
    serializer_class = StudentLessonProgressSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request, 'teacher') and self.request.teacher:
            qs = qs.filter(student__teacher=self.request.teacher)
        student_id = self.request.query_params.get('student_id')
        lesson_id = self.request.query_params.get('lesson_id')
        if student_id:
            qs = qs.filter(student_id=student_id)
        if lesson_id:
            qs = qs.filter(lesson_id=lesson_id)
        return qs


class AssignmentAttemptViewSet(viewsets.ModelViewSet):
    queryset = AssignmentAttempt.objects.select_related('student', 'assignment').prefetch_related(
        'assignment__parts__questions', 'assignment__questions'
    ).all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AssignmentAttemptDetailSerializer
        return AssignmentAttemptSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request, 'teacher') and self.request.teacher:
            qs = qs.filter(student__teacher=self.request.teacher)
        student_id = self.request.query_params.get('student_id')
        assignment_id = self.request.query_params.get('assignment_id')
        if student_id:
            qs = qs.filter(student_id=student_id)
        if assignment_id:
            qs = qs.filter(assignment_id=assignment_id)
        return qs

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        attempt = self.get_object()
        if attempt.submitted_at:
            return Response({'detail': 'Bu attempt allaqachon yuborilgan.'}, status=400)

        answers = attempt.answers.select_related('question').all()
        total_earned = sum(a.points_earned or 0 for a in answers)
        max_score = attempt.max_score or 1
        percentage = round(total_earned / max_score * 100, 2)

        attempt.score = total_earned
        attempt.percentage = percentage
        attempt.submitted_at = timezone.now()
        attempt.is_passed = percentage >= 60
        attempt.save(update_fields=['score', 'percentage', 'submitted_at', 'is_passed'])

        # Lesson va module progressni yangilash
        _update_lesson_progress(attempt)

        return Response(AssignmentAttemptSerializer(attempt).data)


class QuestionAnswerViewSet(viewsets.ModelViewSet):
    queryset = QuestionAnswer.objects.select_related(
        'attempt', 'question__assignment__assignment_type'
    ).all()
    serializer_class = QuestionAnswerSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request, 'teacher') and self.request.teacher:
            qs = qs.filter(attempt__student__teacher=self.request.teacher)
        attempt_id = self.request.query_params.get('attempt_id')
        if attempt_id:
            qs = qs.filter(attempt_id=attempt_id)
        return qs

    def create(self, request, *args, **kwargs):
        """Upsert: bir xil attempt+question bo'lsa update, aks holda create."""
        attempt_id = request.data.get('attempt')
        question_id = request.data.get('question')
        answer_data = request.data.get('answer_data', {})

        try:
            existing = QuestionAnswer.objects.select_related(
                'question__assignment__assignment_type'
            ).get(attempt_id=attempt_id, question_id=question_id)
            existing.answer_data = answer_data
            fields_to_update = ['answer_data']

            # AI grading fields — only update when explicitly sent
            ai_fields = ['is_correct', 'points_earned', 'feedback', 'score_breakdown']
            ai_data_provided = any(f in request.data for f in ai_fields)
            if ai_data_provided:
                for field in ai_fields:
                    if field in request.data:
                        setattr(existing, field, request.data[field])
                        fields_to_update.append(field)
            else:
                # Auto-grade only when AI hasn't already graded
                is_correct, points_earned = _auto_grade(existing.question, answer_data)
                if is_correct is not None:
                    existing.is_correct = is_correct
                    existing.points_earned = points_earned
                    fields_to_update += ['is_correct', 'points_earned']

            existing.save(update_fields=fields_to_update)
            return Response(self.get_serializer(existing).data, status=status.HTTP_200_OK)
        except QuestionAnswer.DoesNotExist:
            pass

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        instance = serializer.save()
        question = instance.question
        is_correct, points_earned = _auto_grade(question, instance.answer_data)
        if is_correct is not None:
            instance.is_correct = is_correct
            instance.points_earned = points_earned
            instance.save(update_fields=['is_correct', 'points_earned'])
