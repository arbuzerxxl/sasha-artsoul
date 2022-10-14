from random import choices
from tabnanny import check
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.forms import ValidationError
from .validators import PhoneNumberValidator
from django.contrib import auth
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models.functions import Length


models.ForeignKey.register_lookup(Length)


class Client(models.Model):

    class Clients(models.TextChoices):

        CONSTANT_CLIENT = 'Постоянный клиент', 'Постоянный клиент'
        SIMPLE_CLIENT = 'Обычный клиент', 'Обычный клиент'
        FIRST_VISIT_CLIENT = 'Первый визит', 'Первый визит'
        __empty__ = 'Укажите пользователя'

    user = models.OneToOneField('User', on_delete=models.CASCADE, limit_choices_to={'is_client': True},
                                help_text='Выберите зарегистрированного пользователя', verbose_name='Клиент')
    client_type = models.CharField(max_length=20, choices=Clients.choices, verbose_name='Тип клиента', help_text='Введите тип клиента')

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self) -> str:
        return self.user.last_name + ' ' + self.user.first_name


class Master(models.Model):

    class Masters(models.TextChoices):
        TOP_MASTER = 'Топ-мастер', 'Топ-мастер'
        SIMPLE_MASTER = 'Обычный мастер', 'Обычный мастер'
        STUDENT_MASTER = 'Ученик', 'Ученик'
        __empty__ = 'Укажите квалификалицию мастера'

    user = models.OneToOneField('User', on_delete=models.CASCADE, limit_choices_to={'is_client': False, 'is_superuser': False},
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
    discount = models.FloatField(choices=Discounts.choices, help_text='Необходимо указать.', verbose_name='Тип скидки')
    total = models.FloatField(editable=False, verbose_name='Вывод по чеку')
    tax = models.FloatField(editable=False, verbose_name='Налог', null=True)
    review = models.CharField(max_length=250, help_text='Напишите ваш отзыв', verbose_name='Отзыв', null=True, blank=True)
    rating = models.PositiveSmallIntegerField(choices=Ratings.choices, unique=True, help_text='Здесь Вы можете указать вашу оценку',
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
        if Visit.objects.filter(client=self.client, visit_date__month=self.visit_date.month).count() >= 1:
            if self.client.client_type != 'Постоянный клиент':
                raise ValidationError('Данный пользователь не может иметь больше 1 записи в месяц')

    def __str__(self) -> str:
        return f'[{self.visit_date}] - {self.client}: {self.get_service_price_display()}'

    def save(self, *args, **kwargs):
        if self.status != self.Statuses.CANCELED:
            if self.discount < 1:
                self.total = self.service_price - self.service_price * self.discount
            else:
                self.total = self.service_price - self.discount
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
        phone_number = normallize_phone_number(phone_number=phone_number)
        user = self.model(phone_number=phone_number, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_client", True)

        if extra_fields.get("is_client") is not True:
            raise ValueError("Пользователь обязательно должен иметь статус 'Клиент'")

        return self._create_user(phone_number, email, password, **extra_fields)

    def create_superuser(self, phone_number, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_client", False)

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


def normallize_phone_number(phone_number, full_number=False):
    pn_regex = PhoneNumberValidator().regex
    matched = pn_regex.search(phone_number)
    if full_number:
        return "+7" + f' ({matched[2]}) ' + f'{matched[3]}' + f'-{matched[4]}-' + f'{matched[5]}'
    return "8" + f'{matched[2]}' + f'{matched[3]}' + f'{matched[4]}' + f'{matched[5]}'


class User(AbstractBaseUser, PermissionsMixin):

    phone_number_validator = PhoneNumberValidator()

    phone_number = models.CharField(
        max_length=150,
        unique=True,
        help_text="Обязательно. Максимально допустимое кол-во символов - 18. Цифры и символы '()', '+' и '_'.",
        validators=[phone_number_validator],
        error_messages={
            "unique": "Пользователь с таким номером телефона уже существует."
        },
        verbose_name='Номер телефона'
    )
    first_name = models.CharField(_("first name"), max_length=150, null=True, blank=False)
    last_name = models.CharField(_("last name"), max_length=150, null=True, blank=False)
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
    is_client = models.BooleanField(
        "Клиент",
        default=False,
        help_text="Отметьте, если пользователь должен считаться клиентом.",
    )

    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["last_name", "first_name", "email"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        abstract = False
        swappable = "AUTH_USER_MODEL"

    def __str__(self):
        return self.last_name + ' ' + self.first_name

    def clean(self):
        super().clean()
        self.phone_number = normallize_phone_number(self.phone_number)
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

        # if not self.id and not self.is_staff and not self.is_superuser:
        self.password = make_password(self.password)
        super().save(*args, **kwargs)
