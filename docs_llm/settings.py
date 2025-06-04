import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url
from chromadb.config import Settings as ChromaSettings

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "change-me")
DEBUG = os.getenv("DEBUG", "True") == "True"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_yasg",
    "app",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "docs_llm.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "docs_llm.wsgi.application"
ASGI_APPLICATION = "docs_llm.asgi.application"

DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv("POSTGRES_URL", "postgresql://postgres:2003@localhost:5432/docs_llm_db"),
        conn_max_age=600,
        ssl_require=False
    )
}

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "uploads"

AUTH_PASSWORD_VALIDATORS = []

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")

CHROMA_PERSIST_DIRECTORY = str(BASE_DIR / "vectorstore" / "chroma")
CHROMA_CLIENT_SETTINGS = ChromaSettings(
    chroma_db_impl="duckdb+parquet",
    persist_directory=CHROMA_PERSIST_DIRECTORY
)

LLAMA_MODEL_PATH = os.getenv("LLAMA_MODEL_PATH", str(BASE_DIR / "models" / "model-q4_K.gguf"))
EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL_NAME",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

HF_TOKEN = os.getenv("HF_TOKEN", "")

OFFLOAD_DIR = Path(os.getenv("OFFLOAD_DIR", BASE_DIR / "offload"))
