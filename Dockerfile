FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the hpqc source code package
COPY hpqc/ hpqc/

# Expose the gRPC port used by the QC server
EXPOSE 50051

# Run the server, binding to all interfaces so it's accessible from outside the container
CMD ["python", "-m", "hpqc.qc.server", "--host", "0.0.0.0", "--port", "50051"]
