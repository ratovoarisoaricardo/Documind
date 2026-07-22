import os
import tempfile
from typing import List, Dict, Any
from pypdf import PdfReader

class DocumentProcessor:
    """Processes uploaded documents (PDF, TXT) and splits them into chunks with metadata."""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def process_file(self, uploaded_file) -> List[Dict[str, Any]]:
        """Reads file content and returns list of chunk dictionaries with text and metadata."""
        filename = uploaded_file.name
        file_ext = os.path.splitext(filename)[1].lower()
        
        raw_pages = []
        
        if file_ext == '.pdf':
            reader = PdfReader(uploaded_file)
            for idx, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                if text.strip():
                    raw_pages.append({"text": text, "page": idx + 1, "source": filename})
        elif file_ext in ['.txt', '.md']:
            text = uploaded_file.read().decode('utf-8')
            raw_pages.append({"text": text, "page": 1, "source": filename})
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")

        # Chunking logic
        chunks = []
        for page_info in raw_pages:
            page_text = page_info["text"]
            page_num = page_info["page"]
            
            # Simple sliding window chunker
            start = 0
            while start < len(page_text):
                end = start + self.chunk_size
                chunk_str = page_text[start:end]
                
                if chunk_str.strip():
                    chunks.append({
                        "content": chunk_str.strip(),
                        "metadata": {
                            "source": filename,
                            "page": page_num,
                            "chunk_id": len(chunks) + 1
                        }
                    })
                start += self.chunk_size - self.chunk_overlap
                
        return chunks
