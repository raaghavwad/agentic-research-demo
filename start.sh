#!/bin/bash

# Stop existing containers
echo "Stopping existing containers..."
docker compose down

# Build and start containers in detached mode
echo "Building and starting containers..."
docker compose up -d --build

# Wait a moment for services to initialize
echo "Waiting for services to initialize..."
sleep 5

# Display URLs
echo ""
echo "========================================================"
echo "🚀 Agentic Research Demo Stack is Running!"
echo "========================================================"
echo ""
echo "📱 Streamlit App:    http://localhost:8501"
echo "📊 Grafana:          http://localhost:3000"
echo "📈 Prometheus:       http://localhost:9090"
echo "⏱️  Tempo:            http://localhost:3200"
echo ""
echo "To view logs, run: docker compose logs -f"
echo "To stop the stack, run: docker compose down"
echo "========================================================"
