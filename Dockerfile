
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install chromium
RUN playwright install-deps

COPY . .

EXPOSE 10000

# التعديل هنا: زدنا الوقت إلى 120 ثانية (timeout 120)
CMD ["gunicorn", "-w", "1", "--timeout", "120", "-b", "0.0.0.0:10000", "app:app"]
