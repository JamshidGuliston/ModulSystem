from django.test import TestCase
from rest_framework.test import APIClient
from accounts.models import Teacher, Level
from .models import Module, Lesson, ContentType, LessonContent


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
