# какой образ мы используем
FROM python:3.11-slim

# настройка рабочей директории в нутри контейнера
WORKDIR /app

# что нужно перенести полностью в наш контейнер
COPY requirements.txt .

# устанавливаем зависимости (RUN - запускает операцию)
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
 
# открываем порт для работы FastAPI
EXPOSE 8000

# выполнение при старте контейнера (CMD)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
