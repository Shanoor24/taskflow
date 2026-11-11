from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from .models import Task
import time


@shared_task
def task_created_notification(task_id):
    print(f"Starting background job for Task ID: {task_id}")
    
    time.sleep(5)
    
    print(f"Background job completed for Task ID: {task_id}")

    return f"Notification processed for task {task_id}"


@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def retry_demo_task(self):
    # try:
    #     print("Attempting background operation...")
        
    #     # Simulate a temporary failure
    #     raise ConnectionError("Email service is unavailable")
    # except ConnectionError as exc:
    #     print(f"Task failed: {exc}")
    #     raise self.retry(exc=exc)
    
    try:
        print(f"Attempt number: {self.request.retries + 1}")

        if self.request.retries < 2:
            raise ConnectionError("Email service is temporarily unavailable")

        print("Email notification sent successfully!")

        return "Notification sent successfully"

    except ConnectionError as exc:
        raise self.retry(exc=exc)
    
    
@shared_task
def scheduled_cleanup_task():
    cutoff_date = timezone.now() - timedelta(days=30)
    
    
    old_tasks = Task.objects.filter(
        completed=True,
        created_at__lt=cutoff_date
    )
    
    deleted_count, _ = old_tasks.delete()
    
    print(f"Cleanup completed. Deleted {deleted_count} old tasks.")

    return f"Deleted {deleted_count} old tasks"