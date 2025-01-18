# Official Python Image
FROM python:3.9-slim

# Working directory
WORKDIR /app

# Copies application code to the container
COPY . /app

LABEL org.opencontainers.image.source https://github.com/ewsmyth/quizme

# Installs the dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Exposed port
EXPOSE 6678

# Runs the Flask app
CMD ["python", "main.py"]