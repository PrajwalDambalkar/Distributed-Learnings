# HW8 Part 2 - Agentic Mini System with Kafka + LangChain + Ollama

A multi-agent AI system where agents process tasks from a Kafka message queue using LangChain with local Ollama models.

## 🏗️ Architecture

```
Producer → Kafka (agent_requests topic) → AI Agent (Ollama) → Kafka (agent_responses topic) → Consumer
```

## 📋 Components

1. **Producer** (`producer.py`) - Sends tasks to Kafka queue
2. **AI Agent** (`agent.py`) - Processes tasks using LangChain + Ollama (local LLM)
3. **Consumer** (`consumer.py`) - Displays agent responses

## 🔧 Prerequisites

- Python 3.8+
- Docker and Docker Compose (for Kafka)
- Ollama installed locally (https://ollama.ai)
- Ollama model downloaded (e.g., `ollama pull llama3.2`)

## 📦 Installation

### 0. Install and Start Ollama (if not already done)

```bash
# Install Ollama from https://ollama.ai
# Or on macOS: brew install ollama

# Pull a model
ollama pull llama3.2

# Verify Ollama is running
ollama list
```

### 1. Start Kafka with Docker Compose

```bash
docker-compose up -d
```

This starts Zookeeper and Kafka broker.

### 2. Install Python Dependencies

```bash
cd Part2_Agentic_System
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` if you want to use a different Ollama model:

```
OLLAMA_MODEL=llama3.2
OLLAMA_BASE_URL=http://localhost:11434
```

Available models: `llama3.2`, `mistral`, `phi`, `codellama`, etc.

## 🚀 Running the System

### Terminal 1: Start the AI Agent

```bash
python agent.py Agent-1
```

### Terminal 2: Start the Response Consumer

```bash
python consumer.py
```

### Terminal 3: Send Tasks (Producer)

```bash
python producer.py
```

## 📝 Task Types

The system supports three types of tasks:

1. **Summarize** - Summarizes given text
2. **Analyze** - Analyzes text and provides insights
3. **Question** - Answers questions

## 🔄 How It Works

1. **Producer** sends tasks to `agent_requests` Kafka topic
2. **AI Agent** consumes from `agent_requests`, processes using LangChain/OpenAI
3. **AI Agent** sends results to `agent_responses` Kafka topic
4. **Consumer** displays responses from `agent_responses`

## 🧪 Example Output

### Producer sends:

```
Task sent: summarize
Task sent: analyze
Task sent: question
```

### Agent processes:

```
Agent-1 processing: summarize
Agent-1 completed: summarize
```

### Consumer receives:

```
============================================================
Agent: Agent-1
Task Type: summarize
Status: success

Result:
Machine learning is a branch of AI that enables computers to...
============================================================
```

## 🛠️ Running Multiple Agents

You can run multiple agents in parallel:

```bash
# Terminal 1
python agent.py Agent-1

# Terminal 2
python agent.py Agent-2

# Terminal 3
python agent.py Agent-3
```

Kafka will distribute tasks across agents automatically!

## 📊 Kafka Topics

- `agent_requests` - Input tasks for agents
- `agent_responses` - Agent processing results

## 🐛 Troubleshooting

### Kafka Connection Issues

```bash
# Check if Kafka is running
docker-compose ps

# View Kafka logs
docker-compose logs kafka
```

### OpenAI API Issues

- Ensure your API key is valid
- Check you have sufficient credits

### Module Not Found

```bash
pip install -r requirements.txt
```

## 🧹 Cleanup

```bash
# Stop Kafka
docker-compose down

# Remove volumes (clears all Kafka data)
docker-compose down -v
```

## 📁 Project Structure

```
Part2_Agentic_System/
├── agent.py              # AI Agent with LangChain
├── producer.py           # Task producer
├── consumer.py           # Response consumer
├── requirements.txt      # Python dependencies
├── .env.example         # Environment template
├── docker-compose.yml   # Kafka setup
└── README.md           # This file
```

## 🎯 Features

- ✅ Asynchronous task processing
- ✅ Multi-agent support
- ✅ LangChain integration
- ✅ OpenAI GPT-3.5 Turbo
- ✅ Kafka message queue
- ✅ Scalable architecture

## 📚 Technologies

- **Kafka** - Message streaming platform
- **LangChain** - AI agent framework
- **OpenAI** - Language model
- **Python** - Implementation language
