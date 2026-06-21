# Используем ОФИЦИАЛЬНЫЙ образ от Microsoft Playwright
# Он уже содержит: Python, все системные зависимости для браузеров и правильные шрифты.
# Версия v1.42.0 соответствует вашей версии в requirements.txt
FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

# Создаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
# Используем httpx==0.25.2 для совместимости с supabase 2.4.0
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем только сам бинарный файл браузера Chromium
# Все системные зависимости (либы, шрифты) уже встроены в этот образ
RUN playwright install chromium

# Копируем весь код приложения
COPY . .

# Указываем порт
EXPOSE 8080

# Запуск сервера
CMD ["uvicorn", "sales_engine.main:app", "--host", "0.0.0.0", "--port", "8080"]
