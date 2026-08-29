FROM python:3.10-slim

WORKDIR /app

# نسخ المتطلبات أولاً
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي الملفات
COPY . .

# تشغيل البوت مباشرة
CMD ["python", "main.py"]
