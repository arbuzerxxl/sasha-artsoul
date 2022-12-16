import secrets
import string
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.markdown import text
from aiogram.types import ContentType
from emoji import emojize
from loader import disp
from logger import bot_logger
from settings import URL
from handlers.utils import authentication, sender_to_admin, make_request
from keyboards.reply_keyboards import yes_no_keyboard, continue_cancel_keyboard, check_phone_number_keyboard


class RegistrationUser(StatesGroup):
    user_verification = State()
    check_full_name = State()
    first_name = State()
    last_name = State()
    request = State()


@disp.message_handler(commands=['registration'])
async def process_registration_user(message: types.Message):

    await RegistrationUser.user_verification.set()

    msg = emojize(text(
        f"<i>{message.chat.first_name}, cпасибо, что решили зарегистрироваться.</i>",
        "<i>Я Вас не подведу!</i>",
        "<i>Сперва мне необходим Ваш номер телефона. :eyes:</i>",
        sep='\n'), language='alias')

    await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=check_phone_number_keyboard)


@disp.message_handler(state=RegistrationUser.user_verification, content_types=ContentType.CONTACT)
async def process_user_verification(message: types.Message, state: FSMContext):

    phone_number = message.contact.phone_number.replace('+7', '8')

    response, status = await make_request(method="GET", url=(URL + "api/users/"), data={"phone_number": phone_number})

    if status == 200 and not response:

        await RegistrationUser.next()

        async with state.proxy() as data:
            data['phone_number'] = phone_number
            data['telegram_id'] = message.contact.user_id

        msg = emojize(text(
            f"<i>К сожалению я не нашел Вас в нашей базе, но я это исправлю!</i>",
            f"<i>Могу ли я использовать эти данные как <b>Имя</b> и <b>Фамилия</b>? :eyes:</i>",
            f"<b>{message.chat.last_name} {message.chat.first_name}</b>",
            sep='\n'), language='alias')

        await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=yes_no_keyboard)

    elif status == 200 and response[0]['telegram_id'] is None:

        response, status = await make_request(method="PATCH", url=response[0]['detail_url'], data={"telegram_id": message.contact.user_id})

        if status == 200:

            msg = f"<i>Новые данные занесены в БД</i>"

            await state.finish()

            await message.answer(text=msg, parse_mode=types.ParseMode.HTML)

    elif status == 200:

        await state.finish()

        msg = emojize(text(
            f"<i>Регистрация прервана! Вы уже являетесь зарегистрированным пользователем! :eyes:</i>"))

        await message.answer(text=msg, parse_mode=types.ParseMode.HTML)

    else:

        bot_logger.info(f"[-] Попытка найти пользователя {phone_number} оказалась безуспешной. Status: {status}")

        await state.finish()

        msg = f"<i>Регистрация прервана! Наш администратор в скором времени свяжется с Вами для решения проблемы.</i>"

        await message.answer(text=msg, parse_mode=types.ParseMode.HTML)


@disp.message_handler(state=RegistrationUser.check_full_name)
async def process_check_full_name(message: types.Message, state: FSMContext):

    if message.text == 'Да':

        await RegistrationUser.request.set()

        async with state.proxy() as data:
            data['first_name'] = message.chat.first_name
            data['last_name'] = message.chat.last_name
            alphabet = string.ascii_letters + string.digits
            data['password'] = ''.join(secrets.choice(alphabet) for i in range(20))
            data['is_client'] = True

        msg = emojize(text(f":pencil2: <i>Фуух.. Надеюсь я успел за Вами и все данные верны? </i>",
                           f"<i>Пока вы проверяете, я немного отдохну..</i>:wine_glass: ",
                           f"<b>Имя: </b> {data['first_name']}",
                           f"<b>Фамилия: </b> {data['last_name']}",
                           f"<b>Номер телефона: </b> {data['phone_number']}",
                           f"<b>Пароль: </b> <span class='tg-spoiler'>{data['password']}</span>",
                           sep='\n'), language='alias')

        await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=continue_cancel_keyboard)

    else:

        await RegistrationUser.next()

        msg = emojize(text(f"<i>Эх..Тогда мне нужно знать, как я могу к Вам обращаться? :sweat:</i>",
                           f"<i>Сперва мне нужно узнать <b>ваше имя</b></i> :face_with_rolling_eyes:",
                           sep='\n'), language='alias')

        await message.answer(text=msg, parse_mode=types.ParseMode.HTML)


