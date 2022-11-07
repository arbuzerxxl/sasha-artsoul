from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class PhoneNumberValidator(validators.RegexValidator):
    regex = r"^(\+7|7|8)?[\s\-]?\(?([489][0-9]{2})\)?[\s\-]?([0-9]{3})[\s\-]?([0-9]{2})[\s\-]?([0-9]{2})$"
    message = _(
        "Пожалуйста, введите корректный номер телефона. Вы можете использовать '8' или '+7'. "
        "Пример: 89855310868, +79855310868. "
        "Если вы используете скобки для указания провайдера, отделите их пробелами. "
        "Пример: +7 (926) 777-77-77"
    )
    flags = 0
