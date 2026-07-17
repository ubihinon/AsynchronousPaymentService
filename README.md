
## Реализация

### Стек

- **FastAPI** — REST API
- **FastStream + RabbitMQ** — асинхронная обработка сообщений
- **PostgreSQL + SQLAlchemy 2.0** — хранение данных
- **Alembic** — миграции
- **Outbox pattern** — гарантированная доставка событий в брокер

### Процессы

- "api" — "uvicorn core.main:app" — REST API, принимает запросы
- "outbox_worker" — "python src/payments/outbox_worker.py" — публикует события из БД в RabbitMQ
- "consumer" — "faststream run payments.consumer:app" — обрабатывает платежи из очереди

### RabbitMQ топология

Exchanges:
- payment.events (topic) — основной exchange
- payment.events.retry (direct) — retry exchange
- payment.failed (direct) — dead letter exchange

Queues:
- payments.new — основная очередь платежей
- payment.retry.1 — первый retry, TTL 3s
- payment.retry.2 — второй retry, TTL 9s
- payment.retry.3 — третий retry, TTL 27s
- payment.failed — dead letter queue

---

## Запуск

### Требования

- Docker + Docker Compose

### 1. Переменные окружения

```bash
cp .env.template .env
```

Значения по умолчанию подходят для локального запуска.

### 2. Запуск

```bash
docker compose up --build
```

Запустятся все сервисы: postgres, rabbitmq, api, outbox_worker, consumer.

Миграции применяются автоматически при старте api. Вручную:

```bash
docker exec payment_service_app alembic upgrade head
```

### Доступные сервисы

- REST API — http://localhost:8000
- Swagger UI — http://localhost:8000/docs
- RabbitMQ Management — http://localhost:15672 (guest / guest)

---

## API

Все запросы требуют заголовок "X-API-Key".

### Создать платёж

```
POST /api/v1/payments
X-API-Key: c7e3f1a9b2d84f5e
Idempotency-Key: <уникальный ключ>
Content-Type: application/json
```

```json
{
  "price": "100.00",
  "currency": "USD",
  "description": "Оплата заказа #42",
  "meta_data": {"order_id": "42"},
  "webhook_url": "https://example.com/webhook"
}
```

Ответ 202 Accepted:

```json
{
  "payment_id": "019f6fa4-90a3-7785-a40c-03e97b1c6e37",
  "status": "PENDING",
  "created_at": "2026-07-17T10:34:43.723925+00:00"
}
```

curl:

```bash
curl -X POST http://localhost:8000/api/v1/payments \
  -H "X-API-Key: c7e3f1a9b2d84f5e" \
  -H "Idempotency-Key: order-42-attempt-1" \
  -H "Content-Type: application/json" \
  -d '{
    "price": "100.00",
    "currency": "USD",
    "description": "Оплата заказа #42",
    "meta_data": {"order_id": "42"},
    "webhook_url": "https://example.com/webhook"
  }'
```

---

### Получить платёж

```
GET /api/v1/payments/{payment_id}
X-API-Key: c7e3f1a9b2d84f5e
```

Ответ 200 OK:

```json
{
  "id": "019f6fa4-90a3-7785-a40c-03e97b1c6e37",
  "status": "SUCCEEDED",
  "price": "100.00",
  "currency": "USD",
  "description": "Оплата заказа #42",
  "meta_data": {},
  "created_at": "2026-07-17T10:34:43.723925+00:00",
  "handled_at": "2026-07-17T10:34:48.000000+00:00"
}
```

curl:

```bash
curl http://localhost:8000/api/v1/payments/019f6fa4-90a3-7785-a40c-03e97b1c6e37 \
  -H "X-API-Key: c7e3f1a9b2d84f5e"
```

---

### Идемпотентность

Повторный запрос с тем же "Idempotency-Key" вернёт тот же результат без создания нового платежа.
При конфликте (тот же ключ, другое тело запроса) — 409 Conflict.

---

## Статусы платежа

- PENDING — создан, ожидает обработки
- SUCCEEDED — успешно обработан
- FAILED — обработка завершилась ошибкой

---

## Retry механизм

