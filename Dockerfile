# Use an official Python image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install system dependencies for Selenium
RUN apt-get update && apt-get install -y \
    chromium-driver \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy files
COPY . .

# Expose the Flask port
EXPOSE 8080

# Run app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]