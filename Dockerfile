FROM python:3.9-alpine


ADD . /code
WORKDIR /code

RUN pip install --upgrade pip
RUN pip install -r requirements.txt