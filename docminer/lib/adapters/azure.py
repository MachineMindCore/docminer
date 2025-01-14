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
            dict: A dictionary containing extracted data for the required keys.
        """
        try:
            #file_content = file.read()
            #encoded_content = base64.b64encode(file).decode("utf-8")
            with open(file_path, "rb") as doc:
                poller = self.client.begin_analyze_document(
                    "prebuilt-document",
                    document=doc
                )
            result = poller.result()

            # Initialize the result dictionary
            extracted_data = {key: None for key in self.required_keys}

            # Extract key-value pairs
            for kv_pair in result.key_value_pairs:
                if kv_pair.key and kv_pair.value:
                    key = normalize_key(kv_pair.key.content)
                    value = normalize_key(kv_pair.value.content)
                    if key in self.required_keys:
                        extracted_data[key] = value
                        print(key, value)

            return extracted_data

        except Exception as e:
            print(f"Error with Base64 processing: {e}")
            return dict()



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