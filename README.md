# Football Scores High-Performance Pipeline

An end-to-end serverless data pipeline building for high throughput and reliability.

## Architecture
- **API Gateway**: Direct integration to SQS (no Lambda overhead).
- **SQS**: Buffering and decoupling for high-load handling.
- **Lambda (Python 3.14)**: Efficient batch processing (BatchSize: 10).
- **Confluent Cloud (Kafka)**: High-performance event streaming.

## Performance Benchmarks
- **Throughput**: ~1500 RPS (Requests Per Second).
- **Average Latency**: < 60ms.
- **Optimization**: Used HTTP Connection Pooling & SQS Direct Integration.

## Deployment
`sam build && sam deploy`