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
        with self.assertRaises(Exception):
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
