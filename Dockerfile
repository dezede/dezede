FROM python:3.8.18-slim-bookworm

# RUN sed -i -e's/ main/ main contrib non-free science/g' /etc/apt/sources.list.d/debian.sources
RUN apt update -y
RUN apt install -y --no-install-recommends \
    build-essential libgdal32 npm \
    texlive-xetex fonts-linuxlibertine texlive-lang-french texlive-fonts-extra \
    ffmpeg

WORKDIR /srv/

COPY package*.json /srv/
RUN npm install

COPY ./requirements/* /srv/requirements/
RUN pip install -r requirements/base.txt -r requirements/prod.txt

COPY . /srv

ARG DOMAIN

ENV DJANGO_SETTINGS_MODULE=dezede.settings.prod
ENV ELASTICSEARCH_HOST=elasticsearch
ENV DOMAIN=${DOMAIN}
CMD gunicorn dezede.wsgi:application -b django:8000 -w 9 -t 21600
