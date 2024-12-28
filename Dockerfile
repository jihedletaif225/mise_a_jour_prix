
FROM mcr.microsoft.com/playwright/python:v1.38.0-focal

# Install system dependencies needed for Node.js and other tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        gnupg \
        && rm -rf /var/lib/apt/lists/*

# Install Node.js using the NodeSource repository (LTS version recommended)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - # Use a recent LTS version (e.g., 20.x)
RUN apt-get update && apt-get install -y --no-install-recommends nodejs && rm -rf /var/lib/apt/lists/*

# Install Playwright dependencies (now npx is available)
RUN npx playwright install-deps
RUN npx playwright install chromium

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "Home.py"]