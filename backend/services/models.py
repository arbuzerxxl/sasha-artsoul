import decimal
from django.db import models
from django.forms import ValidationError
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


# class ClientManager(models.Manager):
#     def get_by_natural_key(self, user):
#         return self.get(user=user)


class Client(models.Model):

    class Clients(models.TextChoices):

        CONSTANT_CLIENT = 'Постоянный клиент', 'Постоянный клиент'
        SIMPLE_CLIENT = 'Обычный клиент', 'Обычный клиент'
        FIRST_VISIT_CLIENT = 'Первый визит', 'Первый визит'
        __empty__ = 'Укажите пользователя'

    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, limit_choices_to={'is_client': True},
                                help_text='Выберите зарегистрированного пользователя', verbose_name='Клиент')
    client_type = models.CharField(max_length=20, choices=Clients.choices, verbose_name='Тип клиента', help_text='Введите тип клиента')

    # objects = ClientManager()

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self) -> str:
        return self.user.last_name + ' ' + self.user.first_name

    # def natural_key(self):
    #     return self.user


class Master(models.Model):

    class Masters(models.TextChoices):
        TOP_MASTER = 'Топ-мастер', 'Топ-мастер'
        SIMPLE_MASTER = 'Обычный мастер', 'Обычный мастер'
        STUDENT_MASTER = 'Ученик', 'Ученик'
        __empty__ = 'Укажите квалификалицию мастера'

    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, limit_choices_to={'is_client': False},
                                help_text='Укажите зарегистрированного пользователя', verbose_name='Мастер')
    qualification = models.CharField(max_length=15, choices=Masters.choices, verbose_name='Квалификация мастера',
                                     help_text='Выберите квалификалицию мастера', null=True, blank=True)

    class Meta:
        verbose_name = "Мастер"
        verbose_name_plural = "Мастера"

    def __str__(self) -> str:
        return self.user.last_name + ' ' + self.user.first_name


class Visit(models.Model):

    class Statuses(models.TextChoices):
        PRELIMINARY = 'Предварительная запись', 'Предварительная запись'
        SUCCESSFULLY = 'Успешная запись', 'Успешная запись'
        CANCELED = 'Отмененная запись', 'Отмененная запись'
        __empty__ = 'Выберите тип записи'

    class Services(models.IntegerChoices):
        MANICURE = 1000, 'Маникюр'
        MANICURE_WITH_COATING = 2000, 'Маникюр с покрытием'
        CORRECTION = 2800, 'Коррекция'
        BUILD_UP = 3800, 'Наращивание'
        FRENCH = 2500, 'Френч'

        PEDICURE = 2600, 'Педикюр'
        PEDICURE_WITH_COATING_FOOT = 3000, 'Педикюр с покрытием (стопа)'
        PEDICURE_WITH_COATING_FINGERS = 2300, 'Педикюр с покрытием (пальчики)'
        __empty__ = 'Укажите услугу'

    class Ratings(models.IntegerChoices):
        BEST = 5, 'Великолепно'
        HIGH = 4, 'Хорошо'
        MEDIUM = 3, 'Обычно'
        LOW = 2, 'Плохо'
        BAD = 1, 'Ужасно'
        __empty__ = 'Укажите оценку'

    class Discounts(float, models.Choices):
        FIRST_VISIT = 0.15, 'Первый визит'
        SIX_VISIT = 0.35, 'Шестой визит'
        TALK = 500.0, 'Сарафан'
        __empty__ = 'Укажите скидку'

    visit_date = models.DateTimeField(unique=True, help_text='Необходимо указать. Укажите дату и время записи', verbose_name='Дата и время записи')
    status = models.CharField(max_length=30, choices=Statuses.choices, help_text='Необходимо указать.', verbose_name='Тип записи')
    service_price = models.PositiveSmallIntegerField(choices=Services.choices, help_text='Необходимо указать.', verbose_name='Тип услуги')
    client = models.ForeignKey('Client', on_delete=models.SET_NULL, help_text='Необходимо указать.', verbose_name='Клиент', null=True, blank=False)
    master = models.ForeignKey('Master', on_delete=models.SET_NULL, help_text='Необходимо указать.', verbose_name='Мастер', null=True)
    discount = models.FloatField(choices=Discounts.choices, help_text='Необходимо указать.', verbose_name='Тип скидки', null=True, blank=True)  # TODO: настроить DecimalField для всех значений
    total = models.FloatField(editable=False, verbose_name='Вывод по чеку')
    tax = models.FloatField(editable=False, verbose_name='Налог', null=True)
    review = models.CharField(max_length=250, help_text='Напишите ваш отзыв', verbose_name='Отзыв', null=True, blank=True)
    rating = models.PositiveSmallIntegerField(choices=Ratings.choices, help_text='Здесь Вы можете указать вашу оценку',
                                              verbose_name='Ваша оценка', null=True, blank=True)

    class Meta():
        verbose_name = "Запись"
        verbose_name_plural = "Записи"
        constraints = [models.UniqueConstraint(fields=['visit_date', 'status'], name='unique_status'),
                       models.UniqueConstraint(fields=['visit_date', 'client'], name='unique_client'),
                       models.UniqueConstraint(fields=['visit_date', 'master'], name='unique_master'),
                       ]

    def clean(self):
        super().clean()
        if Visit.objects.filter(
            client=self.client, visit_date__month=self.visit_date.month) and Visit.objects.filter(
                client=self.client, visit_date__month=self.visit_date.month).count() >= 3:
            if self.client.client_type != 'Постоянный клиент':
                raise ValidationError('Данный пользователь не может иметь больше 1 записи в месяц')

    def __str__(self) -> str:
        return f'[{self.visit_date}] - {self.client}: {self.get_service_price_display()}'

    def get_client_name(self) -> str:
        return f'{self.client}'

    def save(self, *args, **kwargs):

        if self.status != self.Statuses.CANCELED:
            if not self.discount:
                self.total = self.service_price
            elif self.discount < 1:
                self.total = self.service_price - self.service_price * self.discount
            else:
                self.total = self.service_price - self.discount
        else:
            self.total = 0
        self.tax = self.total * 0.04
        super(Visit, self).save(*args, **kwargs)
