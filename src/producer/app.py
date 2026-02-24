import os
from typing import TYPE_CHECKING

import boto3
from aws_lambda_powertools import Logger, Metrics
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.parser import parse
from aws_lambda_powertools.utilities.typing import LambdaContext

if TYPE_CHECKING:
    from mypy_boto3_sqs import SQSClient

from common.domain import SportEvent
from errors import handle_api_errors

app = APIGatewayRestResolver()
logger = Logger(service="football-producer")
metrics = Metrics(namespace="FootballProject", service="football-producer")
sqs: SQSClient = boto3.client('sqs')
QUEUE_URL = os.environ['SQS_QUEUE_URL']


@app.post("/scores")
@handle_api_errors
def handle_scores():
    score: SportEvent = parse(event=app.current_event.json_body, model=SportEvent)
    logger.info(f'Score received: {score}')

    sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=score.model_dump_json(by_alias=True)
    )

    logger.info(f"Match {score.match_id} queued to SQS")
    return {"status": "Accepted", "matchId": score.match_id}, 202


@metrics.log_metrics(capture_cold_start_metric=True, raise_on_empty_metrics=False)
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
