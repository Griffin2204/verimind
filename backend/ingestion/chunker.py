import uuid
from typing import List, Dict, Any
from core.config import CHUNK_SIZE, CHUNK_OVERLAP

class DocumentChunkDTO:
    def __init__(self, chunk_id: str, document_id: int, page: int, section: str, text: str):
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.page = page
        self.section = section
        self.text = text

def chunk_document(document_id: int, parsed_sections: List[Dict[str, Any]], chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP) -> List[DocumentChunkDTO]:
    chunks = []
    chunk_index = 0
    
    for section_info in parsed_sections:
        page = section_info.get("page", 1)
        section = section_info.get("section", "General")
        text = section_info.get("text", "")
        
        if not text:
            continue
            
        if len(text) <= chunk_size:
            chunk_id = f"doc_{document_id}_chunk_{chunk_index}"
            chunks.append(DocumentChunkDTO(chunk_id, document_id, page, section, text))
            chunk_index += 1
        else:
            start = 0
            while start < len(text):
                end = min(start + chunk_size, len(text))
                
                # Try to break at newline or space near end if possible
                if end < len(text):
                    last_space = text.rfind(" ", start + chunk_size - 100, end)
                    if last_space > start:
                        end = last_space
                
                chunk_text = text[start:end].strip()
                if chunk_text:
                    chunk_id = f"doc_{document_id}_chunk_{chunk_index}"
                    chunks.append(DocumentChunkDTO(chunk_id, document_id, page, section, chunk_text))
                    chunk_index += 1
                
                start = end - chunk_overlap if end < len(text) else len(text)
                
    return chunks