При ошибке обработки сообщение автоматически повторяется до **3 раз** с задержкой **3 секунды** через DLX-паттерн RabbitMQ. После исчерпания попыток сообщение отправляется в Dead Letter Queue payment.failed.

---

## Переменные окружения

- API_KEY — ключ для аутентификации запросов (по умолчанию 123)
- DATABASE_URL — AsyncPG URL для подключения к PostgreSQL
- SYNC_DATABASE_URL — Psycopg2 URL (используется Alembic)
- RABBITMQ_HOST — хост RabbitMQ (по умолчанию rabbitmq)
- RABBITMQ_PORT — порт RabbitMQ (по умолчанию 5672)
- RABBITMQ_USER — пользователь RabbitMQ (по умолчанию guest)
- RABBITMQ_PASS — пароль RabbitMQ (по умолчанию guest)
- OUTBOX_LIMIT — кол-во событий за одну итерацию outbox worker (по умолчанию 10)
- WEBHOOK_RETRY_ATTEMPTS — кол-во попыток доставки webhook (по умолчанию 3)
- WEBHOOK_TIMEOUT_SECONDS — таймаут webhook запроса (по умолчанию 5)
- WEBHOOK_RETRY_DELAY_SECONDS — задержка между попытками webhook (по умолчанию 5)
- LOG_LEVEL — уровень логирования (по умолчанию error)
- DEBUG — режим отладки (по умолчанию false)

---

# Тестовое задание: Асинхронный сервис процессинга платежей

## Описание

Необходимо реализовать микросервис для асинхронной обработки платежей. Сервис
принимает запросы на оплату, обрабатывает их через внешний платежный шлюз
(эмуляцию) и уведомляет клиента о результате через webhook.

## Сущности

### Платеж (Payment)
 - ID платежа (уникальный идентификатор)
 - Сумма (decimal)
 - Валюта (RUB, USD, EUR)
 - Описание (строка)
 - Метаданные (JSON поле для дополнительной информации)
 - Статус (pending, succeeded, failed)
 - Idempotency key (уникальный ключ для защиты от дублей)
 - Webhook URL (для уведомления о результате)
 - Даты создания и обработки

## Функционал API
### 1. Создание платежа
**POST /api/v1/payments**
 - Заголовок: Idempotency-Key (обязательный)
 - Body: сумма, валюта, описание, метаданные, webhook_url
 - Ответ: 202 Accepted, payment_id, статус, created_at

### 2. Получение информации о платеже
**GET /api/v1/payments/{payment_id}**
 - Ответ: детальная информация о платеже

## Технические требования

### Брокер сообщений
 - При создании платежа публикуется событие в очередь payments.new
 - Один consumer:
    - Получает сообщение из очереди
    - Эмулирует обработку платежа (2-5 сек, 90% успех, 10% ошибка)
    - Обновляет статус в БД
    - Отправляет webhook уведомление на указанный URL
    - Реализует повторные попытки при ошибках отправки

### Гарантии доставки
 - Outbox pattern для гарантированной публикации событий
 - Idempotency key для защиты от дублей
 - Dead Letter Queue для сообщений, не обработанных после 3 попыток

### Аутентификация
 - Статический API ключ в заголовке X-API-Key для всех эндпоинтов

### Стек технологий
 - FastAPI + Pydantic v2
 - SQLAlchemy 2.0 (асинхронный режим)
 - PostgreSQL
 - RabbitMQ (FastStream)
 - Alembic (миграции)
 - Docker + docker-compose

### Требования к результату
1. Модели и миграции: таблицы payments и outbox
2. API эндпоинты: создание и получение платежа
3. Consumer: один обработчик, делающий всё
4. Outbox pattern: гарантированная доставка событий
5. Retry: 3 попытки с экспоненциальной задержкой
6. Dead Letter Queue: для окончательно упавших сообщений
7. Docker: compose файл с postgres, rabbitmq, api, consumer
8. Документация: README с запуском и примерами

### Критерии оценки
 - Архитектура и чистота кода
 - Корректная реализация Outbox pattern
 - Работа с RabbitMQ (очереди, обменники, DLQ)
 - Идемпотентность
 - Обработка ошибок и retry логика
 - Работоспособность Docker-окружения
