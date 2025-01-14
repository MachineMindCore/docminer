import os
import re
import base64
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AzureOCRAdapter:
    """
    Adapter for Azure Document Intelligence (Form Recognizer) to extract specified key-value pairs from documents.
    """

    def __init__(self):
        """
        Initialize the AzureOCRAdapter with credentials and required keys.

        Args:
            required_keys (list): A list of keys to extract from the document.
        """
        self.endpoint = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")
        self.api_key = os.getenv("AZURE_FORM_RECOGNIZER_KEY_A")
        if not self.endpoint or not self.api_key:
            raise ValueError("Azure Form Recognizer key and endpoint must be set in the .env file.")
        self.client = DocumentAnalysisClient(self.endpoint, AzureKeyCredential(self.api_key))

    def set_keys(self, keys: str):
        self.raw_keys = keys
        self.required_keys = list(map(normalize_key, keys))
        return

    def process(self, file_path: str):
        """
        Process a document and extract specified key-value pairs.

        Args:
            file_path: The uploaded file path.

        Returns:
            dict: A dictionary containing extracted data for the document,
                where the values are lists of dictionaries (one per page).
        """
        try:
            with open(file_path, "rb") as doc:
                poller = self.client.begin_analyze_document(
                    "prebuilt-document",
                    document=doc
                )
            result = poller.result()

            # Initialize the result list for the document
            extracted_data = []

            # Iterate through pages in the document
            for page in result.pages:
                # Extract key-value pairs for this page
                page_data = dict.fromkeys(self.required_keys)
                for kv_pair in result.key_value_pairs:
                    if kv_pair.key and kv_pair.value and kv_pair.key.bounding_regions:
                        # Check if the key-value pair belongs to the current page
                        if kv_pair.key.bounding_regions[0].page_number == page.page_number:
                            key = kv_pair.key.content.strip()
                            key_normal = normalize_key(key)
                            value = kv_pair.value.content.strip()

                            if key_normal in self.required_keys:
                                page_data[key_normal] = value
                extracted_data.append(page_data)

            return extracted_data

        except Exception as e:
            print(f"Error processing document: {e}")
            return []




def normalize_key(key):
    """
    Convert a key like 'User Name' to 'username'.
    Removes spaces and non-alphanumeric characters, and converts to lowercase.

    Args:
        key (str): The input string to normalize.

    Returns:
        str: The normalized string.
    """
    key = re.sub(r'[^a-zA-Z0-9]', '', key)  # Remove non-alphanumeric characters
    return key.replace(" ", "").lower()