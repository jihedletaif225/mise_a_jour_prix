
# Use a specific, stable base image
FROM mcr.microsoft.com/playwright/python:v1.38.0-focal

# Avoid combining commands unnecessarily. It makes debugging harder.
# Update apt repositories
RUN apt-get update

# Install system dependencies. Use --no-install-recommends to reduce image size
RUN apt-get install -y --no-install-recommends \
    libgstreamer-gl1.0-0 \
    libgstreamer-plugins-bad1.0-0 \
    libavif-dev \
    libenchant-2-2 \
    libsecret-1-0 \
    libmanette-0.2-0 \
    libgles2-mesa \
    && rm -rf /var/lib/apt/lists/* # Clean up apt cache in the same RUN command

# Install Playwright system dependencies
RUN npx playwright install-deps

# Install only Chromium browser
RUN npx playwright install chromium

# Set working directory
WORKDIR /app

# Copy only requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt # --no-cache-dir is important in Docker

# Copy the rest of your application code
COPY . .

# Set the default command to run your app
CMD ["python", "Home.py"]