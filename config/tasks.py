from celery import shared_task

@shared_task
def fetch_data():
    print("Fetching data from external API")