# Generated by Django 4.1.2 on 2022-10-18 15:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='user',
            unique_together={('first_name', 'last_name')},
        ),
    ]