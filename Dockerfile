# Dockerfile for helper_agent
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent/workflow directories
COPY . .

# Expose DevUI default port
EXPOSE 8080

# Run DevUI server
CMD ["devui", ".", "--port", "8080", "--host", "0.0.0.0"]
