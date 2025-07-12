FROM osgeo/gdal:alpine-small-latest

USER root

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apk update && apk add --no-cache \
    python3 \
    py3-pip \
    py3-numpy \
    py3-pandas \
    py3-setuptools \
    py3-wheel \
    py3-cython \
    geos-dev \
    proj-dev \
    && pip install --upgrade pip \
    && pip install --no-cache-dir geopandas \
    && rm -rf /var/cache/apk/*

USER 1000

