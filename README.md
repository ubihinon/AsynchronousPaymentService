# Asynchronous Payment Service

Асинхронный сервис процессинга платежей: FastAPI, RabbitMQ (FastStream), PostgreSQL, Outbox, DLQ.

Текст тестового задания — в [TASK.md](TASK.md).

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

При ошибке обработки сообщение автоматически повторяется до **3 раз** с **экспоненциальной задержкой** через DLX-паттерн RabbitMQ (TTL-очереди + dead-letter exchange):

- 1-я повторная попытка — через 3 секунды (payment.retry.1)
- 2-я повторная попытка — через 9 секунд (payment.retry.2)
- 3-я повторная попытка — через 27 секунд (payment.retry.3)

Consumer публикует упавшее сообщение в payment.events.retry с заголовком x-retry-count; по истечении TTL сообщение возвращается в payment.events → payments.new. После исчерпания попыток сообщение отправляется в Dead Letter Queue payment.failed.

Доставка webhook повторяется отдельно, внутри consumer: до WEBHOOK_RETRY_ATTEMPTS попыток с экспоненциальной задержкой WEBHOOK_RETRY_DELAY_SECONDS × 2^n (по умолчанию 5 и 10 секунд).

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
- WEBHOOK_RETRY_DELAY_SECONDS — базовая задержка между попытками webhook, удваивается с каждой попыткой (по умолчанию 5)
- LOG_LEVEL — уровень логирования (по умолчанию error)
- DEBUG — режим отладки (по умолчанию false)
