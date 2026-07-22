from typing import List, Dict, Any

class VectorStore:
    """In-memory Vector Store performing vector embedding & similarity search."""
    
    def __init__(self):
        self.chunks: List[Dict[str, Any]] = []

    def add_chunks(self, new_chunks: List[Dict[str, Any]]):
        """Adds text chunks to the vector database."""
        self.chunks.extend(new_chunks)

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Performs similarity search to retrieve top_k matching chunks."""
        if not self.chunks:
            return []

        query_terms = set(query.lower().split())
        scored_chunks = []

        for chunk in self.chunks:
            content = chunk["content"].lower()
            score = 0
            for term in query_terms:
                if term in content:
                    score += content.count(term)
            
            if query.lower() in content:
                score += 5
                
            if score > 0:
                scored_chunks.append((score, chunk))
                
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        
        if not scored_chunks:
            return self.chunks[:top_k]
            
        return [chunk for score, chunk in scored_chunks[:top_k]]

    def clear(self):
        """Resets the vector store."""
        self.chunks = []
