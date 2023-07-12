# Use the official Python base image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project directory into the container
COPY . .

# Run the Python script
CMD ["python", "final.py"]
