# Use the official Python image.
# https://hub.docker.com/_/python
FROM python:3.9-slim-buster

# Allow statements and log messages to immediately appear in the Cloud Run logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Install production dependencies.
RUN pip install -r requirements.txt

# Run the web service on container startup. Here we use the gunicorn HTTP server
# for production.
# CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
# For simplicity with Flask's built-in server (suitable for small scale, but gunicorn is better for prod)
CMD ["python", "main.py"]
