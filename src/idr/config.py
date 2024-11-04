import os

from dotenv import load_dotenv

from idr.llm.openai_config import AzureOpenAIConfig

load_dotenv()

FORM_KEY = os.getenv("FORM_KEY")
FORM_ENDPOINT = os.getenv("FORM_ENDPOINT")

openai_config_classifier = AzureOpenAIConfig.from_env(suffix="_v4o_mini")
openai_config_extractor = AzureOpenAIConfig.from_env(suffix="_v4o")

BLOB_CONTAINER_MAPPING = {
    "stream": "DOC_CONTAINER",
    "qr_info": "QR_CONTAINER",
    "fields": "META_CONTAINER",
    "text": "TEXT_CONTAINER",
    "comments": "COMMENTS_CONTAINER",
}
