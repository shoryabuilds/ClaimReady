import os
import json
from google import genai
from google.genai import types
from typing import Dict, Any
from schemas.extraction import ExtractedFacts
from .base import BaseGemmaClient
from .prompts import SYSTEM_PROMPT

class GemmaClient(BaseGemmaClient):
    def __init__(self, api_key: str = None):
        key = api_key or os.environ.get("GEMINI_API_KEY")
        if not key:
            raise ValueError("API Key is required for live GemmaClient")
        self.client = genai.Client(api_key=key)
        self.model = "gemini-2.5-pro" # Using available high quality model for extraction

    def extract_facts(self, extracted_text: Dict[int, str]) -> ExtractedFacts:
        # Combine text with page indicators
        full_text = "\\n\\n".join([f"--- PAGE {page_num} ---\\n{text}" for page_num, text in extracted_text.items()])
        
        prompt = f"{SYSTEM_PROMPT}\\n\\nHere is the document content:\\n{full_text}"
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ExtractedFacts
            ),
        )
        
        # Parse JSON into Pydantic model
        result_dict = json.loads(response.text)
        return ExtractedFacts(**result_dict)
