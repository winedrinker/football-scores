from confluent_kafka import Consumer
import json


conf = {
    'bootstrap.servers': 'pkc-oxqxx9.us-east-1.aws.confluent.cloud:9092',
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'PLAIN',
    'sasl.username': 'NFVIRIKHXTZG2RIX',
    'sasl.password': 'cfltXA2no9+Za/BXwWvvZNWKgvfvKGSAbojkvnnRd2yXtPDjSumimn2UNGRJQyKg',
    'client.id': 'ccloud-python-client-254db582-2fe3-4d47-85db-609a17b7bf25',
    'group.id': 'football-scores-consumer-group',
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(conf)
consumer.subscribe(['football_scores'])

print("Waiting for goals... (Ctrl+C to stop)")


last_scores = {}

try:
    while True:
        msg = consumer.poll(1.0)

        if msg is None: continue
        if msg.error():
            print(f"Error: {msg.error()}")
            continue


        data = json.loads(msg.value().decode('utf-8'))
        match_id = data.get('matchId')
        current_score = data.get('score')
        teams = f"{data.get('teamHome')} vs {data.get('teamAway')}"


        if match_id not in last_scores or last_scores[match_id] != current_score:
            print(f"EVENT: {teams} | Match score: {current_score}")
            last_scores[match_id] = current_score

except KeyboardInterrupt:
    pass
finally:
    consumer.close()