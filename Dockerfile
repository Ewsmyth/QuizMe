# Official Python Image
FROM python:3.9-slim

# Install necessary tools
RUN apt-get update && apt-get install -y docker.io lsof

# Working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Add GitHub repository label
LABEL org.opencontainers.image.source="https://github.com/ewsmyth/quizme"

# Expose Flask app port
EXPOSE 6678

# Run the Flask app
CMD ["python", "main.py"]
