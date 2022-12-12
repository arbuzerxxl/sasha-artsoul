import locale
from decimal import Decimal, getcontext
from django.db import models
from django.forms import ValidationError
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

getcontext().prec = 10
locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')


class Client(models.Model):

    class Clients(models.TextChoices):

        CONSTANT_CLIENT = 'Постоянный клиент', 'Постоянный клиент'
        FIRST_VISIT_CLIENT = 'Первый визит', 'Первый визит'
        __empty__ = 'Укажите тип клиента'

    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, limit_choices_to={'is_client': True},
                                help_text='Выберите зарегистрированного пользователя', verbose_name='Клиент', to_field='phone_number')
    user_type = models.CharField(max_length=20, choices=Clients.choices, default=Clients.FIRST_VISIT_CLIENT,
                                 verbose_name='Тип клиента', help_text='Введите тип клиента')
    last_visit_manicure = models.DateTimeField(default=None, null=True, blank=True, verbose_name='Дата последнего маникюра')
    last_visit_pedicure = models.DateTimeField(default=None, null=True, blank=True, verbose_name='Дата последнего педикюра')

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self) -> str:
        return f'{self.user.last_name} {self.user.first_name}'

    def save(self, *args, **kwargs):
        self.user_phone_number = self.user.phone_number
        super(Client, self).save(*args, **kwargs)


class Master(models.Model):

    class Masters(models.TextChoices):
        TOP_MASTER = 'Топ-мастер', 'Топ-мастер'
        SIMPLE_MASTER = 'Обычный мастер', 'Обычный мастер'
        STUDENT_MASTER = 'Ученик', 'Ученик'
        __empty__ = 'Укажите квалификалицию мастера'

    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, limit_choices_to={'is_client': False},
                                help_text='Укажите зарегистрированного пользователя', verbose_name='Мастер', to_field='phone_number')
    user_type = models.CharField(max_length=15, choices=Masters.choices, verbose_name='Квалификация мастера',
                                 help_text='Выберите квалификалицию мастера', null=True, blank=True)

    class Meta:
        verbose_name = "Мастер"
        verbose_name_plural = "Мастера"

    def __str__(self) -> str:
        return f'{self.user.last_name} {self.user.first_name}'


class Calendar(models.Model):

    date_time = models.DateTimeField(unique=True, help_text='Необходимо указать. Укажите дату и время записи', verbose_name='Дата и время записи')
    master = models.ForeignKey('Master', on_delete=models.CASCADE, help_text='Укажите зарегистрированного мастера',
                               verbose_name='Мастер', to_field='user_id')
    is_free = models.BooleanField(default=True, editable=False, verbose_name='Запись свободна')

    class Meta:
        verbose_name = "Календарь"
        verbose_name_plural = "Календарь"
        constraints = [models.UniqueConstraint(fields=['date_time', 'master'], name='unique_date_time')]

    def __str__(self) -> str:
        return f'Дата: {self.date_time.strftime("%d-%b-%Y %a %H:%M")} Мастер: {self.master.user}'

    def save(self, *args, **kwargs):

        super(Calendar, self).save(*args, **kwargs)


