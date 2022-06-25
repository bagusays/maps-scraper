FROM python:3.10.5-slim-bullseye

RUN pip install selenium pika && apt update && apt-get install chromium=103.0.5060.53-1~deb11u1 -y

WORKDIR /app

RUN apt install wget unzip -y

RUN wget https://chromedriver.storage.googleapis.com/103.0.5060.53/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip

RUN ls

ADD consumer.py .

CMD ["python", "-u", "./consumer.py"] 