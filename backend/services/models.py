import locale
from datetime import datetime
from django.utils import timezone
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

    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, limit_choices_to={'is_staff': False},
                                help_text='Выберите зарегистрированного пользователя', verbose_name='Клиент', to_field='phone_number')
    user_type = models.CharField(max_length=20, choices=Clients.choices, default=Clients.FIRST_VISIT_CLIENT,
                                 verbose_name='Тип клиента', help_text='Введите тип клиента')
    last_visit_manicure = models.DateTimeField(default=None, null=True, blank=True, verbose_name='Дата последнего маникюра')
    last_visit_pedicure = models.DateTimeField(default=None, null=True, blank=True, verbose_name='Дата последнего педикюра')

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        ordering = ['user__last_name']

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

    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, limit_choices_to={'is_staff': True},
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
    is_free = models.BooleanField(default=True, editable=True, verbose_name='Запись свободна')

    class Meta:
        verbose_name = "Календарь"
        verbose_name_plural = "Календарь"
        constraints = [models.UniqueConstraint(fields=['date_time', 'master'], name='unique_date_time')]
        ordering = ['date_time']

    def __str__(self) -> str:

        return f'Дата: {timezone.localtime(self.date_time).strftime("%d-%b-%Y %a %H:%M")} Мастер: {self.master.user}'

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

    class Discounts(Decimal, models.Choices):  # TODO: скидка не работает в API

        FIRST_VISIT = '0.15', 'Первый визит'
        SIX_VISIT = '0.35', 'Шестой визит'
        TALK = '500.00', 'Сарафан'
        __empty__ = 'Укажите скидку'

    calendar = models.OneToOneField('Calendar', on_delete=models.PROTECT, unique=True, db_index=True, blank=True, limit_choices_to={'is_free': True},
                                    help_text='Необходимо указать. Укажите дату и время записи', verbose_name='Дата и время записи')
    status = models.CharField(max_length=30, db_index=True, choices=Statuses.choices,
                              help_text='Необходимо указать.', verbose_name='Тип записи')
    service = models.CharField(max_length=255, choices=Services.choices, help_text='Необходимо указать.', verbose_name='Тип услуги')
    service_price = models.DecimalField(max_digits=6, decimal_places=2, editable=False, verbose_name='Стоимость услуги')
    client = models.ForeignKey('Client', on_delete=models.PROTECT, db_index=True, help_text='Необходимо указать.',
                               verbose_name='Клиент', blank=False, to_field='user_id')
    discount = models.DecimalField(max_digits=5, decimal_places=2, choices=Discounts.choices, default=None,
                                   help_text='Необходимо указать.', verbose_name='Тип скидки', null=True, blank=True)
    extra = models.CharField(max_length=255, null=True, blank=True, verbose_name='Доп. услуги')
    extra_total = models.DecimalField(max_digits=6, decimal_places=2, default=None,
                                      verbose_name='Стоимость доп. услуги', null=True, blank=True)
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

        if self.extra_total:
            self.service_price = self.SERVICE_PRICES[self.service] + self.extra_total
        else:
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

    @staticmethod
    def searchNextCalendarEntry(visit=None, service: str = None) -> Calendar | None:

        if visit and hasattr(visit, 'service') and visit.service in [Visit.Services.CORRECTION, Visit.Services.BUILD_UP]:

            local_time = timezone.localtime(visit.calendar.date_time)

        elif service and hasattr(visit, 'initial_data') and service in [Visit.Services.CORRECTION, Visit.Services.BUILD_UP]:

            calendar = Calendar.objects.get(pk=visit.initial_data['calendar'])

            local_time = timezone.localtime(calendar.date_time)

        else:
            return None

        next_calendar_datetime = timezone.make_aware(datetime(year=local_time.year, month=local_time.month, day=local_time.day,
                                                              hour=local_time.hour + 2, minute=local_time.minute))

        try:
            next_calendar = Calendar.objects.get(date_time=next_calendar_datetime)
            return next_calendar
        except Calendar.DoesNotExist:
            return None

    def setNextCalendarEntry(self, close: bool):

        next_calendar: Calendar | None = Visit.searchNextCalendarEntry(visit=self)

        if next_calendar and close is True:
            next_calendar.is_free = False
            next_calendar.save()

        if next_calendar and close is False:
            next_calendar.is_free = True
            next_calendar.save()

    def clean(self):

        super().clean()

        # для возможности изменять поля в админке пробрасывается нынешнее значение из календаря
        try:
            prev_visit_data = Visit.objects.get(pk=self.pk)
            self.calendar = prev_visit_data.calendar
        except Visit.DoesNotExist:
            pass

        # проверка клиента на количество записей в месяц и его статус
        client_also_month_visits = Visit.objects.filter(client=self.client, calendar__date_time__month=self.calendar.date_time.month)

        if client_also_month_visits and client_also_month_visits.count() >= 2 and self.client.user_type == 'Первый визит':
            raise ValidationError('Данный пользователь не может иметь больше 2 записей в месяц')

        # проверка след. записи из-за времени процедуры более 2 ч.
        next_visit: Calendar | None = Visit.searchNextCalendarEntry(visit=self)
        if next_visit and next_visit.is_free is False:
            raise ValidationError("'Наращивание' и 'Коррекция' требуют больше 2 часов работы. Найдите более подходящее время записи.")

    def __str__(self) -> str:

        return f'Запись: {self.calendar} Клиент: [{self.client}] Стоимость: [{self.total}]'

    def delete(self, *args, **kwargs):

        self.calendar.is_free = True
        self.calendar.save()
        self.setNextCalendarEntry(close=False)
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):

        try:
            prev_visit_data = Visit.objects.get(pk=self.pk)

            if prev_visit_data.calendar.pk != self.calendar.pk:
                prev_visit_data.calendar.is_free = True
                prev_visit_data.calendar.save()
        except Visit.DoesNotExist:
            pass

        if self.status == self.Statuses.SUCCESSFULLY:
            self.change_visit_dates()
        self.solveProfit()
        self.solveTax()
        self.calendar.is_free = False
        self.calendar.save()
        self.setNextCalendarEntry(close=True)
        super(Visit, self).save(*args, **kwargs)
