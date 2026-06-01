from django.db import IntegrityError
from django.test import TestCase
from rest_framework.test import APIClient
from accounts.models import Teacher, Level
from .models import Module, Lesson, ContentType, LessonContent, ModuleType


def make_teacher():
    return Teacher.objects.create(email='t@test.com', password='pass', full_name='T')


class LessonTypeTest(TestCase):
    def setUp(self):
        self.teacher = make_teacher()
        self.module = Module.objects.create(
            teacher=self.teacher, title='Modul 1', order_index=0
        )

    def test_lesson_default_type_is_regular(self):
        lesson = Lesson.objects.create(
            module=self.module, title='Lesson 1', order_index=0
        )
        self.assertEqual(lesson.lesson_type, 'regular')

    def test_lesson_type_choices(self):
        for lt in ('regular', 'jn', 'on', 'placement'):
            lesson = Lesson.objects.create(
                module=self.module,
                title=f'Lesson {lt}',
                order_index=0,
                lesson_type=lt,
            )
            self.assertEqual(lesson.lesson_type, lt)

    def test_existing_lessons_default_to_regular(self):
        lesson = Lesson.objects.create(
            module=self.module, title='Old Lesson', order_index=0
        )
        self.assertEqual(lesson.lesson_type, 'regular')


class LessonContentLevelTest(TestCase):
    def setUp(self):
        self.teacher = make_teacher()
        self.level_b1 = Level.objects.create(teacher=self.teacher, name='B1')
        self.module = Module.objects.create(
            teacher=self.teacher, title='M', order_index=0
        )
        self.lesson = Lesson.objects.create(
            module=self.module, title='L', order_index=0
        )
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.teacher.api_token}')

    def test_lesson_content_has_level_field(self):
        ct = ContentType.objects.create(name='text')
        lc = LessonContent.objects.create(
            lesson=self.lesson, content_type=ct,
            title='B1 kontent', order_index=0,
            level=self.level_b1,
        )
        self.assertEqual(lc.level, self.level_b1)

    def test_lesson_content_level_null_by_default(self):
        ct = ContentType.objects.create(name='video')
        lc = LessonContent.objects.create(
            lesson=self.lesson, content_type=ct,
            title='Universal kontent', order_index=0,
        )
        self.assertIsNone(lc.level)

    def test_lesson_content_filter_by_level_id(self):
        ct = ContentType.objects.create(name='book')
        lc_b1 = LessonContent.objects.create(
            lesson=self.lesson, content_type=ct,
            title='B1 kontent', order_index=0, level=self.level_b1,
        )
        lc_null = LessonContent.objects.create(
            lesson=self.lesson, content_type=ct,
            title='Barchaga kontent', order_index=1, level=None,
        )
        resp = self.client.get(
            f'/api/lesson-contents/?lesson_id={self.lesson.id}&level_id={self.level_b1.id}'
        )
        self.assertEqual(resp.status_code, 200)
        ids = [item['id'] for item in resp.data]
        self.assertIn(str(lc_b1.id), ids)
        self.assertIn(str(lc_null.id), ids)

    def test_lesson_content_no_level_filter_returns_all(self):
        ct = ContentType.objects.create(name='pres')
        LessonContent.objects.create(
            lesson=self.lesson, content_type=ct,
            title='B1', order_index=0, level=self.level_b1,
        )
        LessonContent.objects.create(
            lesson=self.lesson, content_type=ct,
            title='All', order_index=1, level=None,
        )
        resp = self.client.get(f'/api/lesson-contents/?lesson_id={self.lesson.id}')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 2)


class ModuleTypeModelTest(TestCase):
    def setUp(self):
        self.teacher = make_teacher()

    def test_create_module_type(self):
        mt = ModuleType.objects.create(
            teacher=self.teacher, name='Grammatika', order_index=0
        )
        self.assertEqual(mt.name, 'Grammatika')
        self.assertEqual(mt.teacher, self.teacher)
        self.assertEqual(str(mt), 'Grammatika')

    def test_module_type_unique_per_teacher(self):
        ModuleType.objects.create(teacher=self.teacher, name='Grammatika')
        with self.assertRaises(IntegrityError):
            ModuleType.objects.create(teacher=self.teacher, name='Grammatika')


class ModuleTypeApiTest(TestCase):
    def setUp(self):
        self.teacher = make_teacher()
        self.other = Teacher.objects.create(
            email='o@test.com', password='p', full_name='O'
        )
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.teacher.api_token}')

    def test_create_module_type(self):
        resp = self.client.post('/api/module-types/', {'name': 'Grammatika', 'order_index': 0})
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data['name'], 'Grammatika')
        self.assertEqual(str(self.teacher.id), str(resp.data['teacher']))

    def test_list_only_own_types(self):
        ModuleType.objects.create(teacher=self.teacher, name='Mine')
        ModuleType.objects.create(teacher=self.other, name='Theirs')
        resp = self.client.get('/api/module-types/')
        self.assertEqual(resp.status_code, 200)
        names = [item['name'] for item in resp.data]
        self.assertEqual(names, ['Mine'])

    def test_duplicate_name_rejected(self):
        ModuleType.objects.create(teacher=self.teacher, name='Grammatika')
        resp = self.client.post('/api/module-types/', {'name': 'Grammatika'})
        self.assertEqual(resp.status_code, 400)
        self.assertIn('name', resp.data)

    def test_cannot_retrieve_other_teacher_type(self):
        other_mt = ModuleType.objects.create(teacher=self.other, name='Theirs')
        resp = self.client.get(f'/api/module-types/{other_mt.id}/')
        self.assertEqual(resp.status_code, 404)

    def test_cannot_update_other_teacher_type(self):
        other_mt = ModuleType.objects.create(teacher=self.other, name='Theirs')
        resp = self.client.patch(f'/api/module-types/{other_mt.id}/', {'name': 'Hacked'})
        self.assertEqual(resp.status_code, 404)


class ModuleFieldsTest(TestCase):
    def setUp(self):
        self.teacher = make_teacher()
        self.mt = ModuleType.objects.create(teacher=self.teacher, name='Grammatika')

    def test_module_type_optional(self):
        module = Module.objects.create(
            teacher=self.teacher, title='M', order_index=0
        )
        module.refresh_from_db()
        self.assertIsNone(module.module_type)

    def test_module_type_assignment(self):
        module = Module.objects.create(
            teacher=self.teacher, title='M', order_index=0, module_type=self.mt
        )
        self.assertEqual(module.module_type, self.mt)

    def test_module_teachers_m2m(self):
        other = Teacher.objects.create(email='o2@test.com', password='p', full_name='O2')
        module = Module.objects.create(
            teacher=self.teacher, title='M', order_index=0
        )
        module.teachers.add(other)
        self.assertIn(other, module.teachers.all())
        # teachers M2M is informational: it must not affect the owner FK scoping
        self.assertIn(module, self.teacher.modules.all())
        self.assertNotIn(module, other.modules.all())
