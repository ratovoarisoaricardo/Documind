import os
from typing import List, Dict, Any
from pypdf import PdfReader

class DocumentProcessor:
    """Processes uploaded documents (PDF, TXT, MD) safely with chunking and metadata sanitization."""
    
    MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB Limit
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = max(100, min(chunk_size, 2000))
        self.chunk_overlap = max(0, min(chunk_overlap, chunk_size // 2))

    def process_file(self, uploaded_file) -> List[Dict[str, Any]]:
        """Reads file content safely and returns chunk dictionaries with metadata."""
        # Security Check: File Size Limit
        uploaded_file.seek(0, os.SEEK_END)
        size = uploaded_file.tell()
        uploaded_file.seek(0)
        
        if size > self.MAX_FILE_SIZE:
            raise ValueError(f"File size exceeds maximum safety limit of 20MB.")

        # Sanitize Filename
        filename = os.path.basename(uploaded_file.name).replace("..", "").strip()
        file_ext = os.path.splitext(filename)[1].lower()
        
        raw_pages = []
        
        if file_ext == '.pdf':
            try:
                reader = PdfReader(uploaded_file)
                for idx, page in enumerate(reader.pages):
                    text = page.extract_text() or ""
                    if text.strip():
                        raw_pages.append({"text": text.strip(), "page": idx + 1, "source": filename})
            except Exception as e:
                raise ValueError(f"Could not parse PDF file '{filename}': {str(e)}")
                
        elif file_ext in ['.txt', '.md']:
            try:
                content_bytes = uploaded_file.read()
                text = content_bytes.decode('utf-8', errors='ignore')
                if text.strip():
                    raw_pages.append({"text": text.strip(), "page": 1, "source": filename})
            except Exception as e:
                raise ValueError(f"Could not read text file '{filename}': {str(e)}")
        else:
            raise ValueError(f"Unsupported file type '{file_ext}'. Allowed: .pdf, .txt, .md")

        # Sliding window chunking
        chunks = []
        for page_info in raw_pages:
            page_text = page_info["text"]
            page_num = page_info["page"]
            
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
