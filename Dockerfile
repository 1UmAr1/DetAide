# Use the official Python image as the base image
FROM python:3.10-slim as builder

# Add author metadata
LABEL maintainer="Umar Hajam <umerayoub54@gmail.com>"

ENV HOME=/app
WORKDIR $HOME

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install pip requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Multi-stage build: Create a clean final image
FROM python:3.10-slim as final

ENV HOME=/app
WORKDIR $HOME

# Copy only the necessary artifacts from the builder stage
# Here we need to make sure that the entire Python environment including installed packages is copied
COPY --from=builder /usr/local /usr/local
COPY --from=builder /app /app

# Add any application files required
COPY . .

# Expose the port on which your FastAPI service will run
EXPOSE 8080

# Command to run your FastAPI application using Uvicorn
CMD ["uvicorn", "application.api:app", "--host", "0.0.0.0", "--port", "8080"]
