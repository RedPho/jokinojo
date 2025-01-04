# Use the official Python image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy all files into the container
COPY . /app


# Install protobuf with retry mechanism
RUN pip install --no-cache-dir -r requirements.txt --retries 5 --timeout 30

# Expose the port the server listens on
EXPOSE 5000

# Command to run the application
CMD ["python", "server.py"]
