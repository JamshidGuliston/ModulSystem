from django.db import IntegrityError
from django.test import TestCase
from rest_framework.test import APIClient
from .models import Teacher, Level


def make_teacher(**kwargs):
    defaults = dict(email='t@test.com', password='pass', full_name='Teacher')
    defaults.update(kwargs)
    return Teacher.objects.create(**defaults)


class LevelModelTest(TestCase):
    def test_level_creation(self):
        teacher = make_teacher()
        level = Level.objects.create(teacher=teacher, name='B1', order_index=1)
        self.assertEqual(str(level), 'B1')
        self.assertEqual(level.teacher, teacher)

    def test_level_unique_per_teacher(self):
        teacher = make_teacher()
        Level.objects.create(teacher=teacher, name='A2')
        with self.assertRaises(IntegrityError):
            Level.objects.create(teacher=teacher, name='A2')


class LevelAPITest(TestCase):
    def setUp(self):
        self.teacher = make_teacher()
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.teacher.api_token}')

    def test_create_level(self):
        resp = self.client.post('/api/levels/', {'name': 'A2', 'order_index': 0})
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data['name'], 'A2')
        self.assertEqual(Level.objects.get(name='A2').teacher, self.teacher)

    def test_list_levels_teacher_scope(self):
        Level.objects.create(teacher=self.teacher, name='A2')
        other = make_teacher(email='other@test.com')
        Level.objects.create(teacher=other, name='B1')
        resp = self.client.get('/api/levels/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)

    def test_delete_level(self):
        level = Level.objects.create(teacher=self.teacher, name='A2')
        resp = self.client.delete(f'/api/levels/{level.id}/')
        self.assertEqual(resp.status_code, 204)

    def test_duplicate_level_name_returns_400(self):
        Level.objects.create(teacher=self.teacher, name='A2')
        resp = self.client.post('/api/levels/', {'name': 'A2', 'order_index': 0})
        self.assertEqual(resp.status_code, 400)

    def test_patch_cannot_reassign_teacher(self):
        other = make_teacher(email='other@test.com')
        level = Level.objects.create(teacher=self.teacher, name='A2')
        resp = self.client.patch(f'/api/levels/{level.id}/', {
            'teacher': str(other.id),
        }, format='json')
        level.refresh_from_db()
        self.assertEqual(level.teacher, self.teacher)


class StudentLevelFieldsTest(TestCase):
    def setUp(self):
        self.teacher = make_teacher()
        self.level = Level.objects.create(teacher=self.teacher, name='B1')
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.teacher.api_token}')

    def test_student_has_level_fields(self):
        from .models import Student
        s = Student.objects.create(
            teacher=self.teacher,
            email='s@test.com',
            password='pass',
            full_name='Student',
            level=self.level,
            placement_done=True,
            initial_score=9,
            group_number='G-101',
        )
        self.assertEqual(s.level, self.level)
        self.assertTrue(s.placement_done)
        self.assertEqual(s.initial_score, 9)
        self.assertEqual(s.group_number, 'G-101')

    def test_student_level_null_by_default(self):
        from .models import Student
        s = Student.objects.create(
            teacher=self.teacher, email='s2@test.com',
            password='pass', full_name='Student2'
        )
        self.assertIsNone(s.level)
        self.assertFalse(s.placement_done)
        self.assertIsNone(s.initial_score)
        self.assertIsNone(s.group_number)

    def test_patch_student_level(self):
        from .models import Student
        s = Student.objects.create(
            teacher=self.teacher, email='s3@test.com',
            password='pass', full_name='Student3'
        )
        resp = self.client.patch(f'/api/students/{s.id}/', {
            'level': str(self.level.id),
            'placement_done': True,
            'initial_score': 7,
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['level']['name'], 'B1')
        self.assertTrue(resp.data['placement_done'])

    def test_existing_student_without_level_still_works(self):
        from .models import Student
        s = Student.objects.create(
            teacher=self.teacher, email='old@test.com',
            password='pass', full_name='OldStudent'
        )
        resp = self.client.get(f'/api/students/{s.id}/')
        self.assertEqual(resp.status_code, 200)
        self.assertIsNone(resp.data['level'])
