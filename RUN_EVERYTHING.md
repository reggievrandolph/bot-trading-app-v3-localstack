# 🚀 How to Run Everything Together

## Quick Start (One Command)

### Option 1: LocalStack + AWS Services (Recommended)
```bash
./scripts/setup.sh && cd simple-frontend && npm start
```

### Option 2: Make Commands (Alternative)
```bash
make simulated && cd simple-frontend && npm start
```

## Detailed Steps

### 1. Start Backend Services
```bash
# LocalStack with AWS services (SNS/SQS/DynamoDB)
./scripts/setup.sh

# OR use make commands
make simulated
```

### 2. Start Frontend
```bash
cd simple-frontend
npm start
# Opens at http://localhost:3000
```

### 3. Verify Everything is Running
```bash
# Check LocalStack services
docker-compose -f docker-compose.localstack.yml ps

# Check frontend
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000
# Should return 200

# Check LocalStack health
curl http://localhost:4566/_localstack/health
```

## Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:3000 | Trading Dashboard |
| **LocalStack UI** | http://localhost:8080 | AWS Services Console |
| **LocalStack API** | http://localhost:4566 | AWS API Endpoint |

## Monitor Activity

### Watch All Services
```bash
docker-compose -f docker-compose.localstack.yml logs -f
```

### Watch Specific Service
```bash
# Trading activity
docker-compose -f docker-compose.localstack.yml logs -f trading-service

# Order execution
docker-compose -f docker-compose.localstack.yml logs -f order-service

# Health monitoring
docker-compose -f docker-compose.localstack.yml logs -f circuit-breaker
```

## Stop Everything

```bash
# Stop LocalStack services
docker-compose -f docker-compose.localstack.yml down

# Stop frontend (Ctrl+C in terminal)
```

## Architecture Overview

```
Frontend (React) → LocalStack (AWS Services) → Lambda Functions
     ↓                    ↓                        ↓
  Dashboard            SNS/SQS                 Trading Logic
  http://3000          Messaging              Order Execution
                       DynamoDB               Health Monitoring
```

## Troubleshooting

### Frontend Not Starting
```bash
cd simple-frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

### Services Not Running
```bash
# Restart LocalStack
docker-compose -f docker-compose.localstack.yml restart

# Check logs
docker-compose -f docker-compose.localstack.yml logs
```

### Port Conflicts
```bash
# Check what's using ports
lsof -ti:3000  # Frontend
lsof -ti:4566  # LocalStack
lsof -ti:8080  # LocalStack UI

# Kill process if needed
kill -9 $(lsof -ti:3000)
```

## Environment Setup

Make sure you have:
```bash
# Python environment
source .venv/bin/activate

# Node.js (for frontend)
node --version  # Should be 16+
npm --version   # Should be 8+

# Docker
docker --version
docker-compose --version
```

## What You'll See

1. **Frontend Dashboard**: Real-time trading data, positions, service status
2. **LocalStack Console**: AWS services (SNS topics, SQS queues, DynamoDB tables)
3. **Terminal Logs**: Trading activity, order execution, health checks

## Success Indicators

✅ Frontend loads at http://localhost:3000  
✅ LocalStack UI accessible at http://localhost:8080  
✅ All 4 Lambda services are healthy  
✅ Trading signals processing  
✅ Orders executing and updating positions  

That's it! Your trading bot is fully operational with AWS services architecture.
