FROM python:3.11-slim

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app/code

COPY ./requirements*.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

ADD ./src /app/code
WORKDIR /app/code
