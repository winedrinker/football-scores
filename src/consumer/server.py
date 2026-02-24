import asyncio
import json

from confluent_kafka import Consumer
from fastapi import FastAPI, WebSocket

app = FastAPI()

conf = {
    'bootstrap.servers': 'pkc-oxqxx9.us-east-1.aws.confluent.cloud:9092',
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'PLAIN',
    'sasl.username': 'NFVIRIKHXTZG2RIX',
    'sasl.password': 'cfltXA2no9+Za/BXwWvvZNWKgvfvKGSAbojkvnnRd2yXtPDjSumimn2UNGRJQyKg',
    'client.id': 'ccloud-python-client-254db582-2fe3-4d47-85db-609a17b7bf25',
    'group.id': 'football-scores-consumer-group',
    'auto.offset.reset': 'latest'
}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    consumer = Consumer(conf)
    consumer.subscribe(['football_scores'])

    try:
        while True:
            # Polling Kafka
            msg = consumer.poll(0.1)
            if msg is None:
                await asyncio.sleep(0.01)
                continue

            data = json.loads(msg.value().decode('utf-8'))
            await websocket.send_json(data)
    except Exception as e:
        print(f"Hiba: {e}")
    finally:
        consumer.close()
