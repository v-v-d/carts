FROM python:3.11-slim

COPY ./requirements*.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

ADD ./src /app/code
WORKDIR /app/code
