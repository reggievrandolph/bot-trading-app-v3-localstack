import json
import boto3
import time
from aws_messaging import AWSMessagingService
from clients.schwab_client import get_client

class DataService:
    def __init__(self):
        self.messaging = AWSMessagingService()
        self.client = get_client()
        self.account_hash = None
        self.running = True
        
    def _fetch_market_data(self):
        """Fetch market data from Schwab API"""
        try:
            # Get price history for SPY
            resp = self.client.price_history(
                symbol="SPY",
                periodType="day",
                period=1,
                frequencyType="minute",
                frequency=1,
                needExtendedHoursData=False,
                needPreviousClose=False,
            )
            
            if resp.status_code == 200:
                data = resp.json()
                candles = data.get('candles', [])
                
                if candles:
                    # Get the most recent candle
                    latest_candle = candles[-1]
                    
                    market_data = {
                        'symbol': 'SPY',
                        'open': latest_candle.get('open'),
                        'high': latest_candle.get('high'),
                        'low': latest_candle.get('low'),
                        'close': latest_candle.get('close'),
                        'volume': latest_candle.get('volume'),
                        'timestamp': str(latest_candle.get('datetime')),
                        'chart_time': str(latest_candle.get('datetime'))
                    }
                    
                    print(f"📊 Fetched market data: {market_data['close']}")
                    return market_data
            else:
                print(f"❌ Error fetching market data: {resp.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Exception fetching market data: {e}")
            return None
    
    def _fetch_account_details(self):
        """Fetch account details from Schwab API"""
        try:
            if not self.account_hash:
                # Get account hash
                accounts_resp = self.client.linked_accounts()
                if accounts_resp.status_code == 200:
                    accounts = accounts_resp.json()
                    if accounts:
                        self.account_hash = accounts[0]["hashValue"]
                        print(f"🏦 Account hash: {self.account_hash}")
                    else:
                        print("❌ No accounts found")
                        return None
                else:
                    print(f"❌ Error getting accounts: {accounts_resp.status_code}")
                    return None
            
            # Get account details
            details_resp = self.client.account_details(self.account_hash)
            if details_resp.status_code == 200:
                details = details_resp.json()
                account_data = {
                    'account_hash': self.account_hash,
                    'cash_balance': details['securitiesAccount']['initialBalances']['cashBalance'],
                    'available_funds': details['securitiesAccount']['initialBalances'].get('availableFunds', 0),
                    'timestamp': str(int(time.time() * 1000))
                }
                
                print(f"🏦 Account balance: ${account_data['cash_balance']}")
                return account_data
            else:
                print(f"❌ Error getting account details: {details_resp.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Exception fetching account details: {e}")
            return None
    
    def _stream_market_data(self):
        """Stream market data continuously"""
        while self.running:
            try:
                market_data = self._fetch_market_data()
                if market_data:
                    self.messaging.publish_market_data(market_data)
                
                # Wait before next fetch (1 minute)
                time.sleep(60)
                
            except Exception as e:
                print(f"❌ Error in market data stream: {e}")
                time.sleep(10)
    
    def _stream_account_data(self):
        """Stream account data periodically"""
        while self.running:
            try:
                account_data = self._fetch_account_details()
                if account_data:
                    self.messaging.publish_account_data(account_data)
                
                # Wait before next fetch (5 minutes)
                time.sleep(300)
                
            except Exception as e:
                print(f"❌ Error in account data stream: {e}")
                time.sleep(30)

def lambda_handler(event, context):
    """Data Service Lambda - Market Data + Account Details"""
    service = DataService()
    
    print("🚀 Data Service Lambda started")
    
    # Handle different data sources
    for record in event['Records']:
        if record['eventSource'] == 'aws:sqs':
            message = json.loads(record['body'])
            task = message.get('task')
            data = message.get('data', {})
            
            print(f"📨 Processing task: {task}")
            
            if task == 'market_data':
                # Fetch and publish market data
                market_data = service._fetch_market_data()
                if market_data:
                    service.messaging.publish_market_data(market_data)
                    print(f"📊 Published market data for {market_data['symbol']}")
                
            elif task == 'account_details':
                # Fetch and publish account details
                account_data = service._fetch_account_details()
                if account_data:
                    service.messaging.publish_account_data(account_data)
                    print(f"🏦 Published account data")
            
            elif task == 'stream_market_data':
                # Start streaming market data (for continuous operation)
                print("🔄 Starting market data stream...")
                service._stream_market_data()
            
            elif task == 'stream_account_data':
                # Start streaming account data (for continuous operation)
                print("🔄 Starting account data stream...")
                service._stream_account_data()
            
            else:
                print(f"⚠️ Unknown task: {task}")
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Data service completed',
            'account_hash': service.account_hash
        })
    }

if __name__ == "__main__":
    # Test locally
    test_event = {
        'Records': [
            {
                'eventSource': 'aws:sqs',
                'body': json.dumps({
                    'task': 'market_data',
                    'data': {'symbol': 'SPY'}
                })
            }
        ]
    }
    
    result = lambda_handler(test_event, None)
    print(f"Result: {result}")
