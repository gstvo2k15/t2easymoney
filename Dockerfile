# Base image
FROM python:3.10-slim

# Install build tools and libraries required for simpleaudio
RUN apt-get update && apt-get install -y \
    gcc \
    libasound2-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir simpleaudio numpy colorama

# Entry point
CMD ["python3", "pin_simulator.py"]
