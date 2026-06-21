# Используем официальный легкий образ Python
FROM python:3.12-slim

# Создаем рабочую директорию
WORKDIR /app

# Устанавливаем базовые инструменты, которые могут понадобиться для установки зависимостей
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости БЕЗ КЕША
RUN pip install --no-cache-dir -r requirements.txt

# 1. Устанавливаем сам браузер Chromium
RUN playwright install chromium

# 2. ОФИЦИАЛЬНЫЙ МЕТОД: Устанавливаем все системные зависимости для этого браузера
# Эта команда сама найдет и поставит все те самые libx11, libgbm и прочие .so файлы
RUN playwright install-deps chromium

# Копируем весь код приложения
COPY . .

# Указываем порт
EXPOSE 8080

# Запуск сервера
CMD ["uvicorn", "sales_engine.main:app", "--host", "0.0.0.0", "--port", "8080"]
