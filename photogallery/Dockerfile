FROM python:3.6-alpine

ENV PYTHONUNBUFFERED 1
RUN mkdir /gallery
WORKDIR /gallery
ADD requirements.txt /gallery/
RUN apk add --update --no-cache libjpeg-turbo-dev postgresql-dev \
    && apk add --update --no-cache --virtual .build-deps build-base zlib-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps \
    && addgroup -S -g 1001 gallery \
    && adduser -S -u 1001 -G gallery gallery
ADD . /gallery/
RUN chmod +x *.sh && chown -R gallery:gallery /gallery/
USER gallery
