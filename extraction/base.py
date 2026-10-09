from abc import ABC, abstractmethod
from schemas.extraction import ExtractedFacts
from schemas.findings import Finding
from schemas.resolution import ResolutionDraft

class BaseGemmaClient(ABC):
    """
    Abstract adapter for Gemma inference.
    Isolates application pipeline from specific model runtimes (Google API, HF, or Mock).
    """

    @abstractmethod
    def extract_packet_facts(self, doc_name: str, pages_text: dict[int, str]) -> ExtractedFacts:
        """
        Extract structured medical and administrative entities with page-grounded evidence.
        """
        pass

    @abstractmethod
    def generate_resolution_draft(
        self,
        finding: Finding,
        patient_name: str | None,
        mrn: str | None
    ) -> ResolutionDraft:
        """
        Draft grounded retrieval ticket or clarification memo for a finding.
        """
        pass
