FROM python:3.6.1-alpine

RUN apk update && apk add build-base zlib-dev libjpeg-turbo-dev postgresql-dev
RUN CC="cc -mavx2" pip install -U --force-reinstall pillow-simd

ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
