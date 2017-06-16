FROM python:3.6.1-alpine

RUN apk update && apk add build-base zlib-dev libjpeg-turbo-dev postgresql-dev
RUN addgroup -S -g 1001 gallery && adduser -S -u 1001 -G gallery gallery
ENV PYTHONUNBUFFERED 1
RUN mkdir /gallery
WORKDIR /gallery
ADD requirements.txt /gallery/
RUN pip install -r requirements.txt
ADD . /gallery/
RUN chmod +x *.sh
RUN chown -R gallery:gallery /gallery/
USER gallery
