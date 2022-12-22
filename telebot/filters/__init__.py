from .filters import IsAdminFilter, IsClientFilter
from aiogram import Dispatcher


def setup(disp: Dispatcher):
    disp.filters_factory.bind(IsAdminFilter)
    disp.filters_factory.bind(IsClientFilter)
