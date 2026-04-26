import boto3
import json
import os
import time
from typing import Dict, Any


class AWSMessagingService:
    def __init__(self, endpoint_url=None):
        # Use environment variable if available, otherwise default to localhost
        if endpoint_url is None:
            endpoint_url = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")

        self.sns = boto3.client(
            "sns", endpoint_url=endpoint_url, region_name="us-east-1"
        )
        self.sqs = boto3.client(
            "sqs", endpoint_url=endpoint_url, region_name="us-east-1"
        )
        self.dynamodb = boto3.client(
            "dynamodb", endpoint_url=endpoint_url, region_name="us-east-1"
        )

        # Create topics and queues
        self._setup_infrastructure()

    def _setup_infrastructure(self):
        """Create SNS topics and SQS queues"""
        try:
            # Trading signals topic
            self.trading_signals_topic = self.sns.create_topic(Name="trading-signals")[
                "TopicArn"
            ]

            # Order events topic
            self.order_events_topic = self.sns.create_topic(Name="order-events")[
                "TopicArn"
            ]

            # Create queues for critical events
            self.signals_queue = self.sqs.create_queue(
                QueueName="trading-signals-queue"
            )["QueueUrl"]

            self.orders_queue = self.sqs.create_queue(QueueName="order-events-queue")[
                "QueueUrl"
            ]

            # Subscribe queues to topics
            self.sns.subscribe(
                TopicArn=self.trading_signals_topic,
                Protocol="sqs",
                Endpoint=self._get_queue_arn(self.signals_queue),
            )

            self.sns.subscribe(
                TopicArn=self.order_events_topic,
                Protocol="sqs",
                Endpoint=self._get_queue_arn(self.orders_queue),
            )

            print("✅ AWS messaging infrastructure setup complete")

        except Exception as e:
            print(f"❌ Infrastructure setup error: {e}")

    def _get_queue_arn(self, queue_url):
        """Get queue ARN from queue URL"""
        try:
            response = self.sqs.get_queue_attributes(
                QueueUrl=queue_url, AttributeNames=["QueueArn"]
            )
            return response["Attributes"]["QueueArn"]
        except Exception as e:
            print(f"❌ Error getting queue ARN: {e}")
            return queue_url

    def publish_signal(self, signal_type: str, data: Dict[Any, Any]):
        """Publish trading signal"""
        message = {
            "signal_type": signal_type,
            "timestamp": str(int(time.time() * 1000)),
            "data": data,
        }

        try:
            self.sns.publish(
                TopicArn=self.trading_signals_topic, Message=json.dumps(message)
            )
            print(f"📈 Published {signal_type} signal")
        except Exception as e:
            print(f"❌ Error publishing signal: {e}")

    def publish_order_event(self, order_data: Dict[Any, Any]):
        """Publish order event"""
        message = {
            "event_type": "order_event",
            "timestamp": str(int(time.time() * 1000)),
            "data": order_data,
        }

        try:
            self.sns.publish(
                TopicArn=self.order_events_topic, Message=json.dumps(message)
            )
            print(f"💼 Published order event")
        except Exception as e:
            print(f"❌ Error publishing order event: {e}")

    def publish_market_data(self, market_data: Dict[Any, Any]):
        """Publish market data (non-critical, SNS only)"""
        message = {
            "event_type": "market_data",
            "timestamp": str(int(time.time() * 1000)),
            "data": market_data,
        }

        try:
            self.sns.publish(
                TopicArn=self.trading_signals_topic, Message=json.dumps(message)
            )
            print(f"📊 Published market data")
        except Exception as e:
            print(f"❌ Error publishing market data: {e}")

    def publish_account_data(self, account_data: Dict[Any, Any]):
        """Publish account data (non-critical, SNS only)"""
        message = {
            "event_type": "account_data",
            "timestamp": str(int(time.time() * 1000)),
            "data": account_data,
        }

        try:
            self.sns.publish(
                TopicArn=self.trading_signals_topic, Message=json.dumps(message)
            )
            print(f"🏦 Published account data")
        except Exception as e:
            print(f"❌ Error publishing account data: {e}")

    def receive_signals(self, max_messages=10, wait_time=1):
        """Receive messages from signals queue"""
        try:
            response = self.sqs.receive_message(
                QueueUrl=self.signals_queue,
                MaxNumberOfMessages=max_messages,
                WaitTimeSeconds=wait_time,
            )
            return response.get("Messages", [])
        except Exception as e:
            print(f"❌ Error receiving signals: {e}")
            return []

    def receive_orders(self, max_messages=10, wait_time=1):
        """Receive messages from orders queue"""
        try:
            response = self.sqs.receive_message(
                QueueUrl=self.orders_queue,
                MaxNumberOfMessages=max_messages,
                WaitTimeSeconds=wait_time,
            )
            return response.get("Messages", [])
        except Exception as e:
            print(f"❌ Error receiving orders: {e}")
            return []

    def delete_message(self, queue_url, receipt_handle):
        """Delete message from queue"""
        try:
            self.sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
        except Exception as e:
            print(f"❌ Error deleting message: {e}")
