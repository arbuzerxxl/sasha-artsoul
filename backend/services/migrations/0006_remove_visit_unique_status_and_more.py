# Generated by Django 4.1.2 on 2022-11-16 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0005_rename_visit_visit_calendar'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='visit',
            name='unique_status',
        ),
        migrations.RemoveConstraint(
            model_name='visit',
            name='unique_client',
        ),
        migrations.AddConstraint(
            model_name='visit',
            constraint=models.UniqueConstraint(fields=('calendar', 'status'), name='unique_status'),
        ),
        migrations.AddConstraint(
            model_name='visit',
            constraint=models.UniqueConstraint(fields=('calendar', 'client'), name='unique_client'),
        ),
    ]
