"""
AI Agent Consumer - Processes tasks from Kafka using LangChain + Ollama
"""
import json
import os
from kafka import KafkaConsumer, KafkaProducer
from dotenv import load_dotenv
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

load_dotenv()

class AIAgent:
    def __init__(self, agent_name="Agent-1"):
        self.agent_name = agent_name
        self.bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        self.request_topic = os.getenv('KAFKA_TOPIC_REQUESTS', 'agent_requests')
        self.response_topic = os.getenv('KAFKA_TOPIC_RESPONSES', 'agent_responses')
        
        # Initialize LangChain with Ollama
        self.llm = Ollama(
            model=os.getenv('OLLAMA_MODEL', 'llama3.1:latest'),
            base_url=os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434'),
            temperature=0.7
        )
        
        # Kafka Consumer
        self.consumer = KafkaConsumer(
            self.request_topic,
            bootstrap_servers=self.bootstrap_servers,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id=f'{agent_name}-group'
        )
        
        # Kafka Producer for responses
        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        print(f"{self.agent_name} initialized and connected to Kafka")
    
    def process_summarize(self, text):
        """Summarize text using LangChain"""
        prompt = PromptTemplate(
            input_variables=["text"],
            template="Summarize the following text in 2-3 sentences:\n\n{text}"
        )
        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = chain.run(text=text)
        return result.strip()
    
    def process_analyze(self, text):
        """Analyze text using LangChain"""
        prompt = PromptTemplate(
            input_variables=["text"],
            template="Analyze the following text and provide key insights:\n\n{text}"
        )
        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = chain.run(text=text)
        return result.strip()
    
    def process_question(self, question):
        """Answer question using LangChain"""
        prompt = PromptTemplate(
            input_variables=["question"],
            template="Answer the following question concisely:\n\n{question}"
        )
        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = chain.run(question=question)
        return result.strip()
    
    def process_task(self, task):
        """Process different types of tasks"""
        task_type = task.get('task_type')
        task_data = task.get('task_data')
        
        print(f"\n{self.agent_name} processing: {task_type}")
        
        try:
            if task_type == 'summarize':
                result = self.process_summarize(task_data.get('text', ''))
            elif task_type == 'analyze':
                result = self.process_analyze(task_data.get('text', ''))
            elif task_type == 'question':
                result = self.process_question(task_data.get('question', ''))
            else:
                result = f"Unknown task type: {task_type}"
            
            response = {
                'agent': self.agent_name,
                'task_type': task_type,
                'result': result,
                'status': 'success'
            }
            
        except Exception as e:
            response = {
                'agent': self.agent_name,
                'task_type': task_type,
                'error': str(e),
                'status': 'error'
            }
        
        # Send response to response topic
        self.producer.send(self.response_topic, value=response)
        print(f"{self.agent_name} completed: {task_type}")
        
        return response
    
    def start(self):
        """Start consuming messages"""
        print(f"\n{self.agent_name} is listening for tasks...\n")
        
        try:
            for message in self.consumer:
                task = message.value
                self.process_task(task)
                
        except KeyboardInterrupt:
            print(f"\n{self.agent_name} shutting down...")
        finally:
            self.consumer.close()
            self.producer.close()


if __name__ == "__main__":
    import sys
    
    agent_name = sys.argv[1] if len(sys.argv) > 1 else "Agent-1"
    agent = AIAgent(agent_name=agent_name)
    agent.start()
