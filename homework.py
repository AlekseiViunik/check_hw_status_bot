import logging
import os
import requests
import sys
import time
import telegram.error

from dotenv import load_dotenv
from http import HTTPStatus
from logging.handlers import RotatingFileHandler
from telegram import Bot

from exceptions import ApiError, SendMessageError

load_dotenv()


PRACTICUM_TOKEN = os.getenv('YA_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID')
RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


VERDICT_STATUSES = {
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
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)
handler = RotatingFileHandler(
    'hw_logger.log', maxBytes=50000000, backupCount=1
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def send_message(bot, message):
    """Отправляем сообщение."""
    logger.info(f'Начало отправки сообщения {message}')
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info(f'Сообщение: {message} отправлено')
    except telegram.error.TelegramError as err:
        raise SendMessageError(
            f'Сообщение "{message}" не отправлено, ошибка {err}'
        )


def get_api_answer(current_timestamp):
    """Делает запрос к единственному эндпоинту API сервиса."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        logger.info('Пытаюсь подключиться к эндпоинту')
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        logger.info(f'Ответ получен: {response.json()}')
        if response.status_code != HTTPStatus.OK:
            raise ApiError('Ошибка подключения к Эндпоинту: '
                           f'ENDPOINT: "{ENDPOINT}", '
                           f'HEADERS: "{HEADERS}", '
                           f'params: "{params}"!')
    except Exception as err:
        raise ApiError(f'Ошибка {err} подключения к Эндпоинту: '
                       f'ENDPOINT: "{ENDPOINT}", '
                       f'HEADERS: "{HEADERS}", '
                       f'params: "{params}"!')
    else:
        return response.json()


def check_response(response):
    """Функция проверяет ответ yandex practicum на корректность."""
    if not isinstance(response, dict) or response is None:
        message = 'Ответ API не содержит словаря с данными'
        raise TypeError(message)

    if response.get('homeworks') is None:
        message = 'Словарь ответа API не содержит ключа homeworks'
        raise KeyError(message)

    if response.get('current_date') is None:
        message = 'Словарь ответа API не содержит ключа current_date'
        raise KeyError(message)

    if not isinstance(response.get('homeworks'), list):
        message = 'Ключ homeworks в ответе API не содержит списка'
        raise TypeError(message)

    if not response.get('homeworks'):
        logger.debug('Статус проверки не изменился')
        return []
    logger.debug(f'ответ {response["homeworks"]}')
    return response['homeworks']


def parse_status(homework):
    """Функция возвращает ответ API со статусом проверки."""
    if homework.get('homework_name') is None:
        message = 'Словарь ответа API не содержит ключа homework_name'
        raise KeyError(message)
    if homework.get('status') is None:
        message = 'Словарь ответа API не содержит ключа status'
        raise KeyError(message)
    homework_name = homework['homework_name']
    verdict_status = homework['status']

    if verdict_status not in VERDICT_STATUSES:
        message = 'Статус ответа не известен'
        raise ApiError(message)
    verdict = VERDICT_STATUSES[verdict_status]

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
    bot.send_message(TELEGRAM_CHAT_ID, 'Начало работы бота')
    current_timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(current_timestamp)
            if response:
                homework = check_response(response)
                if len(homework) > 0:
                    message = parse_status(homework)
                    send_message(bot, message)
                current_timestamp = response.get('current_date')
        except SendMessageError:
            logger.error(f'Сообщение не отправлено')
        except Exception as err:
            bot.send_message(TELEGRAM_CHAT_ID, f'Сбой в программе: {err}')
            logger.error(f'Сбой в работе программы: {err}')
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
