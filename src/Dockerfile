# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements file to install dependencies
COPY src/requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY src/ /app/

# Copy the resources directory for the credentials
COPY resources/ /app/resources/

# Set environment variable for Google application credentials
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/resources/credentials.json

# Make port 80 available to the world outside this container
EXPOSE 80

# Run app.py when the container launches
CMD ["python", "espn_daily_box_score.py"]
