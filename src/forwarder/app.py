from functools import partial

from aws_lambda_powertools import Logger
from aws_lambda_powertools import Metrics
from aws_lambda_powertools import Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.batch import BatchProcessor, EventType, process_partial_response
from aws_lambda_powertools.utilities.batch.types import PartialItemFailureResponse
from aws_lambda_powertools.utilities.data_classes import SQSRecord
from aws_lambda_powertools.utilities.typing import LambdaContext

from common.domain import SportEvent
from kafka_utils import KafkaForwarderContext, get_kafka_context

app = APIGatewayRestResolver()
tracer = Tracer()
logger = Logger(service="football-forwarder")
metrics = Metrics(namespace="FootballProject", service="football-forwarder")
processor = BatchProcessor(event_type=EventType.SQS)


@tracer.capture_method
def record_handler(record: SQSRecord, context: KafkaForwarderContext = None):
    score: SportEvent = SportEvent.model_validate_json(record.body)
    logger.info(f"Processing match: {score.match_id}")
    context.send(score)
    context.get_producer.poll(0)

@tracer.capture_lambda_handler
@metrics.log_metrics(capture_cold_start_metric=True, raise_on_empty_metrics=False)
@logger.inject_lambda_context()
def lambda_handler(event: dict, context: LambdaContext) -> PartialItemFailureResponse:
    kafka_ctx: KafkaForwarderContext = get_kafka_context()
    batch_size = len(event.get('Records', []))
    metrics.add_metric(name="BatchSize", unit="Count", value=batch_size)

    batch_result: PartialItemFailureResponse = process_partial_response(
        event=event,
        context=context,
        processor=processor,
        record_handler=partial(record_handler, context=kafka_ctx)
    )

    kafka_ctx.finalize()
    
    success_count = batch_size - len(batch_result.get('batchItemFailures', []))
    metrics.add_metric(name="MessagesProcessed", unit="Count", value=success_count)

    return batch_result
