FROM python:3.9.1-slim-buster

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

CMD ["python3", "app.py"]
