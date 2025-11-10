"""
Kafka Producer - Sends tasks to agents via Kafka
"""
import json
import time
from kafka import KafkaProducer
from dotenv import load_dotenv
import os

load_dotenv()

class AgentProducer:
    def __init__(self):
        self.bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        self.topic = os.getenv('KAFKA_TOPIC_REQUESTS', 'agent_requests')
        
        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print(f"Producer connected to Kafka at {self.bootstrap_servers}")
    
    def send_task(self, task_type, task_data):
        """Send a task to the agent queue"""
        message = {
            'task_type': task_type,
            'task_data': task_data,
            'timestamp': time.time()
        }
        
        future = self.producer.send(self.topic, value=message)
        result = future.get(timeout=10)
        
        print(f"Task sent: {task_type} -> {result}")
        return result
    
    def close(self):
        self.producer.close()


if __name__ == "__main__":
    producer = AgentProducer()
    
    # Example tasks
    tasks = [
        {
            'task_type': 'summarize',
            'task_data': {
                'text': 'Machine learning is a subset of artificial intelligence that focuses on enabling computers to learn from data without being explicitly programmed. It uses algorithms to identify patterns and make predictions based on historical data.'
            }
        },
        {
            'task_type': 'analyze',
            'task_data': {
                'text': 'Climate change is causing rising sea levels, extreme weather events, and biodiversity loss. Scientists emphasize the urgent need for renewable energy adoption and carbon emission reduction.'
            }
        },
        {
            'task_type': 'question',
            'task_data': {
                'question': 'What are the main differences between supervised and unsupervised learning in machine learning?'
            }
        }
    ]
    
    print("\n=== Sending Tasks to Agents ===\n")
    for task in tasks:
        producer.send_task(task['task_type'], task['task_data'])
        time.sleep(1)
    
    producer.close()
    print("\n=== All tasks sent ===")
