from typing import List, Dict, Any

class RAGEngine:
    """RAG Synthesis engine orchestrating Retrieval + Contextual Answer Generation."""
    
    def __init__(self, vector_store):
        self.vector_store = vector_store

    def query(self, user_question: str) -> Dict[str, Any]:
        """Retrieves relevant context chunks and synthesizes an answer with source citations."""
        relevant_chunks = self.vector_store.search(user_question, top_k=3)
        
        if not relevant_chunks:
            return {
                "answer": "I couldn't find relevant information in the uploaded documents to answer your question.",
                "sources": []
            }
            
        answer_intro = f"Based on the document context, here is the relevant answer regarding **'{user_question}'**:\n\n"
        
        paragraphs = []
        for idx, chunk in enumerate(relevant_chunks, 1):
            excerpt = chunk['content'].strip()
            src = chunk['metadata']['source']
            pg = chunk['metadata']['page']
            paragraphs.append(f"📌 **Relevant Context {idx}** *(Source: `{src}`, Page {pg})*:\n> {excerpt}")
            
        synthesized_answer = answer_intro + "\n\n".join(paragraphs)
        
        sources = [{
            "filename": c['metadata']['source'],
            "page": c['metadata']['page'],
            "snippet": c['content'][:150] + "..."
        } for c in relevant_chunks]
        
        return {
            "answer": synthesized_answer,
            "sources": sources
        }
