from django.db import models
from django.urls import reverse
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from .validators import PhoneNumberValidator
from django.apps import apps
from django.contrib import auth
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# Create your models here.


class ServiceManager(models.Manager):

    def create_service(self, name):
        service = self.create(name=name)
        return service


class Service(models.Model):
    MANICURE = 'Маникюр'
    MANICURE_WITH_COATING = 'Маникюр с покрытием'
    CORRECTION = 'Коррекция'
    BUILD_UP = 'Наращивание'
    FRENCH = 'Френч'

    PEDICURE = 'Педикюр'
    PEDICURE_WITH_COATING_FOOT = 'Педикюр с покрытием (стопа)'
    PEDICURE_WITH_COATING_FINGERS = 'Педикюр с покрытием (пальчики)'

    TYPE_OF_SERVICES_CHOICES = [(MANICURE, 'Маникюр'),
                                (MANICURE_WITH_COATING, 'Маникюр с покрытием'),
                                (CORRECTION, 'Коррекция'),
                                (BUILD_UP, 'Наращивание'),
                                (FRENCH, 'Френч'),
                                (PEDICURE, 'Педикюр'),
                                (PEDICURE_WITH_COATING_FOOT, 'Педикюр с покрытием (стопа)'),
                                (PEDICURE_WITH_COATING_FINGERS, 'Педикюр с покрытием (пальчики)'),
                                ]

    SERVICES_PRICE = {
        'Маникюр': 1000,
        'Маникюр с покрытием': 2000,
        'Коррекция': 2800,
        'Наращивание': 3800,
        'Френч': 2500,
        'Педикюр': 2600,
        'Педикюр с покрытием (стопа)': 3000,
        'Педикюр с покрытием (пальчики)': 2300
    }

    name = models.CharField(max_length=30, choices=TYPE_OF_SERVICES_CHOICES, unique=True, verbose_name='Услуга', help_text='Выберите услугу')

    value = models.IntegerField(editable=False, verbose_name='Стоимость услуги')
    
    objects = ServiceManager()

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        self.value = self.SERVICES_PRICE.get(self.name)
        super(Service, self).save(*args, **kwargs)


class Client(models.Model):
    CONSTANT_CLIENT = 'Постоянный клиент'
    SIMPLE_CLIENT = 'Обычный клиент'
    FIRST_VISIT_CLIENT = 'Первый визит'

    CLIENT_CHOICES = [
        (CONSTANT_CLIENT, 'Постоянный клиент'),
        (SIMPLE_CLIENT, 'Обычный клиент'),
        (FIRST_VISIT_CLIENT, 'Первый визит'),
    ]

    first_name = models.CharField(max_length=40, verbose_name='Имя', help_text='Введите имя')
    second_name = models.CharField(max_length=40, verbose_name='Фамилия', help_text='Введите фамилию')
    age = models.PositiveSmallIntegerField(verbose_name='Возраст', help_text='Введите возраст', null=True, blank=True)
    phone_number = models.CharField(max_length=18, verbose_name='Номер телефона', help_text='Введите номер телефона')
    date_of_birth = models.DateField(verbose_name='Дата рождения', help_text='Введите дату рождения', null=True, blank=True)
    date_of_first_visit = models.DateField(verbose_name='Дата первого визита', help_text='Введите дату первого визита', null=True, blank=True)
    client_type = models.CharField(max_length=20, choices=CLIENT_CHOICES, verbose_name='Тип клиента', help_text='Введите тип клиента')

    def __str__(self) -> str:
        return self.second_name + ' ' + self.first_name


class Master(models.Model):
    TOP_MASTER = 'Топ-мастер'
    SIMPLE_MASTER = 'Обычный мастер'
    STUDENT_MASTER = 'Ученик'

    MASTER_CHOICES = [
        (TOP_MASTER, 'Топ-мастер'),
        (SIMPLE_MASTER, 'Обычный мастер'),
        (STUDENT_MASTER, 'Ученик'),
    ]

    first_name = models.CharField(max_length=40, verbose_name='Имя', help_text='Введите имя')
    second_name = models.CharField(max_length=40, verbose_name='Фамилия', help_text='Введите фамилию')
    age = models.PositiveSmallIntegerField(verbose_name='Возраст', help_text='Введите возраст', null=True, blank=True)
    phone_number = models.CharField(max_length=17, verbose_name='Номер телефона', help_text='Введите номер телефона')
    date_of_birth = models.DateField(verbose_name='Дата рождения', help_text='Введите дату рождения', null=True, blank=True)
    qualification = models.CharField(max_length=15, choices=MASTER_CHOICES, verbose_name='Квалификация мастера',
                                     help_text='Выберите квалификалицию', null=True, blank=True)

    def __str__(self) -> str:
        return self.second_name + ' ' + self.first_name


class DiscountManager(models.Manager):
    
    def create_discount(self, name):
        discount = self.create(name=name)
        return discount


