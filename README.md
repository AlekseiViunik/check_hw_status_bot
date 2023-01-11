# Check_hw_status_bot
![Python version](https://img.shields.io/badge/python-3.7-yellow)

```sh
It is a highly specialized python telegram bot which checks the status of homework each 10 minutes and send it to you in telegram. 
It also write logs in journal.

Possible messages in TG:

- Работа проверена: ревьюеру всё понравилось. Ура! - Everything is good. Yippee!
- Работа взята на проверку ревьюером. - It is in progress
- Работа проверена: у ревьюера есть замечания. - Need to fix something

Это узкоспециализированный телеграмм бот, написанный на python, который проверяет статус домашнего задания и присылает отчет в телеграмм. 
Так же пишет логи.

Возможные сообщения:
- Работа проверена: ревьюеру всё понравилось. Ура!
- Работа взята на проверку ревьюером.
- Работа проверена: у ревьюера есть замечания.

```

## Running project/Запуск проекта

Clone repository. Install and activate virtual environment./
Клонировать репозиторий. Установить и активировать виртуальное окружение.

```
- For Mac or Linux:
$ python3 -m venv venv
$ source venv/bin/activate

- For Windows
$ python3 -m venv venv
$ source venv/Scripts/activate 
``` 

Install dependencies  from requirements.txt./
Установить зависимости из файла requirements.txt.

```
pip install -r requirements.txt
``` 
Create an .env file and add secret data to it./Создать файл .env и вписать туда секреты
```
Secrets:
- YA_TOKEN - Only for Practicum students/Только для студентов практикума
- TELEGRAM_TOKEN - Use BotFather to get telegram token/Токен дает BotFather в Telegramm
- TELEGRAM_CHAT_ID - Use UserInfoBot to get your id/UserInfoBot покажет ваш id
```
Run homework.py/Запустить homework.py
