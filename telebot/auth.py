import ujson
import shelve
import requests
import os
from settings import BASE_DIR, USERNAME, PASSWORD, URL
from logger import bot_logger


def get_access_token(tokens, refresh_token: str):
    """Используя refresh token обновляет access токен в файле"""

    url = URL + "api/token/refresh/"
    payload = ujson.dumps({"refresh": refresh_token[7:]})
    headers = {'Content-Type': 'application/json'}
    response = requests.request("POST", url, headers=headers, data=payload)
    bot_logger.debug(f"[?] Код ответа: [{response.status_code}].")
    if response.status_code == 401:
        bot_logger.debug(f"[!] Refresh-token не действительный.")
        return get_tokens(tokens)
    else:
        data = ujson.loads(response.text)
        tokens['access'] = 'Bearer ' + data['access']
        return tokens['access']


def get_tokens(tokens):
    """Заносит refresh и access токены в файл"""

    url = URL + "api/token/"
    payload = ujson.dumps({"phone_number": USERNAME, "password": PASSWORD})
    headers = {'Content-Type': 'application/json'}
    response = requests.request("POST", url, headers=headers, data=payload)
    bot_logger.debug(f"[?] Код ответа: [{response.status_code}].")
    if response.status_code == 401:
        raise ValueError(f"[WARNING] Ошибка в аутентификации. Неверные данные для пользователя {USERNAME}.")
    else:
        requested_tokens = ujson.loads(response.text)
        tokens['access'] = 'Bearer ' + requested_tokens['access']
        tokens['refresh'] = 'Bearer ' + requested_tokens['refresh']
        bot_logger.debug(f"[+] Access-token и refresh-token успешно обновлены.")
        return tokens['access']


def verify_token(token: str):
    """Проверяет работоспособность токена"""

    url = URL + "api/token/verify/"
    payload = ujson.dumps({"token": token[7:]})
    headers = {'Content-Type': 'application/json'}
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        return True
    else:
        bot_logger.debug(f"[!] Access-token не действительный. Код ответа: [{response.status_code}].")
        return False


def get_token_from_cache(tokens, refresh_token=False):
    """Получает access или refresh токен из файла"""

    if 'access' in tokens and not refresh_token:
        return tokens['access']
    elif 'refresh' in tokens and refresh_token:
        return tokens['refresh']
    else:
        return get_tokens(tokens)


def auth_with_token():
    """Выполняет аутентификацию для бота посредством JWToken"""

    tokens = shelve.open(os.path.join(BASE_DIR, 'tokens'))
    token = get_token_from_cache(tokens=tokens)
    limit_auth = 2

    while True:
        if limit_auth == 0:
            raise ValueError(f"[!] Попыток авторизации: [{limit_auth}]. Невозможно получить действительные токены.")
        elif verify_token(token=token):
            tokens.close()
            bot_logger.debug(f"[+] Access-token действительный. Вход выполнен успешно.")
            break
        else:
            limit_auth -= 1
            bot_logger.debug(f"[!] Попыток авторизации: [{limit_auth}].")
            token = get_token_from_cache(tokens=tokens, refresh_token=True)
            token = get_access_token(tokens=tokens, refresh_token=token)
    return token
