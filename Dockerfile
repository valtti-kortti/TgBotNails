# Базовый образ
FROM python:3.11-slim

# Установка рабочей директории внутри контейнера
WORKDIR /app
VOLUME  "bd.sqlite3"


COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Команда для запуска приложения
CMD ["python", "main.py"]