from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from services.validators import PhoneNumberValidator
from django.contrib import auth
from django.contrib.auth.hashers import make_password, identify_hasher
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def normallize_phone_number(phone_number, full_number=False):
    pn_regex = PhoneNumberValidator().regex
    matched = pn_regex.search(phone_number)
    if full_number:
        return "+7" + f' ({matched[2]}) ' + f'{matched[3]}' + f'-{matched[4]}-' + f'{matched[5]}'
    return "8" + f'{matched[2]}' + f'{matched[3]}' + f'{matched[4]}' + f'{matched[5]}'


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


class User(AbstractBaseUser, PermissionsMixin):

    phone_number_validator = PhoneNumberValidator()

    phone_number = models.CharField(
        max_length=12,
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
        unique_together = [['first_name', 'last_name']]

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
        try:
            _alg = identify_hasher(self.password)
        except ValueError:
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
