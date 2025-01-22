# Official Python Image
FROM python:3.9-slim

# Working directory
WORKDIR /app

# Copies application code to the container
COPY . /app

# Links the code to the image in GitHub
LABEL org.opencontainers.image.source https://github.com/ewsmyth/quizme

# Installs the dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Exposed port
EXPOSE 6678

# Command to run Gunicorn WSGI server
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:6678", "wsgi:app"]