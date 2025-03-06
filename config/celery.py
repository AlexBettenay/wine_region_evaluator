# This must be the first line in the file
from __future__ import absolute_import, unicode_literals

import os
from celery import Celery
from celery.signals import worker_ready
from celery.schedules import crontab

# Set the default Django settings module 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('wine_region_evaluator')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs
app.autodiscover_tasks()

# Define periodic tasks
app.conf.beat_schedule = {
    'fetch_data_task': {
        'task': 'config.tasks.fetch_data',  # Adjust to your actual app and task
        'schedule': crontab(minute=1, hour=0), # Fetch new data just after midnight to get full data for previous day
    },
}

# Execute task on worker startup
@worker_ready.connect
def at_start(sender, **k):
    from config.tasks import fetch_data
    fetch_data.delay()