FROM python:3.11
ENV PYTHONUNBUFFERED 1
RUN mkdir /Bite
WORKDIR /Bite
# Installing OS Dependencies
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
libsqlite3-dev
RUN pip install -U pip setuptools
COPY requirements.txt /Bite/
COPY requirements-opt.txt /Bite/
RUN pip install -r /Bite/requirements.txt
RUN pip install -r /Bite/requirements-opt.txt
ADD . /Bite/
# Django service
EXPOSE 8000
