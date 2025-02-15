import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv
from telegram import TelegramError

from exceptions import NoValidStatusCode, NoValidStatusHomework, \
    NoNameHomework, NoRequiredKey, ApiConnectionError

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверяет доступность переменных окружения."""
    for name, token in {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID
    }.items():
        if not token:
            logging.critical(
                f'Не удалось получить переменную окружения {name}'
            )
            return False
    else:
        return True


def send_message(bot, message):
    """Отправляет сообщение пользователю."""
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
        )
        logging.debug(f'Сообщение отправлено {message}')
    except TelegramError as error:
        logging.error(f'Не удалось отправить сообщение. Ошибка {error}')


def get_api_answer(timestamp):
    """Делает запрос к API сервиса Практикум.Домашка.
    Возвращает словарь.
    """
    try:

        response = requests.get(
            url=ENDPOINT,
            headers=HEADERS,
            params={'from_date': timestamp},
        )
        if response.status_code != HTTPStatus.OK:
            raise NoValidStatusCode
        return response.json()
    except requests.RequestException:
        raise ApiConnectionError


def check_response(response):
    """Проверяет корректность ответа API."""
    if not isinstance(response, dict) or \
            not isinstance(response.get('homeworks'), list):
        raise TypeError
    keys = ('homeworks', 'current_date')
    if all(key in response.keys() for key in keys):
        return True
    else:
        raise NoRequiredKey


def parse_status(homework):
    """Возвращает строку со статусом домашки."""
    if 'homework_name' not in homework:
        raise NoNameHomework
    homework_name = homework['homework_name']
    status = homework['status']
    if not (verdict := HOMEWORK_VERDICTS.get(status)):
        raise NoValidStatusHomework
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        sys.exit(1)
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = 0
    sent_message = None
    while True:
        try:
            response = get_api_answer(timestamp)
            if check_response(response):
                for homework in response.get('homeworks'):
                    message = parse_status(homework)
                    if sent_message != message:
                        send_message(bot, message)
                        sent_message = message
                timestamp = int(time.time())

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(pathname)s:%(lineno)d '
               '- %(levelname)s - %(message)s',
    )
    main()
