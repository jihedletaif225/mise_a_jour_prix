
FROM mcr.microsoft.com/playwright/python:v1.38.0-focal

RUN apt-get update # Keep this for consistent builds

RUN npx playwright install-deps
RUN npx playwright install chromium

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "Home.py"]