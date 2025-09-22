# RAG Chunking Techniques Comparison

This project compares three different chunking techniques for Retrieval-Augmented Generation (RAG) using LlamaIndex:

## Chunking Techniques Analyzed

1. **Token-based Chunking** - Fixed token-size chunks with overlap
2. **Semantic Chunking** - Content-aware semantic boundary detection  
3. **Sentence-window Chunking** - Context-aware sentence windows

## Dataset

- **Tiny Shakespeare**: Classic text dataset for NLP experiments
- Downloaded from: https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt

## Setup Instructions

### 1. Create Virtual Environment
```bash
python3 -m venv rag-env
source rag-env/bin/activate  # On Windows: rag-env\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Comparison
```bash
python chunking_comparison.py
```

## Features

- **Automatic Data Download**: Downloads Tiny Shakespeare dataset if not present
- **Embedding Model**: Uses HuggingFace `sentence-transformers/all-MiniLM-L6-v2`
- **Vector Similarity**: Cosine similarity analysis for retrieval quality
- **Performance Metrics**: Build time, retrieval time, and accuracy comparison
- **Detailed Analysis**: Chunk statistics and top-k retrieval results

## Output

The script generates:
- Detailed console output for each chunking technique
- Comparison tables for retrieval quality and performance
- Analysis of vector shapes and similarity scores

## Requirements

- Python 3.8+
- See `requirements.txt` for package dependencies

## Course Context

Created for **DATA236: Distributed Systems for Data Engineering** - demonstrating different text chunking strategies for RAG systems.