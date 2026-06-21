# Используем ОФИЦИАЛЬНЫЙ образ от Microsoft Playwright
FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

# Создаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем только сам бинарный файл браузера Chromium
RUN playwright install chromium

# Копируем весь код приложения
COPY . .

# Указываем порт (для документации, Railway всё равно переопределит его через ${PORT})
EXPOSE 8000

# Запуск сервера: слушаем ПОРТ, который назначил Railway, или 8000 по умолчанию
CMD uvicorn sales_engine.main:app --host 0.0.0.0 --port ${PORT:-8000}
