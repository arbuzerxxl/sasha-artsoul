# Generated by Django 4.1.2 on 2022-12-20 15:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0016_alter_visit_client'),
    ]

    operations = [
        migrations.AlterField(
            model_name='visit',
            name='client',
            field=models.ForeignKey(help_text='Необходимо указать.', on_delete=django.db.models.deletion.PROTECT, to='services.client', to_field='user_id', verbose_name='Клиент'),
        ),
    ]
