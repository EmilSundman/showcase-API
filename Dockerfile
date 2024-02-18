# Use the official Python image as the base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install uv
RUN pip install -r requirements.txt

# Copy the current directory contents into the container at /app
COPY app/ .

# Command to run the API
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
