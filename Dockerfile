FROM python:3.8-slim

WORKDIR /app

ADD . /app

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app/lite

CMD ["uvicorn", "app:app", "--reload", "--host", "0.0.0.0", "--port", "4242"]
