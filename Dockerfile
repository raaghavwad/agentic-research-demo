FROM python:3.11-slim-bookworm

WORKDIR /app

# Install system dependencies
# libaio1 is often required for oracledb
RUN apt-get update && apt-get install -y \
    libaio1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose Streamlit port and Metrics port
EXPOSE 8501
EXPOSE 9464

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

# Default command runs the Streamlit UI
CMD ["streamlit", "run", "ui/streamlit_app.py", "--server.address=0.0.0.0"]
