# 🤖 Telegram Bot Moderator

Полнофункциональный Telegram-бот для автоматической модерации чатов с поддержкой удаления нецензурной лексики, логирования действий и статистики.

## ✨ Возможности

- **🛡️ Автоматическая модерация** - удаление сообщений с нецензурной лексикой
- **⚠️ Система предупреждений** - прогрессивные наказания (1→2→3 нарушения)
- **🚫 Автоматические блокировки** - 24ч бан → постоянный бан
- **🔓 Управление банами** - команды разбана для администраторов
- **📊 Полное логирование** - запись всех действий в PostgreSQL базу данных
- **📈 Статистика и мониторинг** - детальная статистика модерации
- **👮 Админ-команды** - управление пользователями и проверка статусов
- **🌐 Многоязычность** - поддержка русского и английского языков
- **🐳 Docker** - полная контейнеризация с docker-compose
- **⚡ Современная архитектура** - aiogram 3.21.0 + SQLAlchemy ORM

## 🏗️ Архитектура

```
app/
├── bot/           # Основной модуль бота
├── handlers/      # Обработчики сообщений и команд
├── filters/       # Фильтры (модерация контента)
├── database/      # Работа с базой данных (ORM + репозитории)
├── config/        # Конфигурация
├── logging/       # Система логирования
├── middleware/    # Middleware для логирования
└── utils/         # Утилиты (баны, админ-права)
```

## 🚀 Быстрый старт

### 1. Клонирование и настройка

```bash
git clone <repository-url>
cd tgbot_moderator
cp env.example .env
```

### 2. Настройка .env файла

```bash
# Telegram Bot Configuration
BOT_TOKEN=your_bot_token_here
BOT_ADMIN_ID=your_admin_id_here

# Remote Database Configuration
DB_HOST=your_remote_host.com
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE_PATH=logs/bot.log
```

### 3. Запуск с Docker

```bash
# Сборка и запуск
docker-compose up -d --build

# Просмотр логов
docker-compose logs -f bot

# Остановка
docker-compose down
```

### 4. Настройка бота в группе

1. Добавьте бота в группу
2. Сделайте бота администратором
3. Включите права "Удалять сообщения"
4. Протестируйте команду `/help`

## 📋 Команды бота

### Основные команды
- `/start` - Активация бота в группе
- `/help` - Справка по всем командам
- `/rules` - Показать правила чата
- `/stats` - Статистика модерации (только для админов)

### Команды для администраторов
- **🔓 `/unban [user_id]`** - Разбанить пользователя
- **📋 `/warnings [user_id]`** - Показать предупреждения пользователя
- **📊 `/status [user_id]`** - Проверить статус пользователя в чате
- **🔍 `/search [partial_id]`** - Найти пользователей по части ID
- **👥 `/admins`** - Список администраторов чата

### Система предупреждений
- **1-е нарушение:** Предупреждение
- **2-е нарушение:** Блокировка на 24 часа
- **3-е нарушение:** Постоянная блокировка

## 🛠️ Технологии

- **Python 3.11+** - основной язык
- **aiogram 3.21.0** - Telegram Bot API (обновлено)
- **PostgreSQL** - база данных
- **asyncpg 0.29.0** - асинхронный драйвер PostgreSQL
- **SQLAlchemy 2.0.25** - ORM для работы с базой данных
- **Docker** - контейнеризация
- **python-dotenv 1.0.1** - управление переменными окружения

## 📊 База данных

Бот автоматически создает таблицы через SQLAlchemy ORM:

### Таблица `bot_actions` - логирование действий
```sql
CREATE TABLE bot_actions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    chat_id BIGINT NOT NULL,
    action_type VARCHAR(50) NOT NULL,  -- 'message_received', 'message_deleted', 'admin_unban'
    message_text TEXT,
    reason VARCHAR(200),
    timestamp TIMESTAMPTZ DEFAULT NOW() NOT NULL
);
```

### Таблица `user_warnings` - система предупреждений
```sql
CREATE TABLE user_warnings (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    chat_id BIGINT NOT NULL,
    warning_count INTEGER NOT NULL DEFAULT 0,
    reason VARCHAR(200),
    admin_id BIGINT,                   -- Администратор, выдавший предупреждение
    action_type VARCHAR(50) NOT NULL,  -- 'warning', 'ban_24h', 'ban_permanent'
    ban_until TIMESTAMPTZ,             -- Время окончания бана
    is_active VARCHAR(10) NOT NULL DEFAULT 'true',
    timestamp TIMESTAMPTZ DEFAULT NOW() NOT NULL
);
```

## 🔧 Разработка

### Локальная разработка

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск бота
python main.py
```

### Тестирование

```bash
# Тест подключения к базе
docker-compose exec bot python -c "
import asyncio
from app.database.repository import BotActionRepository
repo = BotActionRepository()
print('Repository test successful')
"

# Просмотр логов
docker-compose logs --tail=50 bot
```

## 📝 Логирование

Все действия бота логируются в:
- **Файл**: `logs/bot.log`
- **База данных**: таблица `bot_actions`

Типы действий:
- `message_received` - получено сообщение
- `message_deleted` - удалено сообщение
- `start_command` - команда /start
- `help_command` - команда /help
- `stats_command` - команда /stats

## 🛡️ Модерация

Бот автоматически удаляет сообщения содержащие:
- Русскую нецензурную лексику
- Английскую нецензурную лексику
- Замаскированные слова (f*ck, б*ядь и т.д.)
- Символы и обфускацию

## 🔒 Безопасность

- Все чувствительные данные в `.env` файле
- `.env` добавлен в `.gitignore`
- Использование переменных окружения
- Логирование без сохранения токенов

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи: `docker-compose logs bot`
2. Убедитесь, что бот - администратор группы
3. Проверьте права бота на удаление сообщений
4. Проверьте подключение к базе данных

## 📄 Лицензия

MIT License - см. файл LICENSE для деталей.

## 🤝 Вклад в проект

1. Fork проекта
2. Создайте feature branch
3. Commit изменения
4. Push в branch
5. Создайте Pull Request

---

**Создано с ❤️ для автоматической модерации Telegram чатов**