#!/bin/bash
echo "🚀 Setting up LocalStack trading bot..."

# Start LocalStack
echo "📦 Starting LocalStack..."
docker-compose -f docker-compose.localstack.yml up -d

# Wait for LocalStack to be ready
echo "⏳ Waiting for LocalStack to be ready..."
sleep 15

# Test LocalStack
echo "🔍 Testing LocalStack services..."
awslocal sns list-topics
awslocal sqs list-queues
awslocal dynamodb list-tables

echo "✅ Setup complete!"
echo "📊 LocalStack is running at http://localhost:4566"
echo "🖥️  LocalStack UI: http://localhost:8080"
echo ""
echo "Next steps:"
echo "1. Test Lambda functions: docker-compose -f docker-compose.localstack.yml logs -f"
echo "2. Run tests: ./scripts/test.sh"
echo "3. Deploy to AWS when ready: cd infrastructure && cdk deploy"
