from abc import ABC, abstractmethod
from typing import Dict, Any
from schemas.extraction import ExtractedFacts

class BaseGemmaClient(ABC):
    @abstractmethod
    def extract_facts(self, extracted_text: Dict[int, str]) -> ExtractedFacts:
        """
        Extracts structured clinical facts from the provided text using the AI model.
        """
        pass
