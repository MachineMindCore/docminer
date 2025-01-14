# Use an official Python runtime as a base image
FROM python:3.10.11

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8080 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP="docminer/app.py"

# Run the application
CMD ["python", "docminer/app.py"]