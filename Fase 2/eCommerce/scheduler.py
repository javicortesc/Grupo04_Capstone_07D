# scheduler.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conejofurioso.settings')
django.setup()

import schedule
import time
from datetime import timedelta
from app.models import Product
from django.utils import timezone

def update_product_status():
    threshold_date = timezone.now() - timedelta(days=7)
    Product.objects.filter(created_at__lt=threshold_date, new=True).update(new=False)

# Programar la ejecución de la función cada 24 horas a las 9:00 AM
schedule.every().day.at("04:00").do(update_product_status)

while True:
    schedule.run_pending()
    time.sleep(1)