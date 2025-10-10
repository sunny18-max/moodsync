FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/models data/datasets

# Expose port
EXPOSE 5000

# Run the application
CMD ["gunicorn", "app.main:app", "--bind", "0.0.0.0:5000", "--workers", "4"]