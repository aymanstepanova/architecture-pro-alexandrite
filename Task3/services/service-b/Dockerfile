FROM python:3.12-slim

# Чтобы логи сразу летели в stdout/stderr
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Сначала зависимости — лучше для кеша
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Потом код
COPY app.py .

EXPOSE 8080

CMD ["uvicorn", "app:app", "--host=0.0.0.0", "--port=8080"]
