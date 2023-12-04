import celery
import redis
import numpy as np 


if __name__ == "__main__":
    
    celery_app = celery.Celery(
        'main_celery',
        backend='redis://:Eyval@localhost:6379/1',
        broker='redis://:Eyval@localhost:6379/1',
        task_default_queue='AIWithCelery',
    )
    task = celery_app.send_task(
            'inference_model',
            queue='AIWithCelery',
            )
    result = task.get()

