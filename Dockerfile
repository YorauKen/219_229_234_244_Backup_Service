FROM alpine:20220328
FROM python:3.10
RUN apt-get update


ENV DISPLAY=host.docker.internal:0.0

WORKDIR /main

RUN pip install google-auth-oauthlib google-api-python-client google-auth-httplib2 

COPY . /main/

CMD ["python","mainc.py"]