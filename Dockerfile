# Указываем базовый образ
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

# Копируем requirements.txt и устанавливаем зависимости
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Копируем код приложения в контейнер
COPY ./app /app/app
