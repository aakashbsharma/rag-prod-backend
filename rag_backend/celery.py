import os
from dotenv import load_dotenv
from celery import Celery
load_dotenv()

# Configure Celery with Upstash Redis
UPSTASH_REDIS_HOST = os.getenv("UPSTASH_REDIS_HOST")
UPSTASH_REDIS_PORT = os.getenv("UPSTASH_REDIS_PORT")
UPSTASH_REDIS_PASSWORD = os.getenv("UPSTASH_REDIS_PASSWORD")

connection_link = f"rediss://default:{UPSTASH_REDIS_PASSWORD}@{UPSTASH_REDIS_HOST}:{UPSTASH_REDIS_PORT}?ssl_cert_reqs=required"

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rag_backend.settings")

app = Celery("rag_backend", broker=connection_link, backend=connection_link)

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
