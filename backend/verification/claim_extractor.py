import re
from typing import List, Dict

def extract_claims(answer_text: str) -> List[Dict[str, str]]:
    if not answer_text or answer_text.startswith("I could not find sufficient"):
        return []

    # Clean and split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', answer_text.strip())
    claims = []
    
    for s in sentences:
        s_clean = s.strip()
        # Filter non-factual / preamble sentences
        if len(s_clean) > 5 and not s_clean.startswith("Based on"):
            claims.append({"text": s_clean})
            
    if not claims and len(answer_text.strip()) > 5:
        claims.append({"text": answer_text.strip()})
        
    return claims
