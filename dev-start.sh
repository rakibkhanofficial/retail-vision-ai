#!/bin/bash

echo "🚀 Retail Vision AI - Development Mode"
echo "======================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your GEMINI_API_KEY"
    echo "   Get your key from: https://makersuite.google.com/app/apikey"
    echo ""
    read -p "Press Enter after you've added your API key to .env..."
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running!"
    echo "   Please start Docker Desktop and try again."
    exit 1
fi

echo "✅ Docker is running"
echo ""
echo "🔨 Starting development containers..."
echo "   This will start:"
echo "   - PostgreSQL database on port 5432"
echo "   - Backend API with hot reload on port 8000" 
echo "   - Frontend on port 3000"
echo ""
echo "📝 Running in foreground (press Ctrl+C to stop)"
echo ""

# Build and start in foreground for development
docker compose up --build