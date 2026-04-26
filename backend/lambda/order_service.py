import json
import boto3
import time
from aws_messaging import AWSMessagingService
from clients.schwab_client import get_client

class OrderService:
    def __init__(self):
        self.messaging = AWSMessagingService()
        self.client = get_client()
        self.positions = {}
        self.running = True
        
    def _execute_order(self, order_data):
        """Execute order through Schwab API"""
        try:
            symbol = order_data.get('symbol')
            side = order_data.get('side')
            quantity = order_data.get('quantity')
            order_type = order_data.get('type', 'MARKET')
            price = order_data.get('price')
            
            print(f"💼 Executing {side} order for {quantity} shares of {symbol} at ${price}")
            
            # Create order payload for Schwab API
            order_payload = {
                "orderType": order_type,
                "session": "NORMAL",
                "duration": "DAY",
                "orderStrategyType": "SINGLE",
                "orderLegCollections": [
                    {
                        "instruction": side,
                        "quantity": quantity,
                        "instrument": {
                            "symbol": symbol,
                            "assetType": "EQUITY"
                        }
                    }
                ]
            }
            
            # For MARKET orders, we don't need price
            if order_type == "MARKET":
                order_payload["orderLegCollections"][0]["instruction"] = side
                order_payload["orderLegCollections"][0]["quantity"] = quantity
            else:
                order_payload["price"] = price
            
            # Place order (simulate for now)
            # In real implementation, you would call:
            # response = self.client.place_order(order_payload)
            
            # Simulate order execution
            order_id = f"order_{int(time.time())}"
            status = "FILLED"
            filled_quantity = quantity
            filled_price = price
            
            result = {
                'order_id': order_id,
                'symbol': symbol,
                'side': side,
                'quantity': filled_quantity,
                'type': order_type,
                'status': status,
                'filled_price': filled_price,
                'timestamp': str(int(time.time() * 1000))
            }
            
            print(f"✅ Order executed: {result}")
            return result
            
        except Exception as e:
            print(f"❌ Error executing order: {e}")
            return {
                'error': str(e),
                'status': 'FAILED',
                'timestamp': str(int(time.time() * 1000))
            }
    
    def _emergency_liquidate_all_positions(self):
        """Emergency liquidation - close all positions"""
        try:
            print("🚨 EMERGENCY LIQUIDATION TRIGGERED")
            
            # Get current positions (simulate)
            # In real implementation, you would fetch from Schwab API
            current_positions = {
                'SPY': 10,  # Example position
                'QQQ': -5   # Example short position
            }
            
            liquidation_results = []
            
            for symbol, quantity in current_positions.items():
                if quantity != 0:
                    # Create market order to close position
                    side = 'SELL' if quantity > 0 else 'BUY'
                    abs_quantity = abs(quantity)
                    
                    order_data = {
                        'symbol': symbol,
                        'side': side,
                        'quantity': abs_quantity,
                        'type': 'MARKET',
                        'emergency_liquidation': True
                    }
                    
                    result = self._execute_order(order_data)
                    liquidation_results.append(result)
                    
                    # Update positions
                    self.positions[symbol] = 0
            
            print(f"🚨 Emergency liquidation completed: {len(liquidation_results)} orders")
            
            return {
                'status': 'COMPLETED',
                'orders_executed': len(liquidation_results),
                'results': liquidation_results,
                'timestamp': str(int(time.time() * 1000))
            }
            
        except Exception as e:
            print(f"❌ Emergency liquidation failed: {e}")
            return {
                'status': 'FAILED',
                'error': str(e),
                'timestamp': str(int(time.time() * 1000))
            }
    
    def _get_all_positions(self):
        """Get all current positions"""
        try:
            # In real implementation, fetch from Schwab API
            # For now, return simulated positions
            return {
                'SPY': 10,
                'QQQ': -5,
                'VTI': 0
            }
        except Exception as e:
            print(f"❌ Error getting positions: {e}")
            return {}
    
    def _update_positions(self, order_result):
        """Update positions after order execution"""
        try:
            symbol = order_result.get('symbol')
            side = order_result.get('side')
            quantity = order_result.get('quantity')
            status = order_result.get('status')
            
            if status == 'FILLED':
                if symbol not in self.positions:
                    self.positions[symbol] = 0
                
                if side == 'BUY':
                    self.positions[symbol] += quantity
                else:  # SELL
                    self.positions[symbol] -= quantity
                
                print(f"📊 Updated {symbol} position: {self.positions[symbol]}")
            
        except Exception as e:
            print(f"❌ Error updating positions: {e}")

def lambda_handler(event, context):
    """Order Service Lambda - Order Execution + Emergency Liquidation"""
    service = OrderService()
    
    print("🚀 Order Service Lambda started")
    
    # Process order events
    for record in event['Records']:
        if record['eventSource'] == 'aws:sqs':
            message = json.loads(record['body'])
            order_data = message.get('data', {})
            
            print(f"📨 Processing order: {order_data}")
            
            if order_data.get('emergency_liquidation'):
                # Emergency liquidation - close all positions
                print("🚨 Triggering emergency liquidation")
                result = service._emergency_liquidate_all_positions()
                
                # Publish emergency liquidation result
                service.messaging.publish_order_event({
                    'event_type': 'emergency_liquidation',
                    'result': result
                })
                
            else:
                # Normal order execution
                result = service._execute_order(order_data)
                
                if result.get('status') == 'FILLED':
                    # Update positions
                    service._update_positions(result)
                    
                    # Publish order result
                    service.messaging.publish_order_event({
                        'event_type': 'order_filled',
                        'order_data': order_data,
                        'result': result
                    })
                else:
                    # Publish order failure
                    service.messaging.publish_order_event({
                        'event_type': 'order_failed',
                        'order_data': order_data,
                        'result': result
                    })
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Orders processed',
            'current_positions': service.positions
        })
    }

if __name__ == "__main__":
    # Test locally
    test_event = {
        'Records': [
            {
                'eventSource': 'aws:sqs',
                'body': json.dumps({
                    'data': {
                        'symbol': 'SPY',
                        'side': 'BUY',
                        'quantity': 10,
                        'type': 'MARKET',
                        'price': 150.5
                    }
                })
            }
        ]
    }
    
    result = lambda_handler(test_event, None)
    print(f"Result: {result}")
