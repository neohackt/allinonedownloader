# Lightweight Python + ffmpeg image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port Render provides
EXPOSE 10000

# Start gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]
