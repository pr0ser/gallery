FROM python:3.6.1-alpine

RUN apk update && apk add build-base zlib-dev libjpeg-turbo-dev postgresql-dev

ENV PYTHONUNBUFFERED 1
RUN mkdir /gallery
WORKDIR /gallery
ADD requirements.txt /gallery/
RUN pip install -r requirements.txt
ADD . /gallery/
