import logging
import os
import requests
import sys
import time

from dotenv import load_dotenv
from http import HTTPStatus
from logging.handlers import RotatingFileHandler
from telegram import Bot

load_dotenv()


PRACTICUM_TOKEN = os.getenv('YA_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID')
RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    level=logging.DEBUG,
    filename='program.log',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(
    'hw_logger.log', maxBytes=50000000, backupCount=1
)
logger.addHandler(handler)


class ApiError(Exception):
    """Ошибка, выбрасываемая при некорректной работе с API."""

    pass


def send_message(bot, message):
    """Отправляем сообщение."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info(f'Сообщение: {message} отправлено')
    except Exception as err:
        logger.error(f'Сообщение "{message}" не отправлено, ошибка {err}')


def get_api_answer(current_timestamp):
    """Делает запрос к единственному эндпоинту API сервиса."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        logger.info('Пытаюсь подключиться к эндпоинту')
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code != HTTPStatus.OK:
            raise ApiError('Ошибка подключения к Эндпоинту')
    except Exception as err:
        raise ApiError(f'Ошибка подключения к Эндпоинту! {err}')
    else:
        return response.json()


def check_response(response):
    """Функция проверяет ответ yandex practicum на корректность."""
    if not isinstance(response, dict) or response is None:
        message = 'Ответ API не содержит словаря с данными'
        raise TypeError(message)

    elif any([response.get('homeworks') is None,
              response.get('current_date') is None]):
        message = ('Словарь ответа API не содержит ключей homeworks и/или '
                   'current_date')
        raise KeyError(message)

    elif not isinstance(response.get('homeworks'), list):
        message = 'Ключ homeworks в ответе API не содержит списка'
        raise TypeError(message)

    elif not response.get('homeworks'):
        logger.debug('Статус проверки не изменился')
        return []

    else:
        return response['homeworks']


def parse_status(homework):
    """Функция возвращает ответ API со статусом проверки."""
    if homework.get('homework_name') is None:
        message = 'Словарь ответа API не содержит ключа homework_name'
        raise KeyError(message)
    elif homework.get('status') is None:
        message = 'Словарь ответа API не содержит ключа status'
        raise KeyError(message)
    homework_name = homework['homework_name']
    homework_status = homework['status']

    if homework_status in HOMEWORK_STATUSES:
        verdict = HOMEWORK_STATUSES[homework_status]
    else:
        message = 'Статус ответа не известен'
        raise ApiError(message)

    message = (f'Изменился статус проверки работы "{homework_name}".'
               f' {verdict}')
    logger.debug(message)
    return message


def check_tokens():
    """Проверяет наличие всех переменных окружения."""
    return all((
        PRACTICUM_TOKEN,
        TELEGRAM_TOKEN,
        TELEGRAM_CHAT_ID,
    ))


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        error_message = (
            'Отсутствуют обязательные элементы окружения: '
            'PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID. '
            'Программа принудительно остановлена!'
        )
        logger.critical(error_message)
        sys.exit(error_message)

    bot = Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    prev_status = None
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            cur_status = parse_status(homework)
            if prev_status != cur_status:
                send_message(bot, cur_status)
                prev_status = cur_status
            current_timestamp = response.get('current_date')
        except Exception as err:
            logger.error(f'Сбой в работе программы: {err}')
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
