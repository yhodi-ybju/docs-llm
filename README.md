# docs-llm

**`docs-llm`** — это система для загрузки и индексации PDF-документов, интеллектуального поиска по их содержимому и получения ответов на вопросы с помощью локальной большой языковой модели.

## Стек технологий

* **Язык программирования:** Python 3.11
* **Фреймворк:** Django 5.2 + Django REST Framework
* **Асинхронные задачи:** Celery 5.5 + Redis
* **Векторное хранилище:** Chroma
* **LLM:** `IlyaGusev/saiga_mistral_7b_lora` (через LlamaCpp)
* **База данных:** PostgreSQL
* **Контейнеризация:** Docker + Docker Compose

## Установка и запуск

### 1. Клонирование репозитория

```bash
git clone https://github.com/yhodi-ybju/docs-llm.git
cd docs-llm
```

### 2. Создание виртуального окружения

**Linux/macOS:**

```bash
python -m venv venv
source venv/bin/activate
```

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate.bat
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка `.env` файла

Создайте файл `.env` в корне проекта и добавьте:

```
DJANGO_SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

POSTGRES_URL=postgresql://postgres:2003@localhost:5432/docs_llm_db
CELERY_BROKER_URL=redis://localhost:6379/0

CHROMA_PERSIST_DIR=app/vectorstore/chroma
LLAMA_MODEL_PATH=models/model-q4_K.gguf
EMBEDDING_MODEL_NAME=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
OFFLOAD_DIR=app/offload

TELEGRAM_TOKEN=your_telegram_bot_token
```

### 5. Инициализация базы данных

Убедитесь, что база `docs_llm_db` создана и PostgreSQL запущен. Затем выполните миграции:

```bash
python manage.py migrate
```

### 6. Загрузка модели

Скачайте модель `gguf` от IlyaGusev в директорию `models/`:

```bash
wget https://huggingface.co/IlyaGusev/saiga_mistral_7b_gguf/resolve/main/model-q4_K.gguf -P models/
```

### 7. Запуск Redis

Если Redis не установлен https://timeweb.cloud/tutorials/redis/ustanovka-i-nastrojka-redis-dlya-raznyh-os

Запуск:

```bash
redis-server
```

### 8. Запуск Celery

В новом терминале:

```bash
celery -A docs_llm worker --loglevel=info --pool=solo
```

### 9. Запуск Django

```bash
python manage.py runserver
```

### 10. Проверка

Перейдите в браузере по адресу:

```
http://localhost:8000/swagger/
```

## Telegram-бот

### 1. Создание бота

Откройте Telegram и найдите `@BotFather`. Отправьте команду:

```
/newbot
```

Задайте:

* **Name** — отображаемое имя (например: `Docs LLM Assistant`)
* **Username** — уникальное имя, заканчивающееся на `bot` (например: `docs_llm_bot`)

Скопируйте выданный токен.

### 2. Добавление токена в `.env`

```
TELEGRAM_TOKEN=123456789:ABCdefGhIJKlmnoPQRstuVWXyz
```

### 3. Запуск бота

```bash
python bot.py
```
