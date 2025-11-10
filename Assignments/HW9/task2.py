import redis
import requests
import numpy as np
import json
import time
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, List, Tuple, Optional

class SemanticCache:
    def __init__(self, redis_host="localhost", redis_port=6380, similarity_threshold=0.85):
        """Initialize semantic cache with Redis and embedding model"""
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.similarity_threshold = similarity_threshold
        self.ollama_url = "http://localhost:11434"
        
        # Initialize sentence transformer for embeddings
        print("Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # 384 dimensions
        print("✓ Embedding model loaded")
        
        # Test connections
        try:
            self.redis_client.ping()
            print("✓ Connected to Redis successfully")
        except redis.ConnectionError:
            print("✗ Failed to connect to Redis!")
            raise
            
        self._setup_vector_index()
    
    
    def _setup_vector_index(self):
        """Create Redis vector index for semantic search"""
        try:
            # Try to create the index (will fail if it already exists)
            self.redis_client.execute_command(
                "FT.CREATE", "semantic_idx", "ON", "HASH", 
                "PREFIX", "1", "cache:", 
                "SCHEMA", 
                "embedding", "VECTOR", "FLAT", "6", "TYPE", "FLOAT32", "DIM", "384", "DISTANCE_METRIC", "COSINE",
                "query", "TEXT",
                "response", "TEXT", 
                "timestamp", "NUMERIC"
            )
            print("✓ Created new vector index")
        except redis.ResponseError as e:
            if "Index already exists" in str(e):
                print("✓ Vector index already exists")
            else:
                print(f"✗ Error creating index: {e}")
                raise
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding vector for text using SentenceTransformer"""
        embedding = self.embedding_model.encode([text])
        return embedding[0]
    
    def _vector_to_bytes(self, vector: np.ndarray) -> bytes:
        """Convert numpy vector to bytes for Redis storage"""
        return vector.astype(np.float32).tobytes()
    
    def _bytes_to_vector(self, vector_bytes: bytes) -> np.ndarray:
        """Convert bytes back to numpy vector"""
        return np.frombuffer(vector_bytes, dtype=np.float32)
    
    def _search_similar_queries(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Dict]:
        """Search for semantically similar cached queries"""
        try:
            # Convert embedding to bytes for Redis search
            query_vector = self._vector_to_bytes(query_embedding)
            
            # Perform vector search using Redis FT.SEARCH
            result = self.redis_client.execute_command(
                "FT.SEARCH", "semantic_idx",
                f"*=>[KNN {top_k} @embedding $vec AS similarity]",
                "PARAMS", "2", "vec", query_vector,
                "RETURN", "4", "query", "response", "similarity", "timestamp",
                "DIALECT", "2"
            )
            
            # Parse results
            if len(result) <= 1:  # Only count, no results
                return []
            
            matches = []
            # Results format: [count, key1, [field1, value1, field2, value2], key2, [...]]
            for i in range(1, len(result), 2):
                key = result[i]
                fields = result[i + 1]
                
                # Parse fields into dict
                field_dict = {}
                for j in range(0, len(fields), 2):
                    field_dict[fields[j]] = fields[j + 1]
                
                if 'similarity' in field_dict:
                    # Convert similarity distance to similarity score (1 - distance)
                    similarity_score = 1 - float(field_dict['similarity'])
                    
                    matches.append({
                        'key': key,
                        'query': field_dict.get('query', ''),
                        'response': field_dict.get('response', ''),
                        'similarity': similarity_score,
                        'timestamp': field_dict.get('timestamp', '')
                    })
            
            return matches
            
        except Exception as e:
            print(f"Error in vector search: {e}")
            return []
    
    def _call_ollama(self, query: str, model: str = "llama3.1:latest") -> str: # llama3.1 used previously
        """Make a request to Ollama LLM"""
        try:
            # First check if Ollama is running
            health_check = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if health_check.status_code != 200:
                return "Error: Ollama service is not running. Please start with 'ollama serve'"
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": model,
                    "prompt": query,
                    "stream": False
                },
                timeout=60  # Increased timeout
            )
            
            if response.status_code == 200:
                return response.json()['response'].strip()
            else:
                return f"Error: Ollama returned status {response.status_code}"

        except requests.exceptions.ConnectionError:
            return "Error: Cannot connect to Ollama. Please start with 'ollama serve'"
        except Exception as e:
            return f"Error calling Ollama: {str(e)}"
    
    def _store_in_cache(self, query: str, response: str, query_embedding: np.ndarray):
        """Store query and response in Redis with vector embedding"""
        cache_key = f"cache:{int(time.time() * 1000)}"  # Unique key with timestamp
        
        # Store in Redis hash
        self.redis_client.hset(cache_key, mapping={
            "query": query,
            "response": response,
            "embedding": self._vector_to_bytes(query_embedding),
            "timestamp": int(time.time())
        })
    
    def query(self, user_query: str) -> Tuple[str, bool, float, float]:
        """
        Main query function with semantic caching
        Returns: (response, is_cached, similarity_score, response_time)
        """
        start_time = time.time()
        
        # Get embedding for the query
        query_embedding = self._get_embedding(user_query)
        
        # Search for similar cached queries
        similar_queries = self._search_similar_queries(query_embedding)
        
        # Check if we have a cache hit above threshold
        if similar_queries and similar_queries[0]['similarity'] >= self.similarity_threshold:
            # Cache hit!
            best_match = similar_queries[0]
            response_time = time.time() - start_time
            
            print(f"🎯 CACHE HIT - Similarity: {best_match['similarity']:.3f}")
            print(f"   Original query: '{best_match['query']}'")
            print(f"   Current query:  '{user_query}'")
            
            return best_match['response'], True, best_match['similarity'], response_time
        
        else:
            # Cache miss - call Ollama
            best_similarity = similar_queries[0]['similarity'] if similar_queries else 0.0
            print(f"❌ CACHE MISS - Best similarity: {best_similarity:.3f}")            
            
            # Call Ollama LLM
            llm_start = time.time()
            response = self._call_ollama(user_query)
            llm_time = time.time() - llm_start
            
            # Store in cache for future use
            self._store_in_cache(user_query, response, query_embedding)
            
            total_time = time.time() - start_time
            
            print(f"   Ollama response time: {llm_time:.3f}s")
            
            return response, False, 0.0, total_time
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        try:
            # Count cached items
            keys = self.redis_client.keys("cache:*")
            cache_count = len(keys)
            
            info = self.redis_client.info()
            
            return {
                "cached_queries": cache_count,
                "redis_memory": info.get("used_memory_human", "N/A"),
                "total_connections": info.get("total_connections_received", "N/A")
            }
        except Exception as e:
            return {"error": str(e)}
    
    def clear_cache(self):
        """Clear all cached data"""
        try:
            keys = self.redis_client.keys("cache:*")
            if keys:
                self.redis_client.delete(*keys)
                print(f"✓ Cleared {len(keys)} cached queries")
            else:
                print("✓ Cache was already empty")
        except Exception as e:
            print(f"Error clearing cache: {e}")


def test_semantic_cache():
    """Test the semantic caching system with diverse queries"""
    print("=" * 80)
    print("SEMANTIC CACHE TESTING WITH OLLAMA")
    print("=" * 80)
    
    # Initialize cache
    cache = SemanticCache()
    cache.clear_cache()
    
    # Test queries - mix of exact, paraphrased, and new queries
    test_queries = [
        # Original queries
        "What is machine learning?",
        "Explain artificial intelligence", 
        "How do neural networks work?",
        "What is the difference between AI and ML?",
        "Tell me about Python programming",
        
        # Exact duplicates (should be cache hits)
        "What is machine learning?",
        "Explain artificial intelligence",
        
        # Paraphrased queries (should be cache hits if similarity > 0.85)
        "Can you explain what machine learning is?",
        "What does artificial intelligence mean?",
        "How do neural nets function?",
        "What's the difference between artificial intelligence and machine learning?",
        "Tell me about programming in Python",
        
        # Completely new queries
        "What is quantum computing?",
        "How does blockchain work?",
        "Explain cloud computing",
    ]
    
    results = []
    cache_hits = 0
    total_queries = len(test_queries)
    
    print(f"\n🧪 Testing with {total_queries} diverse queries...\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"Query {i:2d}: {query}")
        
        response, is_cached, similarity, response_time = cache.query(query)
        
        if is_cached:
            cache_hits += 1
            status = "🎯 CACHED"
        else:
            status = "🔄 OLLAMA"
        
        print(f"          {status} | Time: {response_time:.3f}s | Response: {response[:100]}...")
        print()
        
        results.append({
            'query': query,
            'is_cached': is_cached,
            'similarity': similarity,
            'response_time': response_time,
            'response_length': len(response)
        })
        
        # Small delay to make output readable
        time.sleep(0.5)
    
    # Calculate performance metrics
    cache_hit_rate = (cache_hits / total_queries) * 100
    cached_times = [r['response_time'] for r in results if r['is_cached']]
    ollama_times = [r['response_time'] for r in results if not r['is_cached']]
    
    avg_cached_time = np.mean(cached_times) if cached_times else 0
    avg_ollama_time = np.mean(ollama_times) if ollama_times else 0
    speedup = avg_ollama_time / avg_cached_time if avg_cached_time > 0 else 1
    
    # Print results
    print("=" * 80)
    print("📊 PERFORMANCE RESULTS")
    print("=" * 80)
    print(f"Total queries:        {total_queries}")
    print(f"Cache hits:          {cache_hits}")
    print(f"Cache hit rate:      {cache_hit_rate:.1f}%")
    print(f"Avg cached time:     {avg_cached_time:.3f}s")
    print(f"Avg Ollama time:     {avg_ollama_time:.3f}s") 
    print(f"Speed improvement:   {speedup:.1f}x faster")
    
    # Cache statistics
    stats = cache.get_cache_stats()
    print(f"\n📈 Cache Stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print(f"\n✅ Test completed! Cache hit rate: {cache_hit_rate:.1f}%")
    
    return results


if __name__ == "__main__":
    test_semantic_cache()