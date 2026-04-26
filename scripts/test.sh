#!/bin/bash
echo "🧪 Running tests..."

cd backend

# Install test dependencies
echo "📦 Installing test dependencies..."
pip install pytest pytest-mock boto3

# Run unit tests
echo "🔬 Running unit tests..."
python -m pytest tests/unit/ -v --tb=short

# Run integration tests
echo "🔗 Running integration tests..."
python -m pytest tests/integration/ -v --tb=short

# Run performance tests
echo "⚡ Running performance tests..."
python -m pytest tests/performance/ -v --tb=short

echo "✅ All tests complete!"
