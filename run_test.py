from ingestion.pdf_reader import PDFReader
from extraction.mock_client import MockGemmaClient
from verification.engine import VerificationEngine

def test_packet(filename):
    print(f"\n--- Processing {filename} ---")
    reader = PDFReader(filename)
    text = reader.extract_text()
    
    client = MockGemmaClient()
    facts = client.extract_facts(text)
    
    engine = VerificationEngine()
    findings = engine.run_all_rules(facts)
    
    print("Extracted Facts:")
    print(facts.model_dump_json(indent=2))
    print("\nFindings:")
    if not findings:
        print("None")
    for f in findings:
        print(f"- [{f.severity.value}] {f.rule_code}: {f.description}")

if __name__ == "__main__":
    test_packet("sample_data/packet1.pdf")
    test_packet("sample_data/packet2.pdf")
    test_packet("sample_data/packet3.pdf")
