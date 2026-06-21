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

# Указываем порт
EXPOSE 8000

# САМЫЙ НАДЕЖНЫЙ СПОСОБ ЗАПУСКА:
# Используем shell-форму, чтобы переменная ${PORT} была раскрыта Railway перед запуском uvicorn
CMD ["sh", "-c", "uvicorn sales_engine.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
