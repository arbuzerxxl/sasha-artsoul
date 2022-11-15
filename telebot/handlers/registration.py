import ujson
import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.markdown import text
from emoji import emojize
from telebot.loader import disp
from telebot.logger import bot_logger
from telebot.settings import URL
from telebot.handlers.utils import authorization, sender_to_admin
from telebot.keyboards.reply_keyboards import yes_no_keyboard, continue_cancel_keyboard


class RegistrationUser(StatesGroup):
    check_full_name = State()
    first_name = State()
    last_name = State()
    phone_number = State()
    password = State()
    request = State()


@disp.message_handler(commands=['registration'])
async def process_registration_user(message: types.Message):

    await RegistrationUser.check_full_name.set()

    msg = emojize(text(
        f"<i>{message.chat.first_name}, cпасибо, что решили зарегистрироваться. Я Вас не подведу!</i>",
        f"<i>Сперва мне нужно понять, могу ли я использовать эти данные как <b>Имя</b> и <b>Фамилия</b>? :eyes:</i>",
        f"<b>{message.chat.last_name} {message.chat.first_name}</b>",
        sep='\n'), language='alias')

    await message.answer(text=msg, parse_mode=types.ParseMode.HTML, reply_markup=yes_no_keyboard)


@disp.message_handler(state=RegistrationUser.check_full_name)
async def process_check_full_name(message: types.Message, state: FSMContext):

    if message.text == 'Да':
        await RegistrationUser.phone_number.set()
        async with state.proxy() as data:
            data['first_name'] = message.chat.first_name
            data['last_name'] = message.chat.last_name

        msg = emojize(text(f"<i>Еще мне очень-очень нужен Ваш <b>номер телефона</b> для быстрой обратной связи</i> :flushed:",
                           f":zipper_mouth_face: <i>Можете на меня рассчитывать, я буду хранить Ваш номер в своем сердце.. кхм-кхм.. хранилище.</i> :purple_heart:",
                           sep='\n'), language='alias')

        await message.answer(text=msg, parse_mode=types.ParseMode.HTML)

    else:
        await RegistrationUser.first_name.set()

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

    await RegistrationUser.next()
    msg = emojize(text(f":exploding_head: :exploding_head: :exploding_head:",
                       f"<i>Еще мне очень-очень нужен Ваш <b>номер телефона</b> для быстрой обратной связи</i> :flushed:",
                       f":zipper_mouth_face: <i>Можете на меня рассчитывать, я буду хранить Ваш номер в своем сердце.. кхм-кхм.. хранилище.</i> :purple_heart:",
                       sep='\n'), language='alias')

    await message.answer(text=msg, parse_mode=types.ParseMode.HTML)


@disp.message_handler(state=RegistrationUser.phone_number)
async def process_phone_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone_number'] = message.text

    await RegistrationUser.next()
    msg = emojize(text(f":full_moon_with_face: <span class='tg-spoiler'><i>Последнее что мне необходимо, это пароль.</i></span>",
                       f"<span class='tg-spoiler'><i>Это обезопасит ваши данные и я всегда смогу Вас узнать! </i></span> :full_moon_with_face:",
                       sep='\n'), language='alias')

    await message.answer(text=msg, parse_mode=types.ParseMode.HTML)


@disp.message_handler(state=RegistrationUser.password)
async def process_password(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['password'] = message.text
        data['is_client'] = True
        data['telegram_id'] = message.from_id
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
        bot_logger.info(f"[?] Обработка события: {message}")

        token = authorization()

        url = URL + "api/users/"
        headers = {'Content-Type': 'application/json', 'Authorization': token}
        data = await state.get_data()
        payload = ujson.dumps(data)
        await state.finish()
        response = requests.request("POST", url, headers=headers, data=payload)
        bot_logger.info(f"[?] Запрос по адресу [{url}]. Код ответа: [{response.status_code}]. Содержимое: {response.text}.")
        response_data = ujson.loads(response.content)
        if response.status_code == 201 and response.content:
            bot_logger.info(
                f"[+] Зарегистрирован новый пользователь. ID: {response_data['id']}, TG: {response_data['telegram_id']}, PNONE: {response_data['phone_number']}"
            )
            url = URL + "api/clients/"
            payload = ujson.dumps({"user": response_data['phone_number'], "user_type": "Обычный клиент"})
            response = requests.request("POST", url, headers=headers, data=payload)

            if response.status_code == 201 and response.content:
                bot_logger.info(f"[+] Статус пользователя {response_data['phone_number']} изменен на 'Обычный клиент'")
                msg = "<i>Регистрация успешно завершена!</i>"
                await message.answer(text=msg, parse_mode=types.ParseMode.HTML)

                admin_msg = f"Пользователь: t.me/+7{response_data['phone_number'][1:]} успешно зарегистрировался."
                await sender_to_admin(msg=admin_msg)

            else:
                bot_logger.info(f"[-] Попытка изменить статус нового пользователя {response_data['phone_number']} оказалась безуспешной.")
                msg = f"<i>Регистрация прервана! Наш администратор в скором времени свяжется с Вами для решения проблемы.</i>"
                await message.answer(text=msg, parse_mode=types.ParseMode.HTML)

                admin_msg = f"Пользователь: t.me/+7{response_data['phone_number'][1:]} создан, но статус не поменялся"
                await sender_to_admin(msg=admin_msg)

        else:
            bot_logger.debug("[!] Попытка зарегистрировать нового пользователя оказалась безуспешной.")
            msg = "<i>К сожалению регистрация прервана! Наш администратор в скором времени свяжется с Вами для решения проблемы.</i>"
            await message.answer(text=msg, parse_mode=types.ParseMode.HTML)

            for error in response_data.values():
                msg = f"<b>{error[0]}</b>"
                await message.answer(text=msg, parse_mode=types.ParseMode.HTML)

            admin_msg = f"Пользователь: t.me/+7{response_data['phone_number'][1:]} не может зарегистрироваться"
            await sender_to_admin(msg=admin_msg)