class Discount(models.Model):
    FIRST_VISIT = 'Первый визит'
    SIX_VISIT = 'Шестой визит'
    TALK = 'Сарафан'

    DISCOUNT_CHOICES = [
        (FIRST_VISIT, 'Первый визит'),
        (SIX_VISIT, 'Шестой визит'),
        (TALK, 'Сарафан'),
    ]

    DISCOUNTS_PRICE = {
        'Первый визит': 0.15,
        'Шестой визит': 0.35,
        'Сарафан': 500.0,
    }

    name = models.CharField(max_length=15, choices=DISCOUNT_CHOICES, verbose_name='Тип скидки', help_text='Выберите тип скидки', unique=True)
    value = models.FloatField(editable=False, verbose_name='Значение скидки')
    
    objects = DiscountManager()

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        self.value = self.DISCOUNTS_PRICE.get(self.name)
        super(Discount, self).save(*args, **kwargs)


class Visit(models.Model):

    # STATUSES
    PRELIMINARY = 'Предварительная запись'
    SUCCESSFULLY = 'Успешная запись'
    CANCELED = 'Отмененная запись'
    STATUS_CHOICES = [(PRELIMINARY, 'Предварительная запись'),
                      (SUCCESSFULLY, 'Успешная запись'),
                      (CANCELED, 'Отмененная запись'),
                      ]

    # RATINGS
    BEST = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    BAD = 1
    RATING_CHOICES = [(BEST, 'Великолепно'),
                      (HIGH, 'Хорошо'),
                      (MEDIUM, 'Обычно'),
                      (LOW, 'Плохо'),
                      (BAD, 'Ужасно')
                      ]

    visit_date = models.DateTimeField(help_text='Укажите дату и время записи', verbose_name='Дата и время записи')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, help_text='Выберите статус записи', verbose_name='Статус записи')
    service = models.ForeignKey('Service', on_delete=models.CASCADE, help_text='Выберите тип услуги', verbose_name='Тип услуги')
    client = models.ForeignKey('Client', on_delete=models.CASCADE, help_text='Укажите клиента', verbose_name='Клиент')
    master = models.ForeignKey('Master', on_delete=models.CASCADE, help_text='Укажите мастера', verbose_name='Мастер')
    service_price = models.PositiveSmallIntegerField(editable=False, verbose_name='Стоимость услуги')
    discount = models.ForeignKey('Discount', on_delete=models.CASCADE, help_text='Выберите тип скидки', verbose_name='Тип скидки')
    total = models.FloatField(editable=False, verbose_name='Вывод по чеку')
    tax = models.FloatField(editable=False, verbose_name='Налог', null=True)
    review = models.CharField(max_length=250, help_text='Напишите ваш отзыв', verbose_name='Отзыв', null=True, blank=True)
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, unique=True, help_text='Здесь Вы можете указать вашу оценку',
                                              verbose_name='Ваша оценка', null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['visit_date', 'status'], name='unique_status'),
                       models.UniqueConstraint(fields=['visit_date', 'client'], name='unique_client'),
                       models.UniqueConstraint(fields=['visit_date', 'master'], name='unique_master')]

    def __str__(self) -> str:
        return f'[{self.visit_date}] - {self.client}: {self.service}'

    def save(self, *args, **kwargs):
        self.service_price = self.service.value
        if self.status != self.CANCELED:
            if self.discount.name != self.discount.TALK:
                self.total = self.service_price - self.service_price * self.discount.value
            else:
                self.total = self.service_price - self.discount.value
        else:
            self.total = 0
        self.tax = self.total * 0.04
        super(Visit, self).save(*args, **kwargs)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, phone_number, email, password, **extra_fields):
        """
        Create and save a user with the given phone_number, email, and password.
        """
        if not phone_number:
            raise ValueError("Пользователь должен иметь номер телефона")
        email = self.normalize_email(email)
        phone_number = phone_number
        user = self.model(phone_number=phone_number, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(phone_number, email, password, **extra_fields)

    def create_superuser(self, phone_number, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(phone_number, email, password, **extra_fields)

    def with_perm(
        self, perm, is_active=True, include_superusers=True, backend=None, obj=None
    ):
        if backend is None:
            backends = auth._get_backends(return_tuples=True)
            if len(backends) == 1:
                backend, _ = backends[0]
            else:
                raise ValueError(
                    "You have multiple authentication backends configured and "
                    "therefore must provide the `backend` argument."
                )
        elif not isinstance(backend, str):
            raise TypeError(
                "backend must be a dotted import path string (got %r)." % backend
            )
        else:
            backend = auth.load_backend(backend)
        if hasattr(backend, "with_perm"):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()


class User(AbstractBaseUser, PermissionsMixin):

    phone_number_validator = PhoneNumberValidator()

    phone_number = models.CharField(
        max_length=150,
        unique=True,
        help_text=_(
            "Обязательно. Максимально допустимое кол-во символов - 18. Цифры и символы '()', '+' и '_'."
        ),
        validators=[phone_number_validator],
        error_messages={
            "unique": _("Пользователь с таким номером телефона уже существует.")
        },
        verbose_name='Номер телефона'
    )
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    email = models.EmailField(_("email address"), blank=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        abstract = False
        swappable = "AUTH_USER_MODEL"

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def save(self, *args, **kwargs):
        if not self.id and not self.is_staff and not self.is_superuser:
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
