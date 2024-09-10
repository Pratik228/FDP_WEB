# Build stage
FROM python:3.10 AS builder

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    python3-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.10-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libopenblas-dev \
    liblapack-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.10 /usr/local/lib/python3.10
COPY --from=builder /usr/local/bin /usr/local/bin

# Set up the working directory
WORKDIR /app
COPY . .

# Create a non-root user
RUN useradd -m appuser

# Change ownership of the /app directory to appuser
RUN chown -R appuser:appuser /app

# Switch to appuser
USER appuser

# Expose the port and run the app
EXPOSE 8080
CMD ["streamlit", "run", "attendance.py", "--server.port", "8080", "--server.enableCORS", "false"]