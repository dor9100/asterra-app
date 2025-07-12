FROM mapserver/mapserver:latest

USER root

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3-pip python3-venv python3-setuptools python3-wheel \
    gdal-bin python3-gdal python3-numpy python3-pandas \
    build-essential libgdal-dev libproj-dev \
 && python3 -m venv /venv \
 && /venv/bin/pip install --upgrade pip \
 && /venv/bin/pip install --no-cache-dir cython \
 && /venv/bin/pip install --no-cache-dir geopandas \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

ENV PATH="/venv/bin:$PATH"

USER 1000


CMD ["python", "-m", "http.server", "8080"]
