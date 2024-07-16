from __future__ import absolute_import, unicode_literals
import os, ssl
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')

app = Celery('djangoProject')

# Configure SSL options
app.conf.update(
    broker_use_ssl={
        'ssl_cert_reqs': ssl.CERT_NONE
    },
    redis_backend_use_ssl={
        'ssl_cert_reqs': ssl.CERT_NONE
    }
)

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
