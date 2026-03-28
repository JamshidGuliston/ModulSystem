from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assignments', '0007_add_rubric_display_type'),
    ]

    operations = [
        # 1. grading_prompt maydoni
        migrations.AddField(
            model_name='assignmentpart',
            name='grading_prompt',
            field=models.TextField(
                blank=True, null=True,
                help_text="AI ga yuboriladigan baholash mezoni (Speaking uchun)",
            ),
        ),
        # 2. max_score maydoni (Part 3 uchun 6, qolganlar 5)
        migrations.AddField(
            model_name='assignmentpart',
            name='max_score',
            field=models.IntegerField(
                default=5,
                help_text="Bu part uchun maksimal ball",
            ),
        ),
        # 3. speaking AssignmentType (global)
        migrations.RunSQL(
            sql="""
                INSERT INTO assignment_type (id, teacher_id, name, description, grader_type, config_schema)
                VALUES (
                    gen_random_uuid(),
                    NULL,
                    'speaking',
                    'Multilevel Speaking Mock Test — AI baholaydi',
                    'ai',
                    NULL
                )
                ON CONFLICT DO NOTHING;
            """,
            reverse_sql="DELETE FROM assignment_type WHERE name = 'speaking' AND teacher_id IS NULL;",
        ),
    ]
