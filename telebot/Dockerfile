FROM python:3.10.6-alpine

RUN mkdir -p /usr/src/app/
WORKDIR /usr/src/app/

COPY . /usr/src/app/

RUN pip install -r requirements.txt --compile --no-cache-dir
CMD ["python3", "bot.py"] 

