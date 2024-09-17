# Use the official Python image as the base image
FROM python:3.9-slim

# Set the working directory inside the Docker container
WORKDIR /app

# Install necessary build tools
RUN apt-get update && apt-get install -y gcc python3-dev

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project into the container
COPY . .

# Expose port 8000 for the Django app
EXPOSE 8000

# Run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
