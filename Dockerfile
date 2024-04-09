FROM python:3.8.18-slim-bookworm

# RUN sed -i -e's/ main/ main contrib non-free science/g' /etc/apt/sources.list.d/debian.sources
RUN apt update -y
RUN apt install -y --no-install-recommends build-essential libgdal32 npm

WORKDIR /srv/

COPY package*.json /srv/
RUN npm install

ARG ALLOWED_HOSTS

COPY ./requirements/* /srv/requirements/
RUN pip install -r requirements/base.txt -r requirements/prod.txt

COPY . /srv

ENV DJANGO_SETTINGS_MODULE=dezede.settings.prod
ENV ELASTICSEARCH_HOST=elasticsearch
ENV ALLOWED_HOSTS=${ALLOWED_HOSTS}
CMD python manage.py runserver django:8000
