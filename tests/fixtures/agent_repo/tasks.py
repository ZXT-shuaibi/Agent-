from celery import Celery


celery_app = Celery("agent")


@celery_app.task(bind=True, autoretry_for=(TimeoutError,), retry_backoff=True, max_retries=3)
def run_long_task(self, task_id: str) -> str:
    return task_id
