FROM python:3.11-slim

WORKDIR /app

COPY engine/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY engine/ .

EXPOSE 5000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "2", "--timeout", "120"]