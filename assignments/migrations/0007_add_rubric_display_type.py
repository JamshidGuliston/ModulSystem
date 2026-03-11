import uuid
from django.db import migrations


def add_rubric_display(apps, schema_editor):
    AssignmentType = apps.get_model('assignments', 'AssignmentType')
    AssignmentType.objects.get_or_create(
        name='rubric_display',
        defaults={
            'id': uuid.uuid4(),
            'description': "Baholash rubrikasi — teacher jadval kiritadi, talaba faqat ko'radi",
            'grader_type': 'none',
            'config_schema': None,
            'teacher': None,
        }
    )


def remove_rubric_display(apps, schema_editor):
    AssignmentType = apps.get_model('assignments', 'AssignmentType')
    AssignmentType.objects.filter(name='rubric_display', teacher=None).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('assignments', '0006_add_discussion_message'),
    ]

    operations = [
        migrations.RunPython(add_rubric_display, remove_rubric_display),
    ]
