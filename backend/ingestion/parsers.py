import os
from typing import List, Dict, Any
from pathlib import Path

def parse_pdf(file_bytes: bytes) -> List[Dict[str, Any]]:
    import fitz # PyMuPDF
    pages = []
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text") or ""
        pages.append({
            "page": page_num + 1,
            "section": f"Page {page_num + 1}",
            "text": text.strip()
        })
    doc.close()
    return pages

def parse_docx(file_bytes: bytes) -> List[Dict[str, Any]]:
    import docx
    import io
    doc = docx.Document(io.BytesIO(file_bytes))
    full_text = []
    current_section = "Main Document"
    sections = []
    
    current_text = []
    for p in doc.paragraphs:
        txt = p.text.strip()
        if not txt:
            continue
        if p.style and p.style.name and p.style.name.startswith("Heading"):
            if current_text:
                sections.append({
                    "page": 1,
                    "section": current_section,
                    "text": "\n".join(current_text)
                })
                current_text = []
            current_section = txt
        current_text.append(txt)
        
    if current_text:
        sections.append({
            "page": 1,
            "section": current_section,
            "text": "\n".join(current_text)
        })
        
    if not sections:
        sections.append({"page": 1, "section": "Main Document", "text": ""})
    return sections

def parse_txt(file_bytes: bytes) -> List[Dict[str, Any]]:
    text = file_bytes.decode("utf-8", errors="ignore")
    return [{"page": 1, "section": "Document Content", "text": text.strip()}]

def parse_document(filename: str, file_bytes: bytes) -> List[Dict[str, Any]]:
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return parse_pdf(file_bytes)
    elif ext == ".docx":
        return parse_docx(file_bytes)
    elif ext == ".txt":
        return parse_txt(file_bytes)
    else:
        raise ValueError(f"Unsupported file format: {ext}")
