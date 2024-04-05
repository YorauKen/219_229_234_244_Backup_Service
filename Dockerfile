FROM alpine:20220328
FROM python:3.10
RUN apt-get update


ENV DISPLAY=host.docker.internal:0.0


RUN pip install google-auth-oauthlib google-api-python-client google-auth-httplib2 
COPY main.py main.py 
COPY cronkube-service.json cronkube-service.json
COPY  backup-dir  backup-dir
CMD ["python","main.py"]