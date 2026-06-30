# 🤖 [Название бота] — [Одна строка: что делает]

[2–3 предложения: какую боль решает, для кого, какой результат получает клиент.]

**Стек:** Python 3.11+ · aiogram 3 · SQLAlchemy (async) · SQLite · aiosqlite

> 💼 Разработано для: [название компании / ниша]
> 📅 Версия: 1.0.0

---

## Содержание

1. [Возможности](#возможности)
2. [Запуск на Windows — пошагово с нуля](#запуск-на-windows--пошагово-с-нуля)
3. [Быстрый старт (macOS / Linux)](#быстрый-старт-macos--linux)
4. [Развёртывание на сервере (production)](#развёртывание-на-сервере-production)
5. [Конфигурация](#конфигурация)
6. [Структура проекта](#структура-проекта)
7. [Схема базы данных](#схема-базы-данных)
8. [Сценарии использования](#сценарии-использования)
9. [Настройка контента](#настройка-контента)
10. [Обновление и обслуживание](#обновление-и-обслуживание)
11. [Частые проблемы](#частые-проблемы)
12. [Лицензия](#лицензия)

---

## Возможности

### Для клиентов / пользователей
- [ ] Функция 1
- [ ] Функция 2
- [ ] Функция 3

### Для администраторов
- [ ] Функция 1
- [ ] Функция 2
- [ ] Функция 3

---

## Запуск на Windows — пошагово с нуля

> Этот раздел написан для тех, кто никогда не запускал Python-программы.
> Следуйте шагам по порядку — каждый шаг описан максимально подробно.

---

### Шаг 1 — Создать бота в Telegram (5 минут)

1. Откройте Telegram и найдите бота **@BotFather** (официальный бот от Telegram).
2. Нажмите **Start** или введите `/start`.
3. Введите команду `/newbot`.
4. BotFather спросит **имя бота** — отображаемое название, например: `Поддержка МойМагазин`.
5. Затем спросит **username** (только латиница, должно заканчиваться на `bot`), например: `moy_magazin_bot`.
6. BotFather пришлёт **токен** — строка вида `7123456789:AAFxxxxxxx`. Скопируйте и сохраните.

> ⚠️ Токен — это пароль от вашего бота. Никому его не передавайте.

---

### Шаг 2 — Узнать свой Telegram ID

1. Найдите в Telegram бота **@userinfobot**.
2. Нажмите **Start**.
3. Бот пришлёт `Id: 123456789` — это ваш ID. Запишите его.

---

### Шаг 3 — Установить Python

1. Перейдите на **python.org/downloads** и скачайте Python 3.11 или новее.
2. Запустите установщик.
3. **Важно:** поставьте галочку **"Add Python to PATH"** на первом экране.
4. Нажмите **Install Now** и дождитесь завершения.

Проверка:
- Нажмите `Win + R`, введите `cmd`, нажмите Enter.
- В командной строке введите: `python --version`
- Должно появиться `Python 3.11.x` или новее.

---

### Шаг 4 — Скачать код бота

**Через браузер (проще):**
1. Откройте страницу репозитория на GitHub.
2. Нажмите **Code → Download ZIP**.
3. Распакуйте архив, переименуйте папку, переместите, например, в `C:\Bots\`.

**Через Git:**
```
git clone https://github.com/<аккаунт>/<репозиторий>.git
```

---

### Шаг 5 — Открыть папку в командной строке

1. Откройте папку бота в Проводнике Windows.
2. Кликните на адресную строку вверху (где написан путь).
3. Введите `cmd` и нажмите Enter — командная строка откроется прямо в этой папке. ✅

---

### Шаг 6 — Создать виртуальное окружение

```
python -m venv .venv
.venv\Scripts\activate
```

После активации в начале строки появится `(.venv)` — окружение активно.

> ⚠️ Если Windows не разрешает запуск скриптов, выполните в PowerShell:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` → нажмите `Y`.

---

### Шаг 7 — Установить зависимости

```
pip install -r requirements.txt
```

Дождитесь `Successfully installed ...` (1–2 минуты).

---

### Шаг 8 — Создать файл настроек

В командной строке:
```
copy .env.example .env
```

Откройте `.env` блокнотом и заполните:

```
BOT_TOKEN=7123456789:AAFxxxxxxx
ADMIN_IDS=123456789
# [другие переменные вашего бота]
```

Сохраните (`Ctrl + S`).

---

### Шаг 9 — Запустить бота

```
python main.py
```

В консоли появятся строки вида:
```
2024-01-15 10:00:00 [INFO] Starting Bot...
```

Откройте Telegram, найдите вашего бота и нажмите **Start**. 🎉

---

### Шаг 10 — Как оставить бота работать постоянно

**Временно (для теста):** просто не закрывайте окно командной строки.

**Автозапуск при старте Windows:**

Создайте файл `start_bot.bat`:
```bat
@echo off
cd /d %~dp0
call .venv\Scripts\activate
python main.py
```

Затем создайте ярлык на этот файл и поместите его в папку автозагрузки:
`Win + R` → `shell:startup` → Enter → вставьте ярлык.

> 💡 **Для постоянной работы 24/7** рекомендуется разместить бота на VPS-сервере
> (от 200–300 ₽/месяц). Инструкция ниже — в разделе [Развёртывание на сервере](#развёртывание-на-сервере-production).

---

### Таблица ошибок Windows

| Ошибка в консоли | Причина | Решение |
|---|---|---|
| `'python' is not recognized` | Python не в PATH | Переустановите Python с галочкой «Add to PATH» |
| `No module named '...'` | Зависимости не установлены | Активируйте `.venv` и выполните `pip install -r requirements.txt` |
| `BOT_TOKEN ... is required` | Файл `.env` не создан / пуст | Проверьте имя файла (`.env`, не `.env.txt`) и наличие токена |
| `Unauthorized` | Токен неверный | Скопируйте токен заново из @BotFather |
| `activate` не запускается | Политика PowerShell | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |

---

## Быстрый старт (macOS / Linux)

> Для локального запуска — тестирование и разработка.

```bash
git clone https://github.com/<аккаунт>/<репозиторий>.git
cd <репозиторий>

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# Заполните .env своим токеном и ADMIN_IDS

python main.py
```

---

## Развёртывание на сервере (production)

### Минимальные требования

| Параметр | Минимум |
|---|---|
| ОС | Ubuntu 22.04 / Debian 12 |
| CPU | 1 ядро |
| RAM | 256 МБ |
| Диск | 1 ГБ |
| Python | 3.11+ |
| Сеть | Исходящий HTTPS (443) |

---

### Шаг 1 — Подготовка сервера

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv python3-pip git
```

### Шаг 2 — Системный пользователь

```bash
sudo useradd -m -s /bin/bash botuser
sudo su - botuser
```

### Шаг 3 — Код и зависимости

```bash
git clone https://github.com/<аккаунт>/<репозиторий>.git
cd <репозиторий>

python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Шаг 4 — Конфигурация

```bash
cp .env.example .env
nano .env          # заполните переменные
chmod 600 .env     # закрыть файл от других пользователей
```

### Шаг 5 — systemd-служба

```bash
exit   # вернуться в root
sudo nano /etc/systemd/system/<имя-бота>.service
```

```ini
[Unit]
Description=[Название бота]
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/home/botuser/<репозиторий>
EnvironmentFile=/home/botuser/<репозиторий>/.env
ExecStart=/home/botuser/<репозиторий>/.venv/bin/python main.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable <имя-бота>
sudo systemctl start <имя-бота>
sudo systemctl status <имя-бота>   # проверить: должно быть active (running)
```

### Шаг 6 — Логи

```bash
sudo journalctl -u <имя-бота> -f                        # в реальном времени
sudo journalctl -u <имя-бота> --since today             # за сегодня
sudo journalctl -u <имя-бота> -p err --since "1 hour ago"  # только ошибки
```

---

### Альтернатива: Docker

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

**docker-compose.yml:**
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

В `.env` при Docker укажите путь внутри volume:
```env
DATABASE_URL=sqlite+aiosqlite:////app/data/bot.db
```

```bash
docker compose up -d
docker compose logs -f
```

---

## Конфигурация

Все настройки — через переменные окружения в файле `.env`.

| Переменная | Обязательная | По умолчанию | Описание |
|---|---|---|---|
| `BOT_TOKEN` | ✅ | — | Токен бота от @BotFather |
| `ADMIN_IDS` | ✅ | — | Telegram ID администраторов через запятую |
| `DATABASE_URL` | ❌ | `sqlite+aiosqlite:///./bot.db` | URL базы данных |
| `[ПЕРЕМЕННАЯ]` | ❌ | — | [Описание] |

**Пример `.env`:**
```env
BOT_TOKEN=7123456789:AAFxxxxxxx
ADMIN_IDS=123456789,987654321
DATABASE_URL=sqlite+aiosqlite:///./bot.db
```

---

## Структура проекта

```
<репозиторий>/
├── main.py                    # Точка входа: настройка бота и polling
├── requirements.txt           # Зависимости
├── .env.example               # Шаблон конфигурации
│
└── app/
    ├── models.py              # Модели базы данных (SQLAlchemy)
    ├── database.py            # Подключение к БД, init
    ├── seed.py                # Начальное наполнение данными
    │
    ├── handlers/
    │   ├── client.py          # Хендлеры для пользователей
    │   └── admin.py           # Хендлеры для администраторов
    │
    ├── keyboards/
    │   ├── client.py          # Клавиатуры пользовательского интерфейса
    │   └── admin.py           # Клавиатуры административной панели
    │
    ├── middlewares/
    │   ├── db.py              # Инжекция сессии БД в каждый update
    │   └── throttling.py      # Защита от флуда
    │
    └── services/
        └── [модуль].py        # Бизнес-логика и работа с БД
```

---

## Схема базы данных

```
[таблица_1]                    [таблица_2]
├── id          INTEGER PK     ├── id          INTEGER PK
├── поле_1      TEXT           ├── fk_id       INTEGER FK → таблица_1.id
├── поле_2      TEXT           ├── поле_1      TEXT
└── created_at  DATETIME       └── created_at  DATETIME
```

> Описание логики связей и ключевых полей.

---

## Сценарии использования

### Пользовательский путь

```
/start
  └─► [Шаг 1]
        └─► [Шаг 2]
              ├─► [Вариант A] → Результат A
              └─► [Вариант B] → Результат B
```

### Административный путь

```
/admin
  ├─► [Раздел 1]
  │     ├─► [Действие] → FSM: шаг 1 → шаг 2 → сохранение
  │     └─► [Удалить]
  └─► [Раздел 2]
        └─► [Просмотр / Управление]
```

---

## Настройка контента

### Через административную панель

1. Откройте бота в Telegram.
2. Введите `/admin`.
3. [Конкретные инструкции для вашего бота.]

### Сброс и повторное наполнение

```bash
sudo systemctl stop <имя-бота>
rm bot.db
sudo systemctl start <имя-бота>
```

База пересоздаётся автоматически при следующем запуске.

---

## Обновление и обслуживание

### Обновление кода

```bash
sudo su - botuser
cd <репозиторий>
git pull origin main
source .venv/bin/activate
pip install -r requirements.txt
exit
sudo systemctl restart <имя-бота>
sudo systemctl status <имя-бота>
```

### Резервная копия базы данных

```bash
cp /home/botuser/<репозиторий>/bot.db \
   /home/botuser/backup/bot_$(date +%Y%m%d_%H%M%S).db
```

Автоматический бэкап через cron:

```bash
crontab -e
```

```cron
0 3 * * * cp /home/botuser/<репозиторий>/bot.db /home/botuser/backup/bot_$(date +\%Y\%m\%d).db
```

### Быстрые команды обслуживания

```bash
sudo systemctl status <имя-бота>          # статус
sudo systemctl restart <имя-бота>         # перезапуск
sudo systemctl stop <имя-бота>            # остановка
sudo systemctl is-active <имя-бота>       # alive-check (вернёт "active" или "inactive")
```

---

## Частые проблемы

| Симптом | Вероятная причина | Решение |
|---|---|---|
| Бот не отвечает после `/start` | Telegram задержка | Подождите 10–15 сек, попробуйте снова |
| `BOT_TOKEN ... is required` | `.env` не найден или пуст | Проверьте наличие файла `.env` в корне проекта |
| `Unauthorized` (401) | Неверный токен | Пересоздайте токен в @BotFather командой `/revoke` |
| `/admin` не работает | ID не в `ADMIN_IDS` | Уточните ID через @userinfobot, добавьте в `.env`, перезапустите |
| `PermissionError` при создании БД | Нет прав на запись | `sudo chown -R botuser:botuser /home/botuser/<репозиторий>/` |
| Бот завис, не отвечает | Сетевой сбой | `sudo systemctl restart <имя-бота>` (служба перезапустится автоматически) |
| `No module named '...'` | Зависимости не установлены | `source .venv/bin/activate && pip install -r requirements.txt` |

---

## Лицензия

MIT — свободное использование, в том числе в коммерческих проектах.

---

<details>
<summary>📋 Чеклист перед сдачей клиенту</summary>

- [ ] Токен бота создан и прописан в `.env`
- [ ] ADMIN_IDS заполнен ID клиента
- [ ] База данных заполнена реальным контентом (не тестовым)
- [ ] Бот протестирован: все кнопки работают, ответы корректны
- [ ] Служба systemd настроена и запускается при старте сервера
- [ ] Автоматический бэкап настроен
- [ ] Клиент получил инструкцию по работе с `/admin`
- [ ] Клиент проверил получение уведомлений как администратор

</details>
