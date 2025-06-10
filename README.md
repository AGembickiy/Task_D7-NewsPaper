# NewsPaper Project

## Описание проекта
NewsPaper - это новостной портал, разработанный на Django. Проект позволяет пользователям создавать и просматривать новости и статьи, комментировать их, подписываться на категории и получать уведомления о новых публикациях.

## Основные функции
- Регистрация и авторизация пользователей
- Создание и редактирование статей и новостей
- Комментирование публикаций
- Рейтинговая система для авторов, статей и комментариев
- Подписка на категории новостей
- Email-уведомления о новых публикациях
- Интеграция с Google для авторизации
- Система логирования

## Система логирования
Проект включает в себя настроенную систему логирования со следующими компонентами:

### Консольное логирование (DEBUG = True)
- Все сообщения уровня DEBUG и выше
- Формат: время, уровень, сообщение
- Для WARNING и выше: дополнительно путь к источнику
- Для ERROR и CRITICAL: дополнительно стек ошибки

### Файл general.log (DEBUG = False)
- Сообщения уровня INFO и выше
- Формат: время, уровень, модуль, сообщение
- Логгер: django

### Файл errors.log
- Сообщения уровня ERROR и CRITICAL
- Формат: время, уровень, сообщение, путь, стек ошибки
- Логгеры: django.request, django.server, django.template, django.db_backends

### Файл security.log
- Сообщения безопасности
- Формат: время, уровень, модуль, сообщение
- Логгер: django.security

### Почтовые уведомления (DEBUG = False)
- Сообщения уровня ERROR и выше
- Формат: время, уровень, сообщение, путь
- Логгеры: django.request, django.server

## Технологии
- Python 3.12
- Django 5.1.1
- django-allauth
- django-filter
- django-crispy-forms
- Pillow
- SQLite3

## Установка и запуск
1. Клонировать репозиторий:
```bash
git clone git@github.com:AGembickiy/Task_D7-NewsPaper.git
```

2. Создать виртуальное окружение и активировать его:
```bash
python -m venv .venv
source .venv/bin/activate  # для Linux/Mac
# или
.venv\Scripts\activate  # для Windows
```

3. Установить зависимости:
```bash
pip install -r NewsPaper/requirements.txt
```

4. Применить миграции:
```bash
cd NewsPaper
python manage.py migrate
```

5. Создать суперпользователя:
```bash
python manage.py createsuperuser
```

6. Запустить сервер:
```bash
python manage.py runserver
```

## Структура проекта
```
NewsPaper/
├── news/                  # Основное приложение
│   ├── models.py         # Модели данных
│   ├── views.py          # Представления
│   ├── urls.py           # URL-маршруты
│   └── tests.py          # Тесты
├── templates/            # HTML шаблоны
├── static/              # Статические файлы
├── logs/                # Лог-файлы
└── manage.py            # Скрипт управления Django
```

## Автор
AGembickiy
