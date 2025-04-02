# Базовый образ
FROM python:3.11-slim

# Установка рабочей директории внутри контейнера
WORKDIR /app

# Копирование файлов проекта
COPY . .

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Команда для запуска приложения
CMD ["python", "main.py"]