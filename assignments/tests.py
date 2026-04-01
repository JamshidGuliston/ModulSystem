from django.test import TestCase
from rest_framework.test import APIClient
from accounts.models import Teacher, Level
from courses.models import Module, Lesson
from .models import AssignmentType, Assignment, Question


def make_teacher():
    return Teacher.objects.create(email='t@test.com', password='pass', full_name='T')


def make_structure(teacher):
    module = Module.objects.create(teacher=teacher, title='M', order_index=0)
    lesson = Lesson.objects.create(module=module, title='L', order_index=0)
    atype, _ = AssignmentType.objects.get_or_create(
        name='multiple_choice',
        defaults={'grader_type': 'auto'},
    )
    assignment = Assignment.objects.create(
        lesson=lesson, assignment_type=atype,
        title='A', order_index=0,
    )
    return module, lesson, assignment


class QuestionLevelTest(TestCase):
    def setUp(self):
        self.teacher = make_teacher()
        self.level_b1 = Level.objects.create(teacher=self.teacher, name='B1')
        _, _, self.assignment = make_structure(self.teacher)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.teacher.api_token}')

    def test_question_has_level_field(self):
        q = Question.objects.create(
            assignment=self.assignment,
            question_text='Test?',
            question_data={'options': ['A', 'B']},
            correct_answer='A',
            points=1,
            order_index=0,
            level=self.level_b1,
        )
        self.assertEqual(q.level, self.level_b1)

    def test_question_level_null_by_default(self):
        q = Question.objects.create(
            assignment=self.assignment,
            question_text='Old?',
            question_data={'options': ['A', 'B']},
            correct_answer='A',
            points=1,
            order_index=0,
        )
        self.assertIsNone(q.level)

    def test_filter_questions_by_level_id(self):
        q_b1 = Question.objects.create(
            assignment=self.assignment,
            question_text='B1?', question_data={}, correct_answer='A',
            points=1, order_index=0, level=self.level_b1,
        )
        q_all = Question.objects.create(
            assignment=self.assignment,
            question_text='All?', question_data={}, correct_answer='A',
            points=1, order_index=1, level=None,
        )
        resp = self.client.get(
            f'/api/questions/?assignment_id={self.assignment.id}&level_id={self.level_b1.id}'
        )
        self.assertEqual(resp.status_code, 200)
        ids = [item['id'] for item in resp.data]
        self.assertIn(str(q_b1.id), ids)
        self.assertIn(str(q_all.id), ids)

    def test_no_level_filter_returns_all(self):
        Question.objects.create(
            assignment=self.assignment,
            question_text='B1?', question_data={}, correct_answer='A',
            points=1, order_index=0, level=self.level_b1,
        )
        Question.objects.create(
            assignment=self.assignment,
            question_text='All?', question_data={}, correct_answer='A',
            points=1, order_index=1, level=None,
        )
        resp = self.client.get(f'/api/questions/?assignment_id={self.assignment.id}')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 2)


class AssignmentRandomizationTest(TestCase):
    def setUp(self):
        self.teacher = make_teacher()
        _, _, self.assignment = make_structure(self.teacher)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.teacher.api_token}')

        for i in range(5):
            Question.objects.create(
                assignment=self.assignment,
                question_text=f'Q{i}?', question_data={},
                correct_answer='A', points=1, order_index=i,
            )

    def test_assignment_randomization_defaults(self):
        self.assertFalse(self.assignment.is_randomized)
        self.assertIsNone(self.assignment.question_count)

    def test_assignment_serializer_includes_random_fields(self):
        resp = self.client.get(f'/api/assignments/{self.assignment.id}/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('is_randomized', resp.data)
        self.assertIn('question_count', resp.data)

    def test_random_questions_endpoint(self):
        self.assignment.is_randomized = True
        self.assignment.question_count = 3
        self.assignment.save()
        resp = self.client.get(
            f'/api/questions/?assignment_id={self.assignment.id}&randomize=true'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 3)

    def test_no_randomize_param_returns_all(self):
        self.assignment.is_randomized = True
        self.assignment.question_count = 3
        self.assignment.save()
        resp = self.client.get(f'/api/questions/?assignment_id={self.assignment.id}')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 5)
