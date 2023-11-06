# Use an official Python runtime as a parent image
FROM python:3.8

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN apt-get update && apt-get install -y libgl1-mesa-glx
RUN pip install -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME ObjectTrackingWorld

RUN chmod +x script_nova.sh
# Run app.py when the container launches
ENTRYPOINT ["/app/script_nova.sh"]