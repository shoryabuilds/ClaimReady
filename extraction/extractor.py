from ingestion.pdf_reader import ParsedDocument
from extraction.base import BaseGemmaClient
from extraction.gemma_client import GemmaClient
from schemas.extraction import ExtractedFacts

class PacketExtractor:
    """
    Coordinates multi-document text intake, Gemma-powered extraction,
    and Pydantic schema validation.
    """

    def __init__(self, client: BaseGemmaClient | None = None):
        self.client = client or GemmaClient()

    def extract_from_parsed_doc(self, doc: ParsedDocument) -> ExtractedFacts:
        pages_text = {p.page_number: p.text for p in doc.pages}
        return self.client.extract_packet_facts(doc.doc_name, pages_text)

    def extract_from_multiple_docs(self, docs: list[ParsedDocument]) -> ExtractedFacts:
        """
        Aggregates multiple PDF documents in a claim packet into unified ExtractedFacts.
        """
        combined_pages_text = {}
        global_page = 1
        doc_names = []

        for doc in docs:
            doc_names.append(doc.doc_name)
            for p in doc.pages:
                combined_pages_text[global_page] = f"[{doc.doc_name} Page {p.page_number}]\n{p.text}"
                global_page += 1

        primary_name = ", ".join(doc_names)
        return self.client.extract_packet_facts(primary_name, combined_pages_text)
