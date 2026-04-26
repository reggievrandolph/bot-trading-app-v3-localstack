import json
import boto3
import time
from aws_messaging import AWSMessagingService

class CircuitBreaker:
    def __init__(self):
        self.messaging = AWSMessagingService()
        self.failure_counts = {}
        self.last_heartbeat = {}
        self.circuit_states = {}  # CLOSED, OPEN, HALF_OPEN
        self.failure_threshold = 5
        self.timeout = 60  # seconds
        self.heartbeat_timeout = 30  # seconds
        self.services = ['trading-service', 'data-service', 'order-service']
        
        # Initialize circuit states
        for service in self.services:
            self.circuit_states[service] = "CLOSED"
            self.failure_counts[service] = 0
            self.last_heartbeat[service] = time.time()
    
    def _check_all_services_health(self):
        """Check health of all services"""
        health_status = {
            'timestamp': str(int(time.time() * 1000)),
            'services': {},
            'critical_failures': [],
            'overall_status': 'HEALTHY'
        }
        
        current_time = time.time()
        
        for service in self.services:
            service_health = {
                'state': self.circuit_states[service],
                'failure_count': self.failure_counts[service],
                'last_heartbeat': self.last_heartbeat[service],
                'time_since_heartbeat': current_time - self.last_heartbeat[service],
                'status': 'healthy'
            }
            
            # Check if service is unhealthy
            if service_health['time_since_heartbeat'] > self.heartbeat_timeout:
                service_health['status'] = 'unhealthy'
                health_status['critical_failures'].append(service)
                health_status['overall_status'] = 'DEGRADED'
            
            # Check circuit breaker state
            if self.circuit_states[service] == "OPEN":
                service_health['status'] = 'circuit_open'
                if current_time - self.last_heartbeat[service] < self.timeout:
                    health_status['critical_failures'].append(service)
                    health_status['overall_status'] = 'DEGRADED'
            
            health_status['services'][service] = service_health
        
        return health_status
    
    def _trigger_emergency_stop(self):
        """Trigger emergency stop for all services"""
        try:
            print("🚨 TRIGGERING EMERGENCY STOP")
            
            # Publish emergency stop event
            emergency_event = {
                'event_type': 'emergency_stop',
                'timestamp': str(int(time.time() * 1000)),
                'reason': 'Circuit breaker triggered - critical service failures',
                'services_affected': self.services
            }
            
            self.messaging.publish_order_event(emergency_event)
            print("🚨 Emergency stop event published")
            
        except Exception as e:
            print(f"❌ Error triggering emergency stop: {e}")
    
    def _emergency_liquidate_positions(self):
        """Trigger emergency position liquidation"""
        try:
            print("🚨 TRIGGERING EMERGENCY LIQUIDATION")
            
            # Send emergency liquidation command to order service
            liquidation_command = {
                'task': 'emergency_liquidation',
                'data': {
                    'emergency': True,
                    'reason': 'Circuit breaker triggered',
                    'timestamp': str(int(time.time() * 1000))
                }
            }
            
            self.messaging.publish_order_event(liquidation_command)
            print("🚨 Emergency liquidation command sent")
            
        except Exception as e:
            print(f"❌ Error triggering emergency liquidation: {e}")
    
    def _update_circuit_states(self, health_status):
        """Update circuit breaker states based on health status"""
        current_time = time.time()
        
        for service in self.services:
            service_health = health_status['services'][service]
            
            # Handle OPEN circuit timeout
            if self.circuit_states[service] == "OPEN":
                if current_time - self.last_heartbeat[service] > self.timeout:
                    self.circuit_states[service] = "HALF_OPEN"
                    self.failure_counts[service] = 0
                    print(f"🔄 Circuit {service} moved to HALF_OPEN")
            
            # Handle service failures
            if service_health['status'] == 'unhealthy':
                self.failure_counts[service] += 1
                
                if self.failure_counts[service] >= self.failure_threshold:
                    self.circuit_states[service] = "OPEN"
                    self.last_heartbeat[service] = current_time
                    print(f"🚨 Circuit {service} OPENED due to failures")
            
            # Handle healthy services
            elif service_health['status'] == 'healthy':
                if self.circuit_states[service] == "HALF_OPEN":
                    self.circuit_states[service] = "CLOSED"
                    self.failure_counts[service] = 0
                    print(f"✅ Circuit {service} CLOSED after successful test")
    
    def _record_heartbeat(self, service_name):
        """Record heartbeat from service"""
        self.last_heartbeat[service_name] = time.time()
        
        # Reset failure count on successful heartbeat
        if self.failure_counts[service_name] > 0:
            self.failure_counts[service_name] = max(0, self.failure_counts[service_name] - 1)
    
    def _handle_service_failure(self, service_name, error):
        """Handle service failure"""
        self.failure_counts[service_name] += 1
        print(f"❌ Service {service_name} failure: {error}")
        
        if self.failure_counts[service_name] >= self.failure_threshold:
            self.circuit_states[service_name] = "OPEN"
            self.last_heartbeat[service_name] = time.time()
            print(f"🚨 Circuit {service_name} OPENED")

def lambda_handler(event, context):
    """Circuit Breaker Lambda - Health Monitoring + Safety"""
    breaker = CircuitBreaker()
    
    print("🚀 Circuit Breaker Lambda started")
    
    # Check system health
    health_status = breaker._check_all_services_health()
    print(f"📊 Health check: {health_status['overall_status']}")
    
    # Trigger emergency actions if needed
    if health_status['critical_failures']:
        print(f"🚨 Critical failures detected: {health_status['critical_failures']}")
        breaker._trigger_emergency_stop()
        breaker._emergency_liquidate_positions()
    
    # Update circuit breaker states
    breaker._update_circuit_states(health_status)
    
    # Handle incoming messages (heartbeats, failure reports)
    for record in event['Records']:
        if record['eventSource'] == 'aws:sqs':
            message = json.loads(record['body'])
            message_type = message.get('type')
            service_name = message.get('service')
            
            if message_type == 'heartbeat':
                breaker._record_heartbeat(service_name)
                print(f"💓 Heartbeat received from {service_name}")
            
            elif message_type == 'failure':
                error = message.get('error', 'Unknown error')
                breaker._handle_service_failure(service_name, error)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Circuit breaker check completed',
            'health_status': health_status,
            'circuit_states': breaker.circuit_states
        })
    }

if __name__ == "__main__":
    # Test locally
    test_event = {
        'Records': [
            {
                'eventSource': 'aws:sqs',
                'body': json.dumps({
                    'type': 'heartbeat',
                    'service': 'trading-service'
                })
            }
        ]
    }
    
    result = lambda_handler(test_event, None)
    print(f"Result: {result}")
