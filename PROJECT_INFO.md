# 📋 Информация о проекте

## 🎯 Описание

**Telegram Bot Moderator** - это полнофункциональный бот для автоматической модерации Telegram чатов. Бот автоматически удаляет сообщения с нецензурной лексикой, ведет статистику модерации и логирует все действия в базу данных.

## 🏗️ Архитектура проекта

### Структура файлов

```
tgbot_moderator/
├── app/                    # Основное приложение
│   ├── bot/               # Модуль бота
│   │   ├── __init__.py
│   │   └── bot.py         # Инициализация и запуск бота
│   ├── config/            # Конфигурация
│   │   ├── __init__.py
│   │   └── settings.py    # Настройки из .env
│   ├── database/          # Работа с базой данных
│   │   ├── __init__.py
│   │   ├── database.py    # Подключение к БД
│   │   ├── models.py      # SQLAlchemy модели
│   │   └── repository.py  # Raw SQL репозиторий
│   ├── filters/           # Фильтры
│   │   ├── __init__.py
│   │   └── profanity.py   # Фильтр нецензурной лексики
│   ├── handlers/          # Обработчики
│   │   ├── __init__.py
│   │   └── messages.py    # Обработка сообщений и команд
│   ├── logging/           # Логирование
│   │   ├── __init__.py
│   │   └── logger.py      # Настройка логирования
│   └── utils/             # Утилиты
│       ├── __init__.py
│       └── helpers.py     # Вспомогательные функции
├── logs/                  # Логи приложения
│   └── bot.log
├── docker-compose.yml     # Docker Compose конфигурация
├── Dockerfile            # Docker образ
├── env.example           # Пример переменных окружения
├── GROUP_SETUP.md        # Инструкция по настройке в группе
├── main.py              # Точка входа приложения
├── PROJECT_INFO.md      # Этот файл
├── README.md            # Основная документация
└── requirements.txt     # Python зависимости
```

## 🔧 Технические детали

### Основные технологии

- **Python 3.11+** - основной язык программирования
- **aiogram 3.12.0** - асинхронная библиотека для Telegram Bot API
- **PostgreSQL** - реляционная база данных
- **asyncpg** - асинхронный драйвер PostgreSQL
- **SQLAlchemy 2.0** - ORM для совместимости
- **Docker** - контейнеризация приложения

### Архитектурные решения

1. **Асинхронная архитектура** - все операции выполняются асинхронно
2. **Raw SQL** - для обхода проблем с SQLAlchemy метаданными
3. **Модульная структура** - четкое разделение ответственности
4. **Конфигурация через .env** - безопасное хранение секретов
5. **Docker контейнеризация** - простое развертывание

### База данных

**Таблица `bot_actions`:**
```sql
CREATE TABLE bot_actions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,           -- ID пользователя Telegram
    chat_id BIGINT NOT NULL,           -- ID чата Telegram
    action_type VARCHAR(50) NOT NULL,  -- Тип действия
    message_text TEXT,                 -- Текст сообщения
    reason VARCHAR(200),               -- Причина действия
    timestamp TIMESTAMPTZ DEFAULT NOW() NOT NULL
);
```

**Типы действий:**
- `message_received` - получено сообщение
- `message_deleted` - удалено сообщение
- `start_command` - команда /start
- `help_command` - команда /help
- `stats_command` - команда /stats

## 🚀 Развертывание

### Требования

- Docker и Docker Compose
- Удаленная PostgreSQL база данных
- Telegram Bot Token от @BotFather

### Быстрый старт

1. **Клонирование:**
   ```bash
   git clone <repository-url>
   cd tgbot_moderator
   ```

2. **Настройка:**
   ```bash
   cp env.example .env
   # Отредактируйте .env файл
   ```

3. **Запуск:**
   ```bash
   docker-compose up -d --build
   ```

4. **Настройка в группе:**
   - Добавьте бота в группу
   - Сделайте администратором
   - Включите права "Удалять сообщения"

## 📊 Мониторинг

### Логи

- **Файл:** `logs/bot.log`
- **База данных:** таблица `bot_actions`
- **Docker:** `docker-compose logs -f bot`

### Команды мониторинга

```bash
# Статус контейнеров
docker-compose ps

# Логи в реальном времени
docker-compose logs -f bot

# Перезапуск бота
docker-compose restart bot

# Проверка базы данных
docker-compose exec bot python -c "
import asyncio
from app.database.repository import BotActionRepository
repo = BotActionRepository()
actions = await repo.get_all_actions(limit=10)
print(f'Total actions: {len(actions)}')
"
```

## 🛡️ Безопасность

### Меры безопасности

1. **Переменные окружения** - все секреты в .env
2. **Docker пользователь** - приложение запускается не от root
3. **Логирование** - без сохранения токенов
4. **Валидация** - проверка входных данных
5. **Обработка ошибок** - graceful handling

### Рекомендации

- Регулярно обновляйте зависимости
- Мониторьте логи на предмет ошибок
- Делайте резервные копии базы данных
- Используйте HTTPS для удаленной БД

## 🔄 Обновления

### Процесс обновления

1. **Остановка:**
   ```bash
   docker-compose down
   ```

2. **Обновление кода:**
   ```bash
   git pull origin main
   ```

3. **Пересборка:**
   ```bash
   docker-compose up -d --build
   ```

4. **Проверка:**
   ```bash
   docker-compose logs -f bot
   ```

## 📈 Производительность

### Оптимизации

- **Асинхронность** - неблокирующие операции
- **Connection pooling** - переиспользование соединений
- **Индексы БД** - быстрые запросы
- **Логирование** - минимальный overhead

### Масштабирование

- Горизонтальное масштабирование через Docker Swarm
- Load balancing для множественных инстансов
- Репликация базы данных для высокой доступности

## 🐛 Отладка

### Частые проблемы

1. **Бот не отвечает:**
   - Проверьте права администратора
   - Убедитесь, что Group Privacy отключена

2. **Ошибки БД:**
   - Проверьте настройки подключения
   - Убедитесь в доступности удаленной БД

3. **Не удаляет сообщения:**
   - Проверьте права "Delete messages"
   - Убедитесь, что бот - администратор

### Инструменты отладки

```bash
# Тест подключения к БД
docker-compose exec bot python -c "
from app.database.repository import BotActionRepository
repo = BotActionRepository()
print('DB connection OK')
"

# Тест фильтра
docker-compose exec bot python -c "
from app.filters.profanity import profanity_filter
print(profanity_filter.contains_profanity('fuck'))
"
```

## 📝 Лицензия

MIT License - свободное использование и модификация.

## 🤝 Поддержка

При возникновении проблем:

1. Проверьте логи: `docker-compose logs bot`
2. Убедитесь в правильности настроек
3. Проверьте права бота в группе
4. Создайте issue в репозитории

---

**Проект готов к продакшену! 🚀**