@disp.message_handler(state=RegistrationUser.first_name)
async def process_first_name(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        data['first_name'] = message.text

    await RegistrationUser.next()

    msg = emojize(text(f":frowning: <i> Вау! Я первый раз слышу такое чудесное имя! Может попытаетесь удивить <b>фамилией</b>?</i> :smirk:",
                       sep='\n'), language='alias')

    await message.answer(text=msg, parse_mode=types.ParseMode.HTML)


@disp.message_handler(state=RegistrationUser.last_name)
async def process_last_name(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        data['last_name'] = message.text
        alphabet = string.ascii_letters + string.digits
        data['password'] = ''.join(secrets.choice(alphabet) for i in range(20))
        data['is_client'] = True

    await RegistrationUser.next()

    msg = emojize(text(f":pencil2: <i>Фуух.. Надеюсь я успел за Вами и все данные верны? </i>",
                       f"<i>Пока вы проверяете, я немного отдохну..</i>:wine_glass: ",
                       f"<b>Имя: </b> {data['first_name']}",
                       f"<b>Фамилия: </b> {data['last_name']}",
                       f"<b>Номер телефона: </b> {data['phone_number']}",
                       f"<b>Пароль: </b> <span class='tg-spoiler'>{data['password']}</span>",
                       sep='\n'), language='alias')

    await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=continue_cancel_keyboard)


@disp.message_handler(state=RegistrationUser.request)
async def process_request_registration_user(message: types.Message, state: FSMContext):
    """Добавление нового пользователя в БД на основе API."""

    async with state.proxy() as data:

        data = await state.get_data()

        await state.finish()

        response, status = await make_request(method="POST", url=(URL + "api/users/"), data=data)

        if status == 201:
            bot_logger.info(
                f"[+] Зарегистрирован новый пользователь. ID: {response['id']}, TG: {response['telegram_id']}, PNONE: {response['phone_number']}"
            )

            data = {"user": response['phone_number'], "user_type": "Первый визит"}

            response, status = await make_request(method="POST", url=(URL + "api/clients/"), data=data)

            if status == 201:
                bot_logger.info(f"[+] Статус пользователя {data['user']} изменен на 'Обычный клиент'")
                msg = "<i>Регистрация успешно завершена!</i>"
                await message.answer(text=msg, parse_mode=types.ParseMode.HTML)

                admin_msg = f"Пользователь: t.me/+7{data['user'][1:]} успешно зарегистрировался."
                await sender_to_admin(msg=admin_msg)

            else:
                bot_logger.info(f"[-] Попытка изменить статус нового пользователя {data['user']} оказалась безуспешной.")
                msg = f"<i>Регистрация прервана! Наш администратор в скором времени свяжется с Вами для решения проблемы.</i>"
                await message.answer(text=msg, parse_mode=types.ParseMode.HTML)

                admin_msg = f"Пользователь: t.me/+7{data['user'][1:]} создан, но статус не поменялся"
                await sender_to_admin(msg=admin_msg)

        else:
            bot_logger.debug("[!] Попытка зарегистрировать нового пользователя оказалась безуспешной.")
            msg = "<i>К сожалению регистрация прервана! Наш администратор в скором времени свяжется с Вами для решения проблемы.</i>"
            await message.answer(text=msg, parse_mode=types.ParseMode.HTML)

            for error in response.values():
                msg = f"<b>{error[0]}</b>"
                await message.answer(text=msg, parse_mode=types.ParseMode.HTML)

            admin_msg = f"Пользователь: t.me/+7{response['phone_number'][1:]} не может зарегистрироваться"
            await sender_to_admin(msg=admin_msg)
