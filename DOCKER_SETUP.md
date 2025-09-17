# 🐳 Docker Setup для Telegram Bot Moderator

## Обновления в Docker-конфигурации

### ✅ Что было обновлено:

1. **aiogram 3.21.0** - обновлен до последней версии
2. **SQLAlchemy ORM** - полный переход на ORM вместо raw SQL
3. **Система предупреждений** - восстановлена с прогрессивными наказаниями
4. **Команды администратора** - добавлены команды разбана и управления
5. **Health Check** - обновлен для работы с новой архитектурой
6. **.dockerignore** - добавлен для оптимизации сборки
7. **Middleware** - добавлен LoggingMiddleware
8. **AdminUtils** - утилиты для проверки прав администратора

## 🚀 Запуск бота

### 1. Подготовка окружения

```bash
# Скопируйте env.example в .env и заполните переменные
cp env.example .env
```

### 2. Запуск через docker-compose (рекомендуется)

```bash
# Сборка и запуск
docker-compose up --build -d

# Просмотр логов
docker-compose logs -f bot

# Остановка
docker-compose down
```

### 3. Запуск через Docker напрямую

```bash
# Сборка образа
docker build -t tgbot_moderator:latest .

# Запуск контейнера
docker run -d \
  --name tgbot_moderator \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  tgbot_moderator:latest

# Просмотр логов
docker logs -f tgbot_moderator

# Остановка
docker stop tgbot_moderator
docker rm tgbot_moderator
```

## 🔧 Переменные окружения

Убедитесь, что в `.env` файле указаны:

```env
# Telegram Bot Configuration
BOT_TOKEN=your_bot_token_here
BOT_ADMIN_ID=your_admin_id_here

# Database Configuration
DB_HOST=your_remote_host.com
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE_PATH=logs/bot.log
```

## 📊 Мониторинг

### Health Check
Docker автоматически проверяет здоровье контейнера:
- Проверка подключения к базе данных
- Интервал: 30 секунд
- Таймаут: 10 секунд
- Количество попыток: 3

### Логи
Логи сохраняются в папку `./logs/` на хосте:
```bash
# Просмотр логов в реальном времени
tail -f logs/bot.log

# Просмотр логов через Docker
docker-compose logs -f bot
```

## 🛠️ Отладка

### Проверка статуса контейнера
```bash
docker-compose ps
```

### Вход в контейнер для отладки
```bash
docker-compose exec bot bash
```

### Проверка подключения к базе данных
```bash
docker-compose exec bot python -c "
import asyncio
from app.database.database import init_database
asyncio.run(init_database())
print('✅ Database connection successful!')
"
```

## 🔄 Обновление

### Обновление кода
```bash
# Остановить контейнер
docker-compose down

# Пересобрать образ
docker-compose up --build -d
```

### Очистка старых образов
```bash
# Удалить неиспользуемые образы
docker image prune -f

# Удалить конкретный образ
docker rmi tgbot_moderator:latest
```

## 📈 Производительность

### Оптимизации Docker:
- ✅ Используется `.dockerignore` для исключения ненужных файлов
- ✅ Многослойная сборка для кэширования
- ✅ Пользователь `app` для безопасности
- ✅ Health check для мониторинга

### Новые возможности:
- 🔧 **ORM** - более эффективные запросы к БД
- 📝 **Middleware** - централизованное логирование
- ⚡ **aiogram 3.21.0** - улучшенная производительность
- 🛡️ **Error Handling** - лучшая обработка ошибок
- ⚠️ **Система предупреждений** - прогрессивные наказания
- 🔓 **Команды разбана** - полное управление банами
- 👮 **Админ-команды** - расширенные возможности для администраторов

## 🆘 Решение проблем

### Проблема: Контейнер не запускается
```bash
# Проверить логи
docker-compose logs bot

# Проверить переменные окружения
docker-compose config
```

### Проблема: Ошибка подключения к БД
```bash
# Проверить настройки БД в .env
cat .env | grep DB_

# Проверить доступность БД
docker-compose exec bot ping your_db_host
```

### Проблема: Бот не отвечает
```bash
# Проверить токен бота
docker-compose exec bot python -c "
from app.config.settings import get_settings
settings = get_settings()
print(f'Bot token: {settings.bot.token[:10]}...')
"
```
