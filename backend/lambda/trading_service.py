import json
import boto3
import numpy as np
import time
from aws_messaging import AWSMessagingService

class TradingService:
    def __init__(self):
        self.messaging = AWSMessagingService()
        self.fast_period = 10
        self.slow_period = 20
        self.positions = {}
        self.fast_period_value = None
        self.slow_period_value = None
        self.closes = []
        self.running = True
        
    def _calculate_ema(self, data, period):
        """Calculate EMA using numpy"""
        alpha = 2 / (period + 1)
        ema = np.zeros_like(data)
        ema[0] = data[0]
        for i in range(1, len(data)):
            ema[i] = alpha * data[i] + (1 - alpha) * ema[i-1]
        return ema
    
    def _update_ema_values(self, close_price):
        """Update EMA values with new price data"""
        self.closes.append(close_price)
        
        # Keep only last 100 data points
        if len(self.closes) > 100:
            self.closes = self.closes[-100:]
        
        # Calculate EMAs
        if len(self.closes) >= self.slow_period:
            closes_array = np.array(self.closes)
            self.slow_period_value = self._calculate_ema(closes_array, self.slow_period)[-1]
            
        if len(self.closes) >= self.fast_period:
            closes_array = np.array(self.closes)
            self.fast_period_value = self._calculate_ema(closes_array, self.fast_period)[-1]
    
    def _generate_signal(self, data):
        """Generate trading signal based on EMA crossover"""
        if self.fast_period_value is None or self.slow_period_value is None:
            return None
        
        symbol = data.get('symbol', 'SPY')
        close_price = data.get('close')
        current_position = self.positions.get(symbol, 0)
        
        # Entry signals
        if current_position == 0:
            if close_price > self.fast_period_value and self.fast_period_value > self.slow_period_value:
                return {
                    'type': 'BULL_ENTRY_SIGNAL',
                    'data': {
                        'symbol': symbol,
                        'current_price': close_price,
                        'fast_ema': self.fast_period_value,
                        'slow_ema': self.slow_period_value,
                        'conditions': {
                            'most_recent_candle_close': close_price,
                            'fast_period_value': self.fast_period_value,
                            'slow_period_value': self.slow_period_value,
                            'chart_time': data.get('timestamp', str(int(time.time() * 1000)))
                        }
                    }
                }
            elif close_price < self.fast_period_value and self.fast_period_value < self.slow_period_value:
                return {
                    'type': 'BEAR_ENTRY_SIGNAL',
                    'data': {
                        'symbol': symbol,
                        'current_price': close_price,
                        'fast_ema': self.fast_period_value,
                        'slow_ema': self.slow_period_value,
                        'conditions': {
                            'most_recent_candle_close': close_price,
                            'fast_period_value': self.fast_period_value,
                            'slow_period_value': self.slow_period_value,
                            'chart_time': data.get('timestamp', str(int(time.time() * 1000)))
                        }
                    }
                }
        
        # Exit signals
        elif current_position > 0:  # Long position
            if close_price < self.fast_period_value:
                return {
                    'type': 'BULL_EXIT_SIGNAL',
                    'data': {
                        'symbol': symbol,
                        'current_price': close_price,
                        'fast_ema': self.fast_period_value,
                        'slow_ema': self.slow_period_value,
                        'current_position': current_position,
                        'conditions': {
                            'most_recent_candle_close': close_price,
                            'fast_period_value': self.fast_period_value,
                            'slow_period_value': self.slow_period_value,
                            'chart_time': data.get('timestamp', str(int(time.time() * 1000)))
                        }
                    }
                }
        elif current_position < 0:  # Short position
            if close_price > self.fast_period_value:
                return {
                    'type': 'BEAR_EXIT_SIGNAL',
                    'data': {
                        'symbol': symbol,
                        'current_price': close_price,
                        'fast_ema': self.fast_period_value,
                        'slow_ema': self.slow_period_value,
                        'current_position': current_position,
                        'conditions': {
                            'most_recent_candle_close': close_price,
                            'fast_period_value': self.fast_period_value,
                            'slow_period_value': self.slow_period_value,
                            'chart_time': data.get('timestamp', str(int(time.time() * 1000)))
                        }
                    }
                }
        
        return None
    
    def _create_order_from_signal(self, signal):
        """Create order from trading signal"""
        signal_type = signal['type']
        data = signal['data']
        symbol = data['symbol']
        current_price = data['current_price']
        
        # Calculate position size (simple fixed size for now)
        position_size = 10  # 10 shares
        
        if 'ENTRY' in signal_type:
            if 'BULL' in signal_type:
                return {
                    'symbol': symbol,
                    'side': 'BUY',
                    'quantity': position_size,
                    'type': 'MARKET',
                    'price': current_price,
                    'signal_type': signal_type
                }
            else:  # BEAR
                return {
                    'symbol': symbol,
                    'side': 'SELL',
                    'quantity': position_size,
                    'type': 'MARKET',
                    'price': current_price,
                    'signal_type': signal_type
                }
        elif 'EXIT' in signal_type:
            current_position = data.get('current_position', 0)
            return {
                'symbol': symbol,
                'side': 'SELL' if current_position > 0 else 'BUY',
                'quantity': abs(current_position),
                'type': 'MARKET',
                'price': current_price,
                'signal_type': signal_type
            }
        
        return None
    
    def _update_position(self, order):
        """Update position after order execution"""
        symbol = order['symbol']
        side = order['side']
        quantity = order['quantity']
        
        if symbol not in self.positions:
            self.positions[symbol] = 0
        
        if side == 'BUY':
            self.positions[symbol] += quantity
        else:  # SELL
            self.positions[symbol] -= quantity

def lambda_handler(event, context):
    """Trading Service Lambda - Strategy + Trader Bot"""
    service = TradingService()
    
    print("🚀 Trading Service Lambda started")
    
    # Process incoming messages
    for record in event['Records']:
        if record['eventSource'] == 'aws:sqs':
            message = json.loads(record['body'])
            data = message.get('data', {})
            
            print(f"📨 Processing message: {data}")
            
            # Handle different message types
            if message.get('event_type') == 'market_data':
                # Update EMA calculations with market data
                if 'close' in data:
                    service._update_ema_values(float(data['close']))
                    
                    # Generate trading signal
                    signal = service._generate_signal(data)
                    
                    if signal:
                        print(f"📈 Generated signal: {signal['type']}")
                        
                        # Publish signal
                        service.messaging.publish_signal(signal['type'], signal['data'])
                        
                        # Create and publish order
                        order = service._create_order_from_signal(signal)
                        if order:
                            print(f"💼 Created order: {order}")
                            service.messaging.publish_order_event(order)
                            
                            # Update position (simulate execution)
                            service._update_position(order)
                            print(f"📊 Updated position: {service.positions}")
            
            elif message.get('event_type') == 'signal':
                # Handle signal events (if needed)
                pass
    
    return {
        'statusCode': 200, 
        'body': json.dumps({
            'message': 'Trading signals processed',
            'positions': service.positions,
            'ema_values': {
                'fast': service.fast_period_value,
                'slow': service.slow_period_value
            }
        })
    }

if __name__ == "__main__":
    # Test locally
    test_event = {
        'Records': [
            {
                'eventSource': 'aws:sqs',
                'body': json.dumps({
                    'event_type': 'market_data',
                    'data': {
                        'symbol': 'SPY',
                        'close': 150.5,
                        'timestamp': str(int(time.time() * 1000))
                    }
                })
            }
        ]
    }
    
    result = lambda_handler(test_event, None)
    print(f"Result: {result}")
