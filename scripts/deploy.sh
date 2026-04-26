#!/bin/bash
echo "🚀 Deploying trading bot..."

# Check if AWS credentials are configured
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "❌ AWS credentials not found. Please configure AWS credentials."
    echo "   Run: aws configure"
    exit 1
fi

# Deploy to AWS
echo "📦 Deploying to AWS..."
cd infrastructure

# Bootstrap CDK (first time only)
echo "🔧 Bootstrapping CDK..."
cdk bootstrap

# Deploy the stack
echo "🚀 Deploying TradingBotStack..."
cdk deploy TradingBotStack --require-approval never

echo "✅ Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Test the API: curl <API_ENDPOINT>/health"
echo "2. Monitor logs: aws logs tail /aws/lambda/TradingService --follow"
echo "3. Check CloudWatch alarms in AWS Console"
