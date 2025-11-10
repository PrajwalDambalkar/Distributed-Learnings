"""
Response Consumer - Listens to agent responses
"""
import json
from kafka import KafkaConsumer
from dotenv import load_dotenv
import os

load_dotenv()

class ResponseConsumer:
    def __init__(self):
        self.bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        self.topic = os.getenv('KAFKA_TOPIC_RESPONSES', 'agent_responses')
        
        self.consumer = KafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='response-consumer-group'
        )
        
        print(f"Response Consumer connected to Kafka at {self.bootstrap_servers}")
    
    def start(self):
        """Start listening for responses"""
        print(f"\n=== Listening for Agent Responses ===\n")
        
        try:
            for message in self.consumer:
                response = message.value
                self.display_response(response)
                
        except KeyboardInterrupt:
            print("\nResponse Consumer shutting down...")
        finally:
            self.consumer.close()
    
    def display_response(self, response):
        """Display response in formatted way"""
        print(f"\n{'='*60}")
        print(f"Agent: {response.get('agent')}")
        print(f"Task Type: {response.get('task_type')}")
        print(f"Status: {response.get('status')}")
        
        if response.get('status') == 'success':
            print(f"\nResult:\n{response.get('result')}")
        else:
            print(f"\nError: {response.get('error')}")
        
        print(f"{'='*60}\n")


if __name__ == "__main__":
    consumer = ResponseConsumer()
    consumer.start()
