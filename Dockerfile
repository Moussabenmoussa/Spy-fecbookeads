FROM mcr.microsoft.com/playwright:v1.40.0-jammy

# تثبيت بايثون
RUN apt-get update && apt-get install -y python3 python3-pip

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# تثبيت متصفح Chromium فقط لتوفير المساحة
RUN playwright install chromium

COPY . .

EXPOSE 10000

CMD ["python3", "app.py"]
