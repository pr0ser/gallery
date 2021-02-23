FROM python:3.9-alpine3.12

ENV PYTHONUNBUFFERED 0
RUN mkdir -p /gallery/logs
WORKDIR /gallery
ADD requirements.txt /gallery/
ARG SIMD_LEVEL=avx2
RUN apk add --update --no-cache libjpeg-turbo-dev postgresql-dev gettext libffi-dev \
    && apk add --update --no-cache --virtual .build-deps build-base zlib-dev gcc musl-dev python3-dev libffi-dev openssl-dev cargo \
    && CC="cc -m$SIMD_LEVEL" pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps \
    && addgroup -S -g 1001 gallery \
    && adduser -S -u 1001 -G gallery gallery
ADD . /gallery/
RUN chmod +x *.sh && chown -R gallery:gallery /gallery/
USER gallery
