# Use an official lightweight Python image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the server code into the container
COPY . .

# Install any dependencies (if needed)
# RUN pip install -r requirements.txt  # Uncomment if you have a requirements file

# Expose the server port (make sure this matches your server's port)
EXPOSE 5000

# Run the server
CMD ["python3", "server.py"]
