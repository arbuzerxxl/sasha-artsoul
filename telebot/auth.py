import ujson
import shelve
import requests
import os
from settings import BASE_DIR, USERNAME, PASSWORD, URL


def get_access_token(tokens, refresh_token: str):
    """Используя refresh token обновляет access токен в файле"""

    url = URL + "api/token/refresh/"
    payload = ujson.dumps({"refresh": refresh_token[7:]})
    headers = {'Content-Type': 'application/json'}
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 401:  # refresh token is overdue
        get_tokens(tokens)
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
    if response.status_code == 401:
        raise ValueError('Ошибка в аутентификации. Неверные данные для пользователя.')
    else:
        requested_tokens = ujson.loads(response.text)
        tokens['access'] = 'Bearer ' + requested_tokens['access']
        tokens['refresh'] = 'Bearer ' + requested_tokens['refresh']
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
        return False


def get_token_from_cache(tokens, refresh_token=False):
    """Получает access или refresh токен из файла"""

    if 'access' in tokens and not refresh_token:
        return tokens['access']
    elif 'refresh' in tokens and refresh_token:
        return tokens['refresh']
    else:
        return get_tokens(tokens)


def auth_with_token(auth_success=False):
    """Выполняет аутентификацию для бота посредством JWToken"""

    tokens = shelve.open(os.path.join(BASE_DIR, 'tokens'))
    token = get_token_from_cache(tokens=tokens)

    while not auth_success:
        if verify_token(token=token):
            auth_success = True
            tokens.close()
        else:
            token = get_token_from_cache(tokens=tokens, refresh_token=True)
            if not verify_token(token=token):
                token = get_tokens(tokens=tokens)
    return token
