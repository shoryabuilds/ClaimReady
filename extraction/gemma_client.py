import os
import json
from extraction.base import BaseGemmaClient
from extraction.mock_client import MockGemmaClient
from extraction.prompts import (
    EXTRACTION_SYSTEM_PROMPT,
    DRAFT_RETRIEVAL_TICKET_PROMPT,
    DRAFT_CLARIFICATION_MEMO_PROMPT
)
from schemas.extraction import ExtractedFacts
from schemas.findings import Finding
from schemas.resolution import ResolutionDraft

class GemmaClient(BaseGemmaClient):
    """
    Live Gemma / GenAI inference client with automatic fallback
    to deterministic mock client when offline or unconfigured.
    """

    def __init__(self, api_key: str | None = None, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        self.model_name = model_name
        self._fallback_client = MockGemmaClient()
        self._genai_client = None

        if self.api_key:
            try:
                from google import genai
                self._genai_client = genai.Client(api_key=self.api_key)
            except Exception:
                self._genai_client = None

    def extract_packet_facts(self, doc_name: str, pages_text: dict[int, str]) -> ExtractedFacts:
        if not self._genai_client:
            return self._fallback_client.extract_packet_facts(doc_name, pages_text)

        try:
            # Build structured prompt with document text
            pages_formatted = "\n\n".join(
                f"--- PAGE {p_num} ---\n{text}" for p_num, text in pages_text.items()
            )
            prompt = (
                f"{EXTRACTION_SYSTEM_PROMPT}\n\n"
                f"DOCUMENT: {doc_name}\n\n"
                f"{pages_formatted}\n\n"
                f"Extract structured facts matching the Pydantic ExtractedFacts schema in JSON."
            )

            response = self._genai_client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )
            data = json.loads(response.text)
            return ExtractedFacts(**data)
        except Exception:
            # Safe degradation to mock client ensuring audit pipeline continuity
            return self._fallback_client.extract_packet_facts(doc_name, pages_text)

    def generate_resolution_draft(
        self,
        finding: Finding,
        patient_name: str | None,
        mrn: str | None
    ) -> ResolutionDraft:
        if not self._genai_client:
            return self._fallback_client.generate_resolution_draft(finding, patient_name, mrn)

        try:
            # Format prompt and invoke model
            prompt = DRAFT_RETRIEVAL_TICKET_PROMPT.format(
                title=finding.title,
                description=finding.description,
                patient_name=patient_name or "Patient",
                mrn=mrn or "N/A",
                evidence_quote=finding.evidence[0].evidence_quote if finding.evidence else "N/A",
                source_document=finding.evidence[0].source_document if finding.evidence else "Packet",
                source_page=finding.evidence[0].source_page if finding.evidence else 1
            )
            response = self._genai_client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            body = response.text.strip()
            draft = self._fallback_client.generate_resolution_draft(finding, patient_name, mrn)
            draft.body = body
            return draft
        except Exception:
            return self._fallback_client.generate_resolution_draft(finding, patient_name, mrn)
