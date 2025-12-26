# استخدام صورة تحتوي على Playwright مسبقاً (الأقوى والأسهل)
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# إعداد مجلد العمل
WORKDIR /app

# نسخ ملف المتطلبات وتثبيتها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# تثبيت المتصفحات الضرورية
RUN playwright install chromium
RUN playwright install-deps

# نسخ باقي ملفات المشروع
COPY . .

# فتح المنفذ
EXPOSE 10000

# أمر التشغيل (باستخدام Gunicorn)
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:10000", "app:app"]
