# Сервис загрузки и модерации документов

Сервис позволяет зарегистрированным пользователям загружать документы через API.  
Администратор получает уведомление по email о новых документах и может подтверждать или отклонять их в Django admin.  
После модерации пользователь получает уведомление по email. Отправка уведомлений выполняется через Celery.

## Стек

- **Backend**: Django, Django REST Framework
- **База данных**: PostgreSQL
- **Очередь сообщений**: Celery + Redis
- **Контейнеризация**: Docker, Docker Compose
- **Документация API**: Swagger (drf-yasg)

## Запуск в Docker

1. Создайте файл `.env` в корне проекта:


2. Соберите и запустите контейнеры:

```bash
docker compose up --build
```

3. Выполните миграции и создайте суперпользователя:

```bash
docker compose run --rm web python manage.py migrate
docker compose run --rm web python manage.py createsuperuser
```

4. Откройте:

- Django admin: `http://localhost:8000/admin/`
- Swagger UI: `http://localhost:8000/swagger/`
- Redoc: `http://localhost:8000/redoc/`

## API

- `POST /api/documents/` — загрузка документа (только для аутентифицированных пользователей, multipart/form-data).
- `GET /api/documents/` — список документов текущего пользователя.
- `GET /api/documents/{id}/` — детальная информация о документе.

После создания документа:

- Администратору отправляется email-уведомление (асинхронно через Celery).
- В админке доступны действия для подтверждения и отклонения документов. После изменения статуса пользователю отправляется email.

## Тесты

Запуск тестов (локально, внутри виртуального окружения):

```bash
python -m venv venv
venv/Scripts/activate  # Windows
pip install -r requirements.txt
python manage.py test
```

Покрытие тестами настроено через стандартный `manage.py test` (можно использовать `coverage` при необходимости).


