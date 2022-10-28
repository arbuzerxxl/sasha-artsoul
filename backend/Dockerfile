FROM python:3.10.6-alpine

RUN mkdir -p /usr/src/app/
WORKDIR /usr/src/app/

COPY . /usr/src/app/

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

RUN pip install -r requirements.txt --compile --no-cache-dir

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]


