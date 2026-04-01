from django.test import TestCase
from rest_framework.test import APIClient
from accounts.models import Teacher, Student
from courses.models import Module, Lesson
from .models import StudentSessionLog


def make_teacher():
    return Teacher.objects.create(email='t@test.com', password='pass', full_name='T')


def make_student(teacher):
    return Student.objects.create(
        teacher=teacher, email='s@test.com', password='pass', full_name='S'
    )


class SessionLogModelTest(TestCase):
    def setUp(self):
        self.teacher = make_teacher()
        self.student = make_student(self.teacher)

    def test_session_log_creation(self):
        log = StudentSessionLog.objects.create(student=self.student)
        self.assertIsNotNone(log.started_at)
        self.assertIsNone(log.ended_at)
        self.assertIsNone(log.duration_seconds)

    def test_session_log_with_lesson(self):
        module = Module.objects.create(teacher=self.teacher, title='M', order_index=0)
        lesson = Lesson.objects.create(module=module, title='L', order_index=0)
        log = StudentSessionLog.objects.create(student=self.student, lesson=lesson)
        self.assertEqual(log.lesson, lesson)


class SessionLogAPITest(TestCase):
    def setUp(self):
        self.teacher = make_teacher()
        self.student = make_student(self.teacher)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.teacher.api_token}')

    def test_create_session_log(self):
        resp = self.client.post('/api/session-logs/', {
            'student': str(self.student.id),
        }, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertIn('id', resp.data)
        self.assertIn('started_at', resp.data)

    def test_end_session_log(self):
        log = StudentSessionLog.objects.create(student=self.student)
        resp = self.client.patch(f'/api/session-logs/{log.id}/', {
            'ended_at': '2026-04-01T12:30:00Z',
            'duration_seconds': 1800,
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['duration_seconds'], 1800)

    def test_list_session_logs_by_student(self):
        StudentSessionLog.objects.create(student=self.student)
        StudentSessionLog.objects.create(student=self.student)
        resp = self.client.get(f'/api/session-logs/?student_id={self.student.id}')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 2)

    def test_teacher_scope(self):
        other_teacher = Teacher.objects.create(
            email='other@test.com', password='pass', full_name='Other'
        )
        other_student = Student.objects.create(
            teacher=other_teacher, email='os@test.com', password='pass', full_name='OS'
        )
        StudentSessionLog.objects.create(student=other_student)
        resp = self.client.get('/api/session-logs/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 0)
