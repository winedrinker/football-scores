import os
from typing import Any

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities import parameters
from confluent_kafka import Producer
from pydantic import ConfigDict, Field
from pydantic.dataclasses import dataclass

logger = Logger(child=True)
_KAFKA_FORWARDER_CONTEXT: None | KafkaForwarderContext = None
tracer = Tracer()

@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class KafkaForwarderContext:
    _delivery_errors: set[Any] = Field(default_factory=set)
    _producer: Producer | None = Field(default=None, init=False)

    @property
    def get_producer(self) -> Producer:
        if self._producer is None:
            logger.info("Initializing Kafka Producer")
            secrets = parameters.get_secret(os.environ['CONFLUENT_SECRET_ARN'], transform='json', max_age=300)
            self._producer = Producer({
                'bootstrap.servers': secrets['bootstrap.servers'],
                'sasl.username': secrets['sasl.username'],
                'sasl.password': secrets['sasl.password'],
                'security.protocol': 'SASL_SSL',
                'sasl.mechanisms': 'PLAIN',
                'socket.keepalive.enable': True,
                'socket.timeout.ms': 3000,
                'request.timeout.ms': 5000,
                'linger.ms': 50,
                'batch.size': 32768,
                'batch.num.messages': 1000,
                'compression.type': 'lz4',
                'acks': 1,
                'retries': 2,
                'queue.buffering.max.messages': 100000
            })
        return self._producer

    def send(self, score_event):
        with tracer.provider.in_subsegment("## KafkaProduce") as subsegment:
            subsegment.put_annotation("match_id", score_event.match_id)

            self.get_producer.produce(
                topic='football_scores',
                key=str(score_event.match_id).encode('utf-8'),
                value=score_event.model_dump_json(by_alias=True).encode('utf-8'),
                callback=self._delivery_callback(score_event.match_id)
            )

    def _delivery_callback(self, match_id):
        def report(err, msg):
            if err:
                logger.error(f"Kafka delivery failed", extra={"match_id": match_id, "error": str(err)})
                self._delivery_errors.append(str(match_id))
        return report

    @tracer.capture_method
    def finalize(self):
        if not self._producer:
            return
        
        pending = self._producer.flush(timeout=3)
        if pending > 0:
            logger.warning(f"{pending} messages not delivered")
        
        if self._delivery_errors:
            failed_ids = self._delivery_errors[:10]
            err_count = len(self._delivery_errors)
            self._delivery_errors.clear()
            self._producer = None
            raise Exception(f"{err_count} delivery failures: {failed_ids}")

@tracer.capture_method()
def get_kafka_context() -> KafkaForwarderContext:
    global _KAFKA_FORWARDER_CONTEXT
    if _KAFKA_FORWARDER_CONTEXT is None:
        _KAFKA_FORWARDER_CONTEXT = KafkaForwarderContext()
    return _KAFKA_FORWARDER_CONTEXT
