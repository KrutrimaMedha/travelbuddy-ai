# Backend Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY travel_planner_ui/server/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy travel_planner_agent package
COPY travel_planner_agent/ /travel_planner_agent/

# Copy server source code
COPY travel_planner_ui/server/ .

# Create logs directory
RUN mkdir -p logs

# Expose port (Cloud Run uses 8080)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

# Run the application (Cloud Run provides PORT env var)
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}