# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    firefox-esr \
    xvfb \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Download geckodriver for Firefox (adjust version if needed)
RUN curl -L https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux64.tar.gz | tar xz -C /usr/bin/

# Set up a virtual X server (Xvfb)
ENV DISPLAY=:99
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=UTF-8

# Install Python dependencies
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Define environment variable
ENV NAME World

# Run script.py when the container launches
CMD Xvfb :99 -screen 0 1024x768x16 & \
    sleep 2 && \
    python script.py
