FROM python:3.10-slim-bookworm

# Install dependencies in one layer and clean up to reduce image size
RUN apt-get update && apt-get install -y git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory and copy requirements
WORKDIR /AV_FILE_TO_LINK
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip3 install --no-cache-dir -U pip && pip3 install --no-cache-dir -U -r requirements.txt

# Copy the rest of the application
COPY . .

# Command to run the bot
CMD ["python", "bot.py"]
