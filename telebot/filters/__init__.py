from .is_admin import IsAdminFilter
from aiogram import Dispatcher


def setup(disp: Dispatcher):
    disp.filters_factory.bind(IsAdminFilter)
