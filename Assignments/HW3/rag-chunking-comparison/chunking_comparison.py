#!/usr/bin/env python3
"""
LlamaIndex Chunking Techniques Comparison
=========================================

This script compares three chunking techniques on Tiny Shakespeare dataset:
1. Token-based chunking (TokenTextSplitter)
2. Semantic chunking (SemanticSplitterNodeParser) 
3. Sentence-window chunking (SentenceWindowNodeParser)

For DATA236: Distributed Systems for Data Engineering
"""

import os
import time
import requests
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity
from tabulate import tabulate

# LlamaIndex imports
from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.schema import Document, TextNode
from llama_index.core.vector_stores import SimpleVectorStore
from llama_index.core import StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import (
    TokenTextSplitter,
    SemanticSplitterNodeParser,
    SentenceWindowNodeParser
)

# Configuration
EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
SHAKESPEARE_URL = "https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt"
DATA_DIR = Path("data")
RESULTS_DIR = Path("results")

def setup_directories():
    """Create necessary directories"""
    DATA_DIR.mkdir(exist_ok=True)
    RESULTS_DIR.mkdir(exist_ok=True)
    print(f"Directories created: {DATA_DIR}, {RESULTS_DIR}")

def download_shakespeare():
    """Download Tiny Shakespeare dataset"""
    data_path = DATA_DIR / "tinyshakespeare.txt"
    
    if data_path.exists():
        print(f"Using cached dataset: {data_path}")
    else:
        print("Downloading Tiny Shakespeare dataset...")
        response = requests.get(SHAKESPEARE_URL, timeout=30)
        response.raise_for_status()
        
        with open(data_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"Downloaded to: {data_path}")
    
    with open(data_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    print(f"Dataset stats: {len(text):,} characters, {len(text.split()):,} words")
    return text

def setup_embedding_model():
    """Initialize HuggingFace embedding model"""
    print(f"Loading embedding model: {EMBED_MODEL_NAME}")
    
    # Clear any HuggingFace tokens to use public model
    for var in ["HF_TOKEN", "HUGGINGFACEHUB_API_TOKEN", "HUGGINGFACE_HUB_TOKEN"]:
        os.environ.pop(var, None)
    
    embed_model = HuggingFaceEmbedding(model_name=EMBED_MODEL_NAME)
    Settings.embed_model = embed_model
    
    # Test embedding
    test_vec = embed_model.get_text_embedding("test")
    print(f"Embedding model loaded. Dimension: {len(test_vec)}")
    
    return embed_model

def token_chunking_pipeline(text, embed_model):
    """Token-based chunking pipeline"""
    print("\n" + "="*60)
    print("TOKEN-BASED CHUNKING PIPELINE")
    print("="*60)
    
    # Token splitter with specified parameters
    splitter = TokenTextSplitter(
        chunk_size=512,
        chunk_overlap=50
    )
    
    doc = Document(text=text)
    nodes = splitter.get_nodes_from_documents([doc])
    
    print(f"Created {len(nodes)} chunks")
    print(f"Chunk size: 512 tokens, overlap: 50 tokens")
    
    # Build vector index
    print("Building vector index...")
    start_time = time.time()
    
    vector_store = SimpleVectorStore()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex(nodes, storage_context=storage_context)
    
    build_time = time.time() - start_time
    print(f"Index built in {build_time:.2f} seconds")
    
    return index, nodes, {
        'technique': 'Token-based',
        'num_chunks': len(nodes),
        'chunk_size': 512,
        'chunk_overlap': 50,
        'build_time': build_time,
        'avg_chunk_length': np.mean([len(node.text) for node in nodes])
    }

def semantic_chunking_pipeline(text, embed_model):
    """Semantic chunking pipeline"""
    print("\n" + "="*60)
    print("SEMANTIC CHUNKING PIPELINE")
    print("="*60)
    
    # Semantic splitter
    splitter = SemanticSplitterNodeParser(
        buffer_size=3,
        embed_model=embed_model
    )
    
    doc = Document(text=text)
    nodes = splitter.get_nodes_from_documents([doc])
    
    print(f"Created {len(nodes)} chunks")
    print(f"Buffer size: 3 (semantic boundary detection)")
    
    # Build vector index
    print("Building vector index...")
    start_time = time.time()
    
    vector_store = SimpleVectorStore()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex(nodes, storage_context=storage_context)
    
    build_time = time.time() - start_time
    print(f"Index built in {build_time:.2f} seconds")
    
    return index, nodes, {
        'technique': 'Semantic',
        'num_chunks': len(nodes),
        'buffer_size': 3,
        'build_time': build_time,
        'avg_chunk_length': np.mean([len(node.text) for node in nodes])
    }

def sentence_window_chunking_pipeline(text, embed_model):
    """Sentence-window chunking pipeline"""
    print("\n" + "="*60)
    print("SENTENCE-WINDOW CHUNKING PIPELINE") 
    print("="*60)
    
    # Sentence window splitter
    splitter = SentenceWindowNodeParser(
        window_size=3,
        window_metadata_key="window",
        original_text_metadata_key="original_text"
    )
    
    doc = Document(text=text)
    nodes = splitter.get_nodes_from_documents([doc])
    
    print(f"Created {len(nodes)} chunks") 
    print(f"Window size: 3 (context sentences)")
    
    # Build vector index
    print("Building vector index...")
    start_time = time.time()
    
    vector_store = SimpleVectorStore()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex(nodes, storage_context=storage_context)
    
    build_time = time.time() - start_time
    print(f"Index built in {build_time:.2f} seconds")
    
    return index, nodes, {
        'technique': 'Sentence-window',
        'num_chunks': len(nodes),
        'window_size': 3,
        'build_time': build_time,
        'avg_chunk_length': np.mean([len(node.text) for node in nodes])
    }

def retrieve_and_analyze(index, query, embed_model, technique_name, k=5):
    """Retrieve and analyze results for a given technique"""
    print(f"\nRETRIEVAL ANALYSIS - {technique_name}")
    print("-" * 50)
    
    # Get query embedding
    start_time = time.time()
    query_embedding = np.array(embed_model.get_text_embedding(query))
    retrieval_time = time.time() - start_time
    
    print(f"Query: {query}")
    print(f"Query embedding shape: {query_embedding.shape}")
    print(f"First 8 embedding values: {np.round(query_embedding[:8], 4).tolist()}")
    
    # Retrieve top-k results
    retriever = index.as_retriever(similarity_top_k=k)
    results = retriever.retrieve(query)
    
    # Analyze results
    analysis_data = []
    doc_embeddings = []
    
    for rank, result in enumerate(results, 1):
        node = result.node
        text_content = node.text.strip().replace('\n', ' ')
        
        # Get document embedding
        doc_embedding = np.array(embed_model.get_text_embedding(text_content))
        doc_embeddings.append(doc_embedding)
        
        # Calculate cosine similarity
        cosine_sim = cosine_similarity(
            query_embedding.reshape(1, -1), 
            doc_embedding.reshape(1, -1)
        )[0][0]
        
        analysis_data.append({
            'rank': rank,
            'store_score': round(result.score, 6),
            'cosine_sim': round(cosine_sim, 6),
            'chunk_len': len(text_content),
            'preview': text_content[:160] + "..." if len(text_content) > 160 else text_content
        })
    
    # Create results table
    df = pd.DataFrame(analysis_data)
    print(f"\nTOP-{k} RETRIEVAL RESULTS:")
    print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))
    
    # Vector shapes info
    if doc_embeddings:
        doc_embeddings = np.vstack(doc_embeddings)
        print(f"\nVector Shapes:")
        print(f"   Query vector: {query_embedding.shape}")
        print(f"   Document vectors: {doc_embeddings.shape}")
    
    # Return metrics for comparison
    return {
        'technique': technique_name,
        'retrieval_time_ms': round(retrieval_time * 1000, 2),
        'top_1_cosine': analysis_data[0]['cosine_sim'] if analysis_data else 0,
        'mean_cosine': round(np.mean([item['cosine_sim'] for item in analysis_data]), 4),
        'top_1_store_score': analysis_data[0]['store_score'] if analysis_data else 0,
        'mean_store_score': round(np.mean([item['store_score'] for item in analysis_data]), 4),
        'results_df': df
    }

