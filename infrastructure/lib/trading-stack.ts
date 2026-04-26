import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as sns from 'aws-cdk-lib/aws-sns';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as cloudwatch from 'aws-cdk-lib/aws-cloudwatch';
import { Duration, RemovalPolicy } from 'aws-cdk-lib';
import { SqsEventSource } from 'aws-cdk-lib/aws-lambda-event-sources';

export class TradingBotStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // SNS Topics
    const tradingSignalsTopic = new sns.Topic(this, 'TradingSignalsTopic', {
      displayName: 'Trading Signals Topic',
      topicName: 'trading-signals'
    });

    const orderEventsTopic = new sns.Topic(this, 'OrderEventsTopic', {
      displayName: 'Order Events Topic',
      topicName: 'order-events'
    });

    // SQS Queues (for critical events)
    const signalsQueue = new sqs.Queue(this, 'SignalsQueue', {
      queueName: 'trading-signals-queue',
      visibilityTimeout: Duration.seconds(30),
      retentionPeriod: Duration.days(4),
      deadLetterQueue: {
        maxReceiveCount: 3,
        queue: new sqs.Queue(this, 'SignalsDLQ', {
          queueName: 'trading-signals-dlq',
          retentionPeriod: Duration.days(14)
        })
      }
    });

    const ordersQueue = new sqs.Queue(this, 'OrdersQueue', {
      queueName: 'order-events-queue',
      visibilityTimeout: Duration.seconds(30),
      retentionPeriod: Duration.days(4),
      deadLetterQueue: {
        maxReceiveCount: 3,
        queue: new sqs.Queue(this, 'OrdersDLQ', {
          queueName: 'order-events-dlq',
          retentionPeriod: Duration.days(14)
        })
      }
    });

    // DynamoDB Tables
    const positionsTable = new dynamodb.Table(this, 'PositionsTable', {
      tableName: 'trading-positions',
      partitionKey: { name: 'symbol', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'timestamp', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: RemovalPolicy.DESTROY,
      pointInTimeRecovery: true
    });

    const tradingStateTable = new dynamodb.Table(this, 'TradingStateTable', {
      tableName: 'trading-state',
      partitionKey: { name: 'key', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: RemovalPolicy.DESTROY,
      pointInTimeRecovery: true
    });

    // Secrets Manager for Schwab credentials
    const schwabSecret = new secretsmanager.Secret(this, 'SchwabSecret', {
      secretName: 'trading-bot/schwab-credentials',
      removalPolicy: RemovalPolicy.DESTROY
    });

    // Lambda Functions
    const tradingServiceLambda = this.createLambdaFunction(
      'TradingService',
      'lambda/trading_service.py',
      'Trading Service - Strategy + Trader Bot',
      {
        environment: {
          TRADING_SIGNALS_TOPIC_ARN: tradingSignalsTopic.topicArn,
          ORDER_EVENTS_TOPIC_ARN: orderEventsTopic.topicArn,
          POSITIONS_TABLE_NAME: positionsTable.tableName,
          TRADING_STATE_TABLE_NAME: tradingStateTable.tableName,
          SCHWAB_SECRET_ARN: schwabSecret.secretArn
        }
      }
    );

    const dataServiceLambda = this.createLambdaFunction(
      'DataService',
      'lambda/data_service.py',
      'Data Service - Market Data + Account Details',
      {
        environment: {
          TRADING_SIGNALS_TOPIC_ARN: tradingSignalsTopic.topicArn,
          POSITIONS_TABLE_NAME: positionsTable.tableName,
          SCHWAB_SECRET_ARN: schwabSecret.secretArn
        }
      }
    );

    const orderServiceLambda = this.createLambdaFunction(
      'OrderService',
      'lambda/order_service.py',
      'Order Service - Order Execution + Emergency Liquidation',
      {
        environment: {
          ORDER_EVENTS_TOPIC_ARN: orderEventsTopic.topicArn,
          POSITIONS_TABLE_NAME: positionsTable.tableName,
          SCHWAB_SECRET_ARN: schwabSecret.secretArn
        }
      }
    );

    const circuitBreakerLambda = this.createLambdaFunction(
      'CircuitBreaker',
      'lambda/circuit_breaker.py',
      'Circuit Breaker - Health Monitoring + Safety',
      {
        environment: {
          TRADING_SIGNALS_TOPIC_ARN: tradingSignalsTopic.topicArn,
          ORDER_EVENTS_TOPIC_ARN: orderEventsTopic.topicArn
        }
      }
    );

    // Grant permissions to Lambda functions
    positionsTable.grantReadWriteData(tradingServiceLambda);
    positionsTable.grantReadWriteData(orderServiceLambda);
    tradingStateTable.grantReadWriteData(tradingServiceLambda);
    schwabSecret.grantRead(tradingServiceLambda);
    schwabSecret.grantRead(dataServiceLambda);
    schwabSecret.grantRead(orderServiceLambda);

    // SNS Subscriptions
    tradingSignalsTopic.addSubscription(new sns.Subscription(this, 'SignalsToTradingLambda', {
      endpoint: tradingServiceLambda.functionArn,
      protocol: sns.SubscriptionProtocol.LAMBDA
    }));

    tradingSignalsTopic.addSubscription(new sns.Subscription(this, 'SignalsToOrderLambda', {
      endpoint: orderServiceLambda.functionArn,
      protocol: sns.SubscriptionProtocol.LAMBDA
    }));

    orderEventsTopic.addSubscription(new sns.Subscription(this, 'OrdersToOrderLambda', {
      endpoint: orderServiceLambda.functionArn,
      protocol: sns.SubscriptionProtocol.LAMBDA
    }));

    orderEventsTopic.addSubscription(new sns.Subscription(this, 'OrdersToTradingLambda', {
      endpoint: tradingServiceLambda.functionArn,
      protocol: sns.SubscriptionProtocol.LAMBDA
    }));

    // SQS Event Sources for Lambda
    tradingServiceLambda.addEventSource(new sqs.SqsEventSource(signalsQueue));
    orderServiceLambda.addEventSource(new sqs.SqsEventSource(ordersQueue));

    // SNS to SQS subscriptions for critical events
    tradingSignalsTopic.addSubscription(new sns.Subscription(this, 'SignalsToSignalsQueue', {
      endpoint: signalsQueue.queueArn,
      protocol: sns.SubscriptionProtocol.SQS
    }));

    orderEventsTopic.addSubscription(new sns.Subscription(this, 'OrdersToOrdersQueue', {
      endpoint: ordersQueue.queueArn,
      protocol: sns.SubscriptionProtocol.SQS
    }));

    // API Gateway for external access
    const api = new apigateway.RestApi(this, 'TradingBotApi', {
      restApiName: 'Trading Bot API',
      description: 'API for Trading Bot operations'
    });

    // API endpoints
    const tradingResource = api.root.addResource('trading');
    tradingResource.addMethod('POST', new apigateway.LambdaIntegration(tradingServiceLambda));

    const dataResource = api.root.addResource('data');
    const marketDataResource = dataResource.addResource('market');
    marketDataResource.addMethod('GET', new apigateway.LambdaIntegration(dataServiceLambda));

    const accountResource = dataResource.addResource('account');
    accountResource.addMethod('GET', new apigateway.LambdaIntegration(dataServiceLambda));

    const orderResource = api.root.addResource('order');
    orderResource.addMethod('POST', new apigateway.LambdaIntegration(orderServiceLambda));

    // Health check endpoint
    const healthResource = api.root.addResource('health');
    healthResource.addMethod('GET', new apigateway.LambdaIntegration(circuitBreakerLambda));

    // CloudWatch Alarms for monitoring
    this.createCloudWatchAlarms(tradingServiceLambda, 'TradingService');
    this.createCloudWatchAlarms(dataServiceLambda, 'DataService');
    this.createCloudWatchAlarms(orderServiceLambda, 'OrderService');
    this.createCloudWatchAlarms(circuitBreakerLambda, 'CircuitBreaker');

    // Output important values
    new cdk.CfnOutput(this, 'ApiEndpoint', {
      value: api.url,
      description: 'API Gateway endpoint URL'
    });

    new cdk.CfnOutput(this, 'TradingSignalsTopicArn', {
      value: tradingSignalsTopic.topicArn,
      description: 'Trading signals SNS topic ARN'
    });

    new cdk.CfnOutput(this, 'OrderEventsTopicArn', {
      value: orderEventsTopic.topicArn,
      description: 'Order events SNS topic ARN'
    });
  }

  private createLambdaFunction(
    id: string,
    codePath: string,
    description: string,
    environment?: { [key: string]: string }
  ): lambda.Function {
    const lambdaFunction = new lambda.Function(this, id, {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: 'lambda_handler',
      code: lambda.Code.fromAsset('../backend'),
      timeout: Duration.minutes(5),
      memorySize: 256,
      environment: environment || {},
      description: description,
      tracing: lambda.Tracing.ACTIVE,
      retryAttempts: 2
    });

    return lambdaFunction;
  }

  private createCloudWatchAlarms(lambdaFunction: lambda.Function, serviceName: string): void {
    // Error rate alarm
    new cdk.Alarm(this, `${serviceName}ErrorRateAlarm`, {
      metric: lambdaFunction.metricErrors(),
      threshold: 5,
      evaluationPeriods: 2,
      treatMissingData: cdk.TreatMissingData.NOT_BREACHING,
      alarmDescription: `${serviceName} error rate is too high`
    });

    // Throttles alarm
    new cdk.Alarm(this, `${serviceName}ThrottlesAlarm`, {
      metric: lambdaFunction.metricThrottles(),
      threshold: 5,
      evaluationPeriods: 2,
      treatMissingData: cdk.TreatMissingData.NOT_BREACHING,
      alarmDescription: `${serviceName} is being throttled`
    });

    // Duration alarm
    new cdk.Alarm(this, `${serviceName}DurationAlarm`, {
      metric: lambdaFunction.metricDuration(),
      threshold: Duration.minutes(4).toMilliseconds(),
      evaluationPeriods: 2,
      treatMissingData: cdk.TreatMissingData.NOT_BREACHING,
      alarmDescription: `${serviceName} duration is too long`
    });
  }
}
