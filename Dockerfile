FROM python:3.9.1-slim-buster

COPY . /app

WORKDIR /app

RUN python3 install -r requirements.txt

CMD ["python3", "app.py"]
