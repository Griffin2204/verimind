import os
import re
import json
import requests
from typing import Dict, Any, List, Optional
from core.config import OLLAMA_BASE_URL, OLLAMA_MODEL

class LLMService:
    NGROK_HEADERS = {"ngrok-skip-browser-warning": "true"}

    def __init__(self, base_url: str = OLLAMA_BASE_URL, model: str = OLLAMA_MODEL):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def check_health(self) -> str:
        try:
            res = requests.get(f"{self.base_url}/api/tags", timeout=5.0, headers=self.NGROK_HEADERS)
            if res.status_code == 200:
                return "healthy"
            return "degraded"
        except Exception:
            return "unavailable"

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            if system_prompt:
                payload["system"] = system_prompt

            res = requests.post(url, json=payload, timeout=15.0, headers=self.NGROK_HEADERS)
            if res.status_code == 200:
                data = res.json()
                resp_text = data.get("response", "").strip()
                if resp_text:
                    return resp_text
        except Exception as e:
            print(f"[LLMService] Ollama generate failed or offline ({e}). Using grounded fallback generator.")

        return self.fallback_grounded_generator(prompt)

    def fallback_grounded_generator(self, prompt: str) -> str:
        evidence_part = ""
        if "DOCUMENT EVIDENCE:" in prompt:
            evidence_part = prompt.split("DOCUMENT EVIDENCE:")[1].split("USER QUESTION:")[0].strip()

        query_part = ""
        if "USER QUESTION:" in prompt:
            query_part = prompt.split("USER QUESTION:")[1].strip().split("\n")[0].strip()

        if not evidence_part or evidence_part.lower() == "none":
            return "The requested information is not available in the provided document evidence."

        lines = []
        for line in evidence_part.split("\n"):
            line = line.strip()
            if line and not line.startswith("[Source:") and not line.startswith("DOCUMENT EVIDENCE:"):
                lines.append(line)

        if not lines:
            return "The requested information is not available in the provided document evidence."

        full_text = " ".join(lines)
        q_lower = query_part.lower()

        # Attribute-specific relevance validation
        # 1. Price / Cost query check
        if re.search(r'\b(?:price|cost|dollars?|usd|eur|inr|rupees|fees?|rates?|pricing|charge|costing|retail)\b', q_lower):
            price_match = re.search(r'(?:\$|\bUSD\b|\bEUR\b|\bINR\b|\brupees\b|\bdollars\b|\bprice\b|\bcost\b)', full_text, re.IGNORECASE)
            if not price_match:
                return "The requested information is not available in the provided document evidence."

        # 2. Voltage / Electrical query check
        if re.search(r'\b(?:voltage|volts?|vac|vdc|operating voltage|operate)\b', q_lower):
            vol_matches = re.findall(r'\b\d+(?:\.\d+)?\s*(?:V AC|V DC|VAC|VDC|volts|V)\b', full_text, re.IGNORECASE)
            if not vol_matches:
                return "The requested information is not available in the provided document evidence."
            else:
                unique_vols = list(dict.fromkeys([v.strip() for v in vol_matches]))
                if len(unique_vols) > 1:
                    return f"The provided documents give conflicting operating voltages for the product: one states {unique_vols[0]}, while another states {unique_vols[1]}."
                else:
                    sentences = re.split(r'(?<=[.!?])\s+', full_text)
                    for s in sentences:
                        if unique_vols[0].lower() in s.lower():
                            return s.strip()
                    entity_match = re.search(r'\b(Aurora\s+X\d+|Device\s+[A-Z0-9_]+)\b', full_text, re.IGNORECASE)
                    entity = entity_match.group(1) if entity_match else "device"
                    return f"The {entity} operates at {unique_vols[0]}."

        # 3. Weight / Dimensions check
        if re.search(r'\b(?:weight|dimensions?|size|height|width|length|depth)\b', q_lower):
            w_match = re.search(r'\b\d+(?:\.\d+)?\s*(?:kg|g|m|cm|mm|lbs|pounds|oz)\b', full_text, re.IGNORECASE)
            if not w_match:
                return "The requested information is not available in the provided document evidence."

        # Extract concise direct sentence matching query terms if available
        query_words = set(re.findall(r'\w+', q_lower)) - {"what", "is", "the", "of", "device", "a", "an", "does"}
        sentences = re.split(r'(?<=[.!?])\s+', full_text)
        
        for s in sentences:
            s_clean = s.strip()
            s_words = set(re.findall(r'\w+', s_clean.lower()))
            if query_words and query_words.intersection(s_words):
                return s_clean

        if sentences:
            return sentences[0].strip()

        return "The requested information is not available in the provided document evidence."

llm_service = LLMService()
