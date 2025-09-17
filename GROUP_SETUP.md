# 📋 Настройка бота в группе Telegram

Пошаговая инструкция по добавлению и настройке бота-модератора в группу Telegram.

## 🤖 Создание бота

### 1. Создание бота через @BotFather

1. Откройте Telegram и найдите **@BotFather**
2. Отправьте команду `/newbot`
3. Введите имя бота (например: "My Group Moderator")
4. Введите username бота (например: "my_group_moderator_bot")
5. Скопируйте полученный **BOT_TOKEN**

### 2. Настройка бота

Отправьте @BotFather следующие команды:

```
/setprivacy - Disable (отключить приватность группы)
/setjoingroups - Enable (разрешить добавление в группы)
/setdescription - "Автоматический модератор чата с системой предупреждений"
/setabouttext - "Бот для модерации, удаления нецензурной лексики и управления банами"
/setcommands - Установить команды бота
```

### 3. Команды бота

При выполнении `/setcommands` добавьте:

```
start - Активировать бота в группе
help - Показать все команды
rules - Показать правила чата
stats - Статистика модерации (админы)
admins - Список администраторов
unban - Разбанить пользователя (админы)
warnings - Предупреждения пользователя (админы)
status - Статус пользователя (админы)
search - Поиск пользователей (админы)
```

## 📱 Добавление в группу

### 1. Добавление бота

1. Откройте группу, где нужна модерация
2. Нажмите на название группы (вверху)
3. Выберите **"Управление"** или **"Edit Group"**
4. Нажмите **"Администраторы"** или **"Administrators"**
5. Нажмите **"Добавить администратора"** или **"Add Admin"**
6. Найдите вашего бота по username
7. Выберите бота и нажмите **"Добавить"**

### 2. Настройка прав администратора

**Обязательные права:**
- ✅ **"Удалять сообщения"** (Delete messages)
- ✅ **"Читать все сообщения"** (Read all messages)

**Дополнительные права (опционально):**
- ✅ **"Блокировать пользователей"** (Ban users)
- ✅ **"Добавлять новых участников"** (Add new members)
- ✅ **"Закреплять сообщения"** (Pin messages)

**Не рекомендуется:**
- ❌ **"Изменить информацию группы"** (Change group info)
- ❌ **"Удалять участников"** (Delete members)

## ⚙️ Настройка .env файла

Скопируйте токен бота в файл `.env`:

```bash
# Telegram Bot Configuration
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
BOT_ADMIN_ID=123456789

# Remote Database Configuration
DB_HOST=your-database-host.com
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE_PATH=logs/bot.log
```

## 🚀 Запуск бота

```bash
# Запуск с Docker
docker-compose up -d --build

# Проверка статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f bot
```

## ✅ Тестирование

### 1. Проверка команд

В группе отправьте:
- `/start` - бот должен ответить приветствием
- `/help` - бот должен показать справку
- `/stats` - бот должен показать статистику (только для админов)

### 2. Тестирование модерации

Отправьте тестовые сообщения:
- **"Привет всем!"** - должно остаться
- **"fuck"** - должно быть удалено
- **"блядь"** - должно быть удалено
- **"f*ck"** - должно быть удалено

### 3. Проверка логов

```bash
# Просмотр логов в реальном времени
docker-compose logs -f bot

# Проверка записей в базе данных
docker-compose exec bot python -c "
import asyncio
from app.database.repository import BotActionRepository
async def check():
    repo = BotActionRepository()
    actions = await repo.get_all_actions(limit=10)
    for action in actions:
        print(f'{action[\"timestamp\"]}: {action[\"action_type\"]}')
asyncio.run(check())
"
```

## 🔧 Устранение проблем

### Бот не отвечает в группе

**Проверьте:**
1. Бот добавлен в группу
2. У бота есть права администратора
3. Включена настройка "Read all messages"
4. В @BotFather отключена "Group Privacy"

### Бот не удаляет сообщения

**Проверьте:**
1. Бот имеет права "Delete messages"
2. Бот является администратором группы
3. Проверьте логи на ошибки

### Ошибки подключения к базе данных

**Проверьте:**
1. Правильность настроек в `.env`
2. Доступность удаленной базы данных
3. Логи бота: `docker-compose logs bot`

### Бот не видит сообщения

**Проверьте:**
1. В @BotFather: `/setprivacy` → `Disable`
2. Бот имеет права "Read all messages"
3. Перезапустите бота: `docker-compose restart bot`

## 📊 Мониторинг

### Полезные команды

```bash
# Статус контейнеров
docker-compose ps

# Логи бота
docker-compose logs --tail=50 bot

# Перезапуск бота
docker-compose restart bot

# Остановка всех сервисов
docker-compose down

# Обновление и перезапуск
docker-compose down && docker-compose up -d --build
```

### Проверка статистики

```bash
# Количество записей в базе
docker-compose exec bot python -c "
import asyncio
from app.database.repository import BotActionRepository
async def stats():
    repo = BotActionRepository()
    actions = await repo.get_all_actions(limit=1000)
    print(f'Total actions: {len(actions)}')
    deleted = len([a for a in actions if a['action_type'] == 'message_deleted'])
    received = len([a for a in actions if a['action_type'] == 'message_received'])
    print(f'Messages deleted: {deleted}')
    print(f'Messages received: {received}')
asyncio.run(stats())
"
```

## 🎯 Рекомендации

1. **Регулярно проверяйте логи** на предмет ошибок
2. **Мониторьте статистику** модерации
3. **Обновляйте список** нецензурных слов при необходимости
4. **Делайте резервные копии** базы данных
5. **Тестируйте** после обновлений

---

**Бот готов к работе! 🎉**