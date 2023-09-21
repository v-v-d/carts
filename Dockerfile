FROM python:3.11-slim

COPY requirements*.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

ADD ./src /code
ENV PYTHONPATH=/code/
WORKDIR /code
