# Use the Playwright Python base image as a starting point
FROM mcr.microsoft.com/playwright/python:v1.38.0-focal

# Install system dependencies (libgstreamer, libavif, etc.)
RUN apt-get update && apt-get install -y \
    libgstreamer-gl1.0-0 \
    libgstreamer-plugins-bad1.0-0 \
    libavif15 \
    libenchant-2-2 \
    libsecret-1-0 \
    libmanette-0.2-0 \
    libgles2-mesa && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements.txt and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install Playwright dependencies
RUN npx playwright install-deps

# Copy the rest of your application code
COPY . /app
WORKDIR /app

# Set the default command to run your app (replace 'app.py' with your actual entry file)
CMD ["python", "Home.py"]
