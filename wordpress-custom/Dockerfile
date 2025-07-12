FROM geodata/mapserver:latest

USER root
ENV DEBIAN_FRONTEND=noninteractive
# Install Python, pip, and system dependencies for GeoPandas
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv python3-setuptools python3-wheel \
    gdal-bin python3-gdal python3-numpy python3-pandas \
    libgdal-dev libproj-dev build-essential \
 && pip3 install --upgrade pip \
 && pip3 install --no-cache-dir cython geopandas \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

USER www-data
