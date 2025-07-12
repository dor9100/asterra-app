FROM ghcr.io/osgeo/gdal:ubuntu-small-latest

USER root

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    python3-venv \
    python3-pip \
    python3-numpy \
    python3-pandas \
    python3-setuptools \
    python3-wheel \
    cython3 \
    libgeos-dev \
    libproj-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /venv \
    && /venv/bin/pip install --upgrade pip \
    && /venv/bin/pip install --no-cache-dir geopandas

ENV PATH="/venv/bin:$PATH"

USER 1000
