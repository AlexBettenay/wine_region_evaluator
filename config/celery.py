# This must be the first line in the file
from __future__ import absolute_import, unicode_literals

import os
from celery import Celery

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
    'example-task': {
        'task': 'config.tasks.fetch_data',  # Adjust to your actual app and task
        'schedule': 10.0,  # Run every 60 seconds
    },
}