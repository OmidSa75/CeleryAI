# CeleryAI
Using celery framework with AI models (Documentation)

As far as we know celery uses pool executor to run worker. The executor can be events, threads or processes and the developer can choose one of them based on the workflow.
In this repository I tried to explain some kinds of situations in which I try to solve the issue in a proper way. 

# Requirements
* python==3.8.1
* requirements.txt
* Redis Server

# How it works 
There is two main file to execute, `celery_app.py` and `client_request.py`, to run the server the `celery_app.py` must be executed with the following command:
```commandline
python celery_app.py 
```
and  to run the `client_request.py` in order to send the request to the server the below line must be executed:
```commandline
python client_request.py <number of requests (int)>
```

# Documentations
In each tag/version a specific workflow is designed. See more details on releases page.  

# References
* [celery](https://github.com/celery/celery)
* [celery/celery#6036](https://github.com/celery/celery/issues/6036)
