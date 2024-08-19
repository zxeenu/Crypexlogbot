# Use an official Python runtime as a parent image
FROM python:3.12-alpine

# Set the working directory in the container
WORKDIR /app

# Install build dependencies
RUN apk add --no-cache gcc musl-dev python3-dev

# Install any needed packages specified in requirements.txt
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Remove the requirements.txt file after installation
RUN rm /app/requirements.txt

# Run app.py when the container launches
CMD ["python3", "/app/code/main.py"]