# Generated by Django 4.1.2 on 2022-10-26 12:52

from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Calendar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time', models.DateTimeField(help_text='Необходимо указать. Укажите дату и время записи', unique=True, verbose_name='Дата и время записи')),
                ('is_free', models.BooleanField(default=True, editable=False, verbose_name='Запись свободна')),
            ],
            options={
                'verbose_name': 'Календарь',
                'verbose_name_plural': 'Календарь',
            },
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_type', models.CharField(choices=[(None, 'Укажите тип клиента'), ('Постоянный клиент', 'Постоянный клиент'), ('Обычный клиент', 'Обычный клиент'), ('Первый визит', 'Первый визит')], help_text='Введите тип клиента', max_length=20, verbose_name='Тип клиента')),
                ('user', models.OneToOneField(help_text='Выберите зарегистрированного пользователя', limit_choices_to={'is_client': True}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='phone_number', verbose_name='Клиент')),
            ],
            options={
                'verbose_name': 'Клиент',
                'verbose_name_plural': 'Клиенты',
            },
        ),
        migrations.CreateModel(
            name='Visit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[(None, 'Выберите тип записи'), ('Предварительная запись', 'Предварительная запись'), ('Успешная запись', 'Успешная запись'), ('Отмененная запись', 'Отмененная запись')], help_text='Необходимо указать.', max_length=30, verbose_name='Тип записи')),
                ('service', models.CharField(choices=[(None, 'Укажите услугу'), ('Маникюр', 'Маникюр'), ('Маникюр с покрытием', 'Маникюр с покрытием'), ('Коррекция', 'Коррекция'), ('Наращивание', 'Наращивание'), ('Френч', 'Френч'), ('Педикюр', 'Педикюр'), ('Педикюр с покрытием (стопа)', 'Педикюр с покрытием (стопа)'), ('Педикюр с покрытием (пальчики)', 'Педикюр с покрытием (пальчики)')], help_text='Необходимо указать.', max_length=255, verbose_name='Тип услуги')),
                ('service_price', models.DecimalField(decimal_places=2, editable=False, max_digits=6, verbose_name='Стоимость услуги')),
                ('discount', models.DecimalField(blank=True, choices=[(None, 'Укажите скидку'), (Decimal('0.15'), 'Первый визит'), (Decimal('0.35'), 'Шестой визит'), (Decimal('500.00'), 'Сарафан')], decimal_places=2, help_text='Необходимо указать.', max_digits=5, null=True, verbose_name='Тип скидки')),
                ('total', models.DecimalField(decimal_places=2, editable=False, max_digits=7, verbose_name='Вывод по чеку')),
                ('tax', models.DecimalField(decimal_places=2, editable=False, max_digits=5, null=True, verbose_name='Налог')),
                ('review', models.CharField(blank=True, help_text='Напишите ваш отзыв', max_length=250, null=True, verbose_name='Отзыв')),
                ('rating', models.PositiveSmallIntegerField(blank=True, choices=[(None, 'Укажите оценку'), (5, 'Великолепно'), (4, 'Хорошо'), (3, 'Обычно'), (2, 'Плохо'), (1, 'Ужасно')], help_text='Здесь Вы можете указать вашу оценку', null=True, verbose_name='Ваша оценка')),
                ('client', models.ForeignKey(help_text='Необходимо указать.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='services.client', to_field='user_id', verbose_name='Клиент')),
                ('visit', models.OneToOneField(help_text='Необходимо указать. Укажите дату и время записи', limit_choices_to={'is_free': True}, null=True, on_delete=django.db.models.deletion.SET_NULL, to='services.calendar', verbose_name='Дата и время записи')),
            ],
            options={
                'verbose_name': 'Запись',
                'verbose_name_plural': 'Записи',
            },
        ),
        migrations.CreateModel(
            name='Master',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qualification', models.CharField(blank=True, choices=[(None, 'Укажите квалификалицию мастера'), ('Топ-мастер', 'Топ-мастер'), ('Обычный мастер', 'Обычный мастер'), ('Ученик', 'Ученик')], help_text='Выберите квалификалицию мастера', max_length=15, null=True, verbose_name='Квалификация мастера')),
                ('user', models.OneToOneField(help_text='Укажите зарегистрированного пользователя', limit_choices_to={'is_client': False}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, to_field='phone_number', verbose_name='Мастер')),
            ],
            options={
                'verbose_name': 'Мастер',
                'verbose_name_plural': 'Мастера',
            },
        ),
        migrations.AddField(
            model_name='calendar',
            name='master',
            field=models.ForeignKey(help_text='Укажите зарегистрированного мастера', on_delete=django.db.models.deletion.CASCADE, to='services.master', verbose_name='Мастер'),
        ),
        migrations.AddConstraint(
            model_name='visit',
            constraint=models.UniqueConstraint(fields=('visit', 'status'), name='unique_status'),
        ),
        migrations.AddConstraint(
            model_name='visit',
            constraint=models.UniqueConstraint(fields=('visit', 'client'), name='unique_client'),
        ),
        migrations.AddConstraint(
            model_name='calendar',
            constraint=models.UniqueConstraint(fields=('date_time', 'master'), name='unique_date_time'),
        ),
    ]