class Visit(models.Model):

    SERVICE_PRICES = {
        'Маникюр': Decimal(1000),
        'Маникюр с покрытием': Decimal(2000),
        'Коррекция': Decimal(2800),
        'Наращивание': Decimal(3800),
        'Френч': Decimal(2500),
        'Педикюр': Decimal(2600),
        'Педикюр с покрытием (стопа)': Decimal(3000),
        'Педикюр с покрытием (пальчики)': Decimal(2300),
    }

    class Statuses(models.TextChoices):
        PRELIMINARY = 'Предварительная запись', 'Предварительная запись'
        SUCCESSFULLY = 'Успешная запись', 'Успешная запись'
        __empty__ = 'Выберите тип записи'

    class Services(models.TextChoices):
        MANICURE = 'Маникюр', 'Маникюр'
        MANICURE_WITH_COATING = 'Маникюр с покрытием', 'Маникюр с покрытием'
        CORRECTION = 'Коррекция', 'Коррекция'
        BUILD_UP = 'Наращивание', 'Наращивание'
        FRENCH = 'Френч', 'Френч'
        PEDICURE = 'Педикюр', 'Педикюр'
        PEDICURE_WITH_COATING_FOOT = 'Педикюр с покрытием (стопа)', 'Педикюр с покрытием (стопа)'
        PEDICURE_WITH_COATING_FINGERS = 'Педикюр с покрытием (пальчики)', 'Педикюр с покрытием (пальчики)'
        __empty__ = 'Укажите услугу'

    class Ratings(models.IntegerChoices):
        BEST = 5, 'Великолепно'
        HIGH = 4, 'Хорошо'
        MEDIUM = 3, 'Обычно'
        LOW = 2, 'Плохо'
        BAD = 1, 'Ужасно'
        __empty__ = 'Укажите оценку'

    class Discounts(Decimal, models.Choices):
        FIRST_VISIT = '0.15', 'Первый визит'
        TALK = '500.00', 'Сарафан'
        __empty__ = 'Укажите скидку'

    calendar = models.OneToOneField('Calendar', on_delete=models.PROTECT, unique=True, blank=True, limit_choices_to={'is_free': True},
                                    help_text='Необходимо указать. Укажите дату и время записи', verbose_name='Дата и время записи')
    status = models.CharField(max_length=30, choices=Statuses.choices, default='Предварительная запись', help_text='Необходимо указать.', verbose_name='Тип записи')
    service = models.CharField(max_length=255, choices=Services.choices, help_text='Необходимо указать.', verbose_name='Тип услуги')
    service_price = models.DecimalField(max_digits=6, decimal_places=2, editable=False, verbose_name='Стоимость услуги')
    client = models.ForeignKey('Client', on_delete=models.SET_NULL, help_text='Необходимо указать.',
                               verbose_name='Клиент', null=True, blank=False, to_field='user_id')
    discount = models.DecimalField(max_digits=5, decimal_places=2, choices=Discounts.choices, default=None,
                                   help_text='Необходимо указать.', verbose_name='Тип скидки', null=True, blank=True)
    total = models.DecimalField(max_digits=7, decimal_places=2, editable=False, verbose_name='Вывод по чеку')
    tax = models.DecimalField(max_digits=5, decimal_places=2, editable=False, verbose_name='Налог', null=True)
    review = models.CharField(max_length=250, help_text='Напишите ваш отзыв', verbose_name='Отзыв', null=True, blank=True)
    rating = models.PositiveSmallIntegerField(choices=Ratings.choices, help_text='Здесь Вы можете указать вашу оценку',
                                              verbose_name='Ваша оценка', null=True, blank=True)

    class Meta():
        verbose_name = "Запись"
        verbose_name_plural = "Записи"
        constraints = [models.UniqueConstraint(fields=['calendar', 'status'], name='unique_status'),
                       models.UniqueConstraint(fields=['calendar', 'client'], name='unique_client'),
                       ]

    def isFirstVisit(self):

        if not self.client.last_visit_manicure and not self.client.last_visit_pedicure:
            return True
        else:
            return False

    def change_visit_dates(self):

        if self.service not in [self.Services.PEDICURE,
                                self.Services.PEDICURE_WITH_COATING_FINGERS,
                                self.Services.PEDICURE_WITH_COATING_FOOT]:

            self.client.last_visit_manicure = self.calendar.date_time

        else:
            self.client.last_visit_pedicure = self.calendar.date_time

        if self.client.user_type == "Первый визит":
            self.client.user_type = "Постоянный клиент"

        self.client.save()

    def solveProfit(self):

        self.service_price = self.SERVICE_PRICES[self.service]

        if self.isFirstVisit():
            self.discount = self.Discounts.FIRST_VISIT

        if not self.discount:
            self.total = self.service_price
        elif self.discount < 1:
            self.total = self.service_price - self.service_price * self.discount
        else:
            self.total = self.service_price - self.discount

    def solveTax(self):

        self.tax = self.total * Decimal('0.04')

    def clean(self):

        super().clean()
        try:
            prev_visit_data = Visit.objects.get(id=self.id)
            self.calendar = prev_visit_data.calendar
        except Visit.DoesNotExist:
            pass

        if (Visit.objects.filter(client=self.client, calendar__date_time__month=self.calendar.date_time.month) and
            Visit.objects.filter(client=self.client, calendar__date_time__month=self.calendar.date_time.month).count() >= 2 and
                self.client.user_type == 'Первый визит'):
            raise ValidationError('Данный пользователь не может иметь больше 2 записей в месяц')

    def __str__(self) -> str:

        return f'Запись: {self.calendar} Клиент: [{self.client}] Стоимость: [{self.service}]'

    def delete(self, *args, **kwargs):

        self.calendar.is_free = True
        self.calendar.save()
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):

        try:
            prev_visit_data = Visit.objects.get(id=self.id)

            if prev_visit_data.calendar.pk != self.calendar.pk:
                prev_visit_data.calendar.is_free = True
                prev_visit_data.calendar.save()
        except Visit.DoesNotExist:
            pass

        if self.status == self.Statuses.SUCCESSFULLY:
            self.change_visit_dates()
        else:
            self.solveProfit()
            self.solveTax()
            self.calendar.is_free = False
            self.calendar.save()
        super(Visit, self).save(*args, **kwargs)
