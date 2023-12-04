import celery
import redis
import numpy as np
import sys


if __name__ == "__main__":
    
    celery_app = celery.Celery(
        'main_celery',
        backend='redis://:Eyval@localhost:6379/1',
        broker='redis://:Eyval@localhost:6379/1',
        task_default_queue='AIWithCelery',
    )
    if len(sys.argv) > 1:
        number_of_calls = sys.argv[1]
        try:
            number_of_calls = int(number_of_calls)
        except ValueError:
            print('Error:: first arg must be integer <Number_Of_Calls>')
            sys.exit(1)
    else: 
        number_of_calls = 1
    g = celery.group(celery_app.signature('inference_model', queue='AIWithCelery') for _ in range(number_of_calls))
    # for _ in range(number_of_calls):

    #     task = celery_app.send_task(
    #             'inference_model',
    #             queue='AIWithCelery',
    #             )
    # result = task.get()
    task = g.apply_async()
    task.get()