def compare_techniques(metrics_list):
    """Compare all techniques and generate summary"""
    print("\n" + "="*80)
    print("COMPARISON SUMMARY")
    print("="*80)
    
    comparison_df = pd.DataFrame([
        {
            'Technique': m['technique'],
            'Top-1 Cosine': m['top_1_cosine'],
            'Mean@5 Cosine': m['mean_cosine'], 
            'Retrieval Time (ms)': m['retrieval_time_ms']
        }
        for m in metrics_list
    ])
    
    print("\nRETRIEVAL QUALITY COMPARISON:")
    print(tabulate(comparison_df, headers='keys', tablefmt='grid', showindex=False))
    
    # Determine best technique
    best_cosine = comparison_df.loc[comparison_df['Mean@5 Cosine'].idxmax()]
    fastest = comparison_df.loc[comparison_df['Retrieval Time (ms)'].idxmin()]
    
    print(f"\nBest Retrieval Quality: {best_cosine['Technique']} (Mean@5 Cosine: {best_cosine['Mean@5 Cosine']})")
    print(f"Fastest Retrieval: {fastest['Technique']} ({fastest['Retrieval Time (ms)']} ms)")
    
    return comparison_df

def main():
    """Main execution function"""
    print("LlamaIndex Chunking Techniques Comparison")
    print("="*60)
    
    # Setup
    setup_directories()
    text = download_shakespeare()
    embed_model = setup_embedding_model()
    
    # Query to test
    query = "Who are the two feuding houses?"
    print(f"\nTest Query: '{query}'")
    
    # Run all three pipelines
    techniques = []
    metrics = []
    
    # 1. Token-based chunking
    token_index, token_nodes, token_stats = token_chunking_pipeline(text, embed_model)
    token_metrics = retrieve_and_analyze(token_index, query, embed_model, "Token-based")
    techniques.append(('Token-based', token_index, token_stats))
    metrics.append(token_metrics)
    
    # 2. Semantic chunking  
    semantic_index, semantic_nodes, semantic_stats = semantic_chunking_pipeline(text, embed_model)
    semantic_metrics = retrieve_and_analyze(semantic_index, query, embed_model, "Semantic")
    techniques.append(('Semantic', semantic_index, semantic_stats))
    metrics.append(semantic_metrics)
    
    # 3. Sentence-window chunking
    window_index, window_nodes, window_stats = sentence_window_chunking_pipeline(text, embed_model)
    window_metrics = retrieve_and_analyze(window_index, query, embed_model, "Sentence-window")
    techniques.append(('Sentence-window', window_index, window_stats))
    metrics.append(window_metrics)
    
    # Final comparison
    comparison_df = compare_techniques(metrics)
    
    # Print chunk statistics
    print(f"\nCHUNK STATISTICS:")
    stats_df = pd.DataFrame([
        {
            'Technique': stats['technique'],
            'Num Chunks': stats['num_chunks'],
            'Avg Chunk Length': round(stats['avg_chunk_length'], 1),
            'Build Time (s)': round(stats['build_time'], 2)
        }
        for _, _, stats in techniques
    ])
    print(tabulate(stats_df, headers='keys', tablefmt='grid', showindex=False))
    
    print(f"\nAnalysis complete! Take screenshots of each section for your report.")

if __name__ == "__main__":
    main()