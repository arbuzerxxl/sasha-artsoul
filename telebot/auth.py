import os
import aiohttp
import ujson
from settings import LOGIN, PASSWORD, URL
from logger import bot_logger


async def get_access_token(refresh_token: str):
    """Используя refresh token обновляет access токен в файле"""

    if not refresh_token:
        return await get_tokens()

    url = URL + "api/token/refresh/"
    payload = ujson.dumps({"refresh": refresh_token[7:]})
    headers = {'Content-Type': 'application/json'}

    async with aiohttp.ClientSession(trust_env=True) as session:

        async with session.post(url, data=payload, headers=headers) as response:

            if response.status == 401:
                bot_logger.debug(f"[!] Refresh-token не действительный.")
                return await get_tokens()
            else:
                requested_tokens = await response.json()
                os.environ['ADMIN_ACCESS_TOKEN'] = 'Bearer ' + requested_tokens['access']
                return os.environ.get('ADMIN_ACCESS_TOKEN')


async def get_tokens():
    """Заносит refresh и access токены в файл"""

    url = URL + "api/token/"
    payload = ujson.dumps({"phone_number": LOGIN, "password": PASSWORD})
    headers = {'Content-Type': 'application/json'}

    async with aiohttp.ClientSession(trust_env=True) as session:

        async with session.post(url, data=payload, headers=headers) as response:

            if response.status == 401:
                raise ValueError(f"[WARNING] Ошибка в аутентификации. Неверные данные для пользователя {LOGIN}.")
            else:
                requested_tokens = await response.json()
                os.environ['ADMIN_ACCESS_TOKEN'] = 'Bearer ' + requested_tokens['access']
                os.environ['ADMIN_REFRESH_TOKEN'] = 'Bearer ' + requested_tokens['refresh']
                bot_logger.debug(f"[+] Access-token и refresh-token успешно обновлены.")
                return os.environ.get('ADMIN_ACCESS_TOKEN')


async def verify_token(token: str):
    """Проверяет работоспособность токена"""

    if not token:
        return False

    url = URL + "api/token/verify/"
    payload = ujson.dumps({"token": token[7:]})
    headers = {'Content-Type': 'application/json'}

    async with aiohttp.ClientSession(trust_env=True) as session:

        async with session.post(url, data=payload, headers=headers) as response:

            if response.status == 200:
                return True
            else:
                bot_logger.debug(f"[!] Access-token не действительный. URL: [{url}] Status: [{response.status}].")
                return False


async def auth_with_token():
    """Выполняет аутентификацию для бота посредством JWToken"""

    token = os.environ.get('ADMIN_ACCESS_TOKEN')
    limit_auth = 2

    while limit_auth != 0:
        if await verify_token(token=token):
            bot_logger.debug(f"[+] Access-token действительный. Вход выполнен успешно.")
            return token
        else:
            bot_logger.debug(f"[!] Попыток авторизации: [{limit_auth}].")
            token = os.environ.get('ADMIN_REFRESH_TOKEN')
            token = await get_access_token(refresh_token=token)
            limit_auth -= 1
    raise ValueError(f"[!] Попыток авторизации: [{limit_auth}]. Невозможно получить действительные токены.")
