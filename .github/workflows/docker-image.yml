# Use the official Python 3.11 image as the base
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the application files to the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the application's port
EXPOSE 8000

# Define environment variables for the application
ENV DB_NAME=postgres \
    DB_USER=postgres \
    DB_PASSWORD=admin85691 \
    DB_HOST=localhost \
    SECRET_KEY=research_smith_secret_key \
    ALGORITHM=HS256 \
    ACCESS_TOKEN_EXPIRE_MINUTES=30

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
