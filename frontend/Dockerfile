FROM python:3.10.12-slim-buster

RUN apt update -y && apt install git ffmpeg -y 

RUN mkdir /app && mkdir /files && mkdir /app/files

WORKDIR /app

COPY app .
COPY requirements.txt ./requirements.txt

RUN pip install -U pip && pip install -r requirements.txt

CMD [ "python3", "app.py"]
