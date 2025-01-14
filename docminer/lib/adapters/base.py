from abc import ABC

class OCRAdapter(ABC):
    def __init__(self, key: str = None, api_endpoint: str = None):
        self.key = key
        self.api_endpoint = api_endpoint
        return

    def connect(self):
        # Placeholder
        return

    def process(self, file):
        # Placeholder
        return
    

class TestOCRAdapter(OCRAdapter):
    """Simulated OCR class for testing purposes."""
    
    def process(self, file):
        # Simulating multiple rows of structured data extracted from the PDF
        return [
            {"Name": "Foo", "Type": "Test"},
            {"Name": "Bar", "Type": "Example"}
        ]
