FROM python:3.10-slim-bookworm

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    gcc \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory and copy requirements
WORKDIR /AV_FILE_TO_LINK
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip3 install --no-cache-dir -U pip && pip3 install --no-cache-dir -U -r requirements.txt

# Copy application files
COPY . .

# Expose ports
EXPOSE 2626 10000 8080

# Command to run the bot
CMD ["python", "bot.py"]
