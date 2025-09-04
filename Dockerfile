# Use Python 3.9 slim image for smaller size
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    unzip \
    ca-certificates \
    fonts-liberation \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libgtk-3-0 \
    xdg-utils \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Install Google Chrome and ChromeDriver
RUN wget -q -O /tmp/google-chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get update && apt-get install -y /tmp/google-chrome.deb chromium-driver unzip curl && \
    rm /tmp/google-chrome.deb && \
    chmod +x /usr/bin/chromedriver

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create downloads directory with proper permissions
RUN mkdir -p /app/downloads && chmod 755 /app/downloads

# Create non-root user for security
RUN useradd -m -u 1000 scraper && chown -R scraper:scraper /app
USER scraper

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Run the application
CMD ["python", "app.py"]

