# 🤖 Help Desk Bot — FAQ-бот для сервисных компаний

Telegram-бот для автоматизации поддержки клиентов. Отвечает на часто задаваемые вопросы, принимает обращения от клиентов и уведомляет администраторов в реальном времени.

**Стек:** Python 3.11+ · aiogram 3 · SQLAlchemy (async) · SQLite · aiosqlite

---

## Содержание

1. [Возможности](#возможности)
2. [Быстрый старт](#быстрый-старт)
3. [Развёртывание на сервере (production)](#развёртывание-на-сервере-production)
4. [Конфигурация](#конфигурация)
5. [Структура проекта](#структура-проекта)
6. [Сценарии использования](#сценарии-использования)
7. [Настройка контента](#настройка-контента)
8. [Обновление и обслуживание](#обновление-и-обслуживание)
9. [Частые проблемы](#частые-проблемы)

---

## Возможности

### Для клиентов
- Меню с категориями FAQ (инлайн-кнопки)
- Мгновенные ответы на популярные вопросы
- Форма отправки произвольного вопроса администратору
- Навигация «Назад» на каждом уровне меню

### Для администраторов
- Команда `/admin` — полная панель управления прямо в Telegram
- Добавление / удаление категорий и вопросов без правки кода
- Просмотр входящих вопросов от клиентов
- Мгновенные уведомления о новых обращениях
- Защита от флуда (throttling)

---

## Быстрый старт

> Для локального запуска (тестирование, разработка).

### 1. Получить токен бота

1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте `/newbot`, следуйте инструкциям
3. Скопируйте выданный токен вида `7123456789:AAF...`

### 2. Узнать свой Telegram ID

Откройте [@userinfobot](https://t.me/userinfobot) — он пришлёт ваш числовой ID (например, `123456789`).

### 3. Клонировать и настроить

```bash
git clone https://github.com/<ваш-аккаунт>/Help_desk_bot.git
cd Help_desk_bot

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
```

Откройте `.env` и заполните:

```env
BOT_TOKEN=7123456789:AAF...        # токен от BotFather
ADMIN_IDS=123456789                # ваш Telegram ID (через запятую для нескольких)
DATABASE_URL=sqlite+aiosqlite:///./helpdesk.db
```

### 4. Запустить

```bash
python main.py
```

Откройте бота в Telegram → `/start`. При первом запуске база данных заполняется тестовыми данными автоматически.

---

## Развёртывание на сервере (production)

### Требования к серверу

| Параметр | Минимум |
|---|---|
| ОС | Ubuntu 22.04 / Debian 12 |
| CPU | 1 ядро |
| RAM | 256 МБ |
| Диск | 1 ГБ |
| Python | 3.11+ |
| Доступ | SSH, открытый исходящий HTTPS (443) |

---

### Шаг 1 — Подготовка сервера

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv python3-pip git
```

### Шаг 2 — Создание системного пользователя

```bash
sudo useradd -m -s /bin/bash botuser
sudo su - botuser
```

### Шаг 3 — Получение кода

```bash
git clone https://github.com/<ваш-аккаунт>/Help_desk_bot.git
cd Help_desk_bot

python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Шаг 4 — Конфигурация окружения

```bash
cp .env.example .env
nano .env
```

```env
BOT_TOKEN=7123456789:AAF...
ADMIN_IDS=123456789,987654321
DATABASE_URL=sqlite+aiosqlite:////home/botuser/Help_desk_bot/helpdesk.db
```

Ограничьте права на файл с секретами:

```bash
chmod 600 .env
```

### Шаг 5 — Создание systemd-службы

Вернитесь в root-сессию:

```bash
exit   # выход из botuser
sudo nano /etc/systemd/system/helpdesk-bot.service
```

Вставьте:

```ini
[Unit]
Description=Telegram Help Desk Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/home/botuser/Help_desk_bot
EnvironmentFile=/home/botuser/Help_desk_bot/.env
ExecStart=/home/botuser/Help_desk_bot/.venv/bin/python main.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Активируйте и запустите:

```bash
sudo systemctl daemon-reload
sudo systemctl enable helpdesk-bot
sudo systemctl start helpdesk-bot
```

Проверьте статус:

```bash
sudo systemctl status helpdesk-bot
```

Должно отобразиться `active (running)`.

### Шаг 6 — Просмотр логов

```bash
# Все логи в реальном времени
sudo journalctl -u helpdesk-bot -f

# Логи за сегодня
sudo journalctl -u helpdesk-bot --since today
```

---

### Альтернатива: запуск через Docker

#### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

#### docker-compose.yml

```yaml
version: "3.9"

services:
  bot:
    build: .
    restart: always
    env_file: .env
    volumes:
      - ./data:/app/data
```

В `.env` для Docker задайте путь к БД внутри volume:

```env
DATABASE_URL=sqlite+aiosqlite:////app/data/helpdesk.db
```

Запуск:

```bash
docker compose up -d
docker compose logs -f
```

---

## Конфигурация

Все настройки задаются через переменные окружения в файле `.env`.

| Переменная | Обязательная | Описание |
|---|---|---|
| `BOT_TOKEN` | ✅ | Токен бота от @BotFather |
| `ADMIN_IDS` | ✅ | Telegram ID администраторов через запятую |
| `DATABASE_URL` | ❌ | URL базы данных (по умолчанию SQLite в текущей папке) |

**Несколько администраторов:**

```env
ADMIN_IDS=123456789,987654321,111222333
```

Все перечисленные пользователи получат доступ к `/admin` и уведомления о новых вопросах.

---

## Структура проекта

```
Help_desk_bot/
├── main.py                    # Точка входа: настройка бота и polling
├── requirements.txt
├── .env.example               # Шаблон конфигурации
│
└── app/
    ├── models.py              # Модели БД: Category, Question, UserQuestion
    ├── database.py            # Инициализация подключения к БД
    ├── seed.py                # Начальное наполнение тестовыми данными
    │
    ├── handlers/
    │   ├── client.py          # Хендлеры для клиентов (/start, FAQ, вопрос)
    │   └── admin.py           # Хендлеры для администраторов (/admin, CRUD)
    │
    ├── keyboards/
    │   ├── client.py          # Клавиатуры клиентского интерфейса
    │   └── admin.py           # Клавиатуры административной панели
    │
    ├── middlewares/
    │   ├── db.py              # Инжекция сессии БД в каждый update
    │   └── throttling.py      # Защита от флуда (1 сообщ/сек на пользователя)
    │
    └── services/
        └── faq.py             # Бизнес-логика: CRUD категорий, вопросов, обращений
```

### Схема базы данных

```
categories
├── id          INTEGER PK
├── name        TEXT
├── emoji       TEXT
└── order       INTEGER

questions
├── id          INTEGER PK
├── category_id INTEGER FK → categories.id
├── text        TEXT
├── answer      TEXT
└── order       INTEGER

user_questions
├── id          INTEGER PK
├── user_id     BIGINT
├── username    TEXT
├── first_name  TEXT
├── question_text TEXT
├── created_at  DATETIME
└── is_answered BOOLEAN
```

---

## Сценарии использования

### Клиентский путь

```
/start
  └─► Главное меню (категории)
        └─► Список вопросов категории
              ├─► Ответ на вопрос
              │     ├─► [Назад к вопросам]
              │     ├─► [Главное меню]
              │     └─► [Задать свой вопрос]
              └─► [Задать свой вопрос]
                    └─► Ввод текста → отправка → уведомление администратору
```

### Административный путь

```
/admin
  ├─► Категории
  │     ├─► [Категория] → Список вопросов
  │     │       ├─► [Вопрос] → Просмотр / Удалить
  │     │       ├─► [Добавить вопрос] → FSM: текст → ответ
  │     │       └─► [Удалить категорию]
  │     └─► [Добавить категорию] → FSM: название → эмодзи
  │
  └─► Вопросы пользователей
        └─► [Вопрос #N] → Просмотр → [Отметить отвеченным]
```

---

## Настройка контента

### Через административную панель (рекомендуется)

1. Откройте бота в Telegram
2. Введите `/admin`
3. Выберите **Категории → Добавить категорию**
4. Укажите название и эмодзи
5. Войдите в созданную категорию и добавляйте вопросы через **Добавить вопрос**

### Замена демо-данных

Тестовые данные загружаются только при первом запуске (если база пуста). Чтобы сбросить их и начать заново:

```bash
# Остановить бота
sudo systemctl stop helpdesk-bot

# Удалить базу данных
rm helpdesk.db

# Запустить снова — данные пересоздадутся
sudo systemctl start helpdesk-bot
```

После этого отредактируйте содержимое через `/admin` или напрямую измените `app/seed.py` перед первым запуском.

---

## Обновление и обслуживание

### Обновление кода

```bash
sudo su - botuser
cd Help_desk_bot

git pull origin main

source .venv/bin/activate
pip install -r requirements.txt   # на случай новых зависимостей

exit

sudo systemctl restart helpdesk-bot
sudo systemctl status helpdesk-bot
```

### Резервная копия базы данных

```bash
cp /home/botuser/Help_desk_bot/helpdesk.db \
   /home/botuser/backup/helpdesk_$(date +%Y%m%d_%H%M%S).db
```

Добавьте в cron для автоматического резервного копирования:

```bash
crontab -e
```

```cron
0 3 * * * cp /home/botuser/Help_desk_bot/helpdesk.db /home/botuser/backup/helpdesk_$(date +\%Y\%m\%d).db
```

### Мониторинг

Проверить, что бот жив:

```bash
sudo systemctl is-active helpdesk-bot
```

Проверить последние ошибки:

```bash
sudo journalctl -u helpdesk-bot -p err --since "1 hour ago"
```

---

## Частые проблемы

### Бот не отвечает сразу после запуска

Telegram иногда задерживает доставку первого сообщения на 5–10 секунд. Подождите и повторите `/start`.

### `BOT_TOKEN environment variable is required`

Файл `.env` не найден или пуст. Убедитесь, что он находится в директории запуска бота и содержит корректный `BOT_TOKEN`.

### `PermissionError` при создании базы данных

Пользователь, от которого запущен бот, не имеет прав на запись в директорию. Проверьте:

```bash
ls -la /home/botuser/Help_desk_bot/
```

И при необходимости исправьте:

```bash
sudo chown -R botuser:botuser /home/botuser/Help_desk_bot/
```

### Команда `/admin` не работает

Ваш Telegram ID не добавлен в `ADMIN_IDS`. Узнайте ID через [@userinfobot](https://t.me/userinfobot) и добавьте в `.env`, затем перезапустите бота:

```bash
sudo systemctl restart helpdesk-bot
```

### Бот перестал отвечать после долгой работы

Проверьте логи на наличие ошибок сети:

```bash
sudo journalctl -u helpdesk-bot -n 50
```

Перезапустите службу:

```bash
sudo systemctl restart helpdesk-bot
```

Служба настроена на автоматический перезапуск (`Restart=always`), поэтому в большинстве случаев восстановление происходит автоматически.

---

## Лицензия

MIT — свободное использование, в том числе в коммерческих проектах.
