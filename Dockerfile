FROM tiangolo/meinheld-gunicorn-flask:python3.8-alpine3.11
ENV APP_MODULE='app:app'

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt