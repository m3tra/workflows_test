"""

Async methods to process documents

"""

import time

from azure.ai.documentintelligence.aio import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest, ContentFormat, DocumentAnalysisFeature
from loguru import logger
from openai import AsyncAzureOpenAI

from idr.document.document import Document
from idr.document.qr_codes import read_barcode_from_ocr
from idr.document.utils import parse_response_json
from idr.llm import call_chat_completions
from idr.llm.prompt_formatting import make_classification_prompt, make_extraction_prompt


async def async_read_ocr(document: Document, client: DocumentIntelligenceClient) -> tuple[str, dict[str, str]]:
    """Use OCR services to read text from an image asynchronously

    Args:
        document: Document to be read
        client: async client for the Document Intelligence servive in Azure

    Returns:
        tuple of document text and dictionary with qrcode data
    """

    ocr_start = time.time()

    logger.info(f"Starting OCR service for {document.doc_id=}")

    poller = await client.begin_analyze_document(
        model_id="prebuilt-layout",
        analyze_request=AnalyzeDocumentRequest(bytes_source=document.stream),
        features=[DocumentAnalysisFeature.BARCODES],
        output_content_format=ContentFormat.MARKDOWN,
    )
    ocr_result = await poller.result()
    logger.info(f"Extracted text length = {len(ocr_result.content)} in time = {time.time()-ocr_start}")

    qr_data = read_barcode_from_ocr(ocr_result)

    return ocr_result.content, qr_data


async def async_classify(document: Document, llm_client: AsyncAzureOpenAI, llm_model: str) -> dict[str, str]:
    """Use openAI ChatGPT services to classify document text asynchronously

    Args:
        document: Document to be classified
        llm_client: async client for openAI ChatGPT
        llm_model: model name to use for classification

    Returns:
        dict of the model's classification
    """
    logger.info(f"Classification starting for {document.doc_id=}")

    text = "\f".join(document.text)
    logger.info(f"Full text length: {len(text)}")

    prompt = make_classification_prompt(text, document.has_qr(), document.qr_info)
    completion = await call_chat_completions(
        llm_client=llm_client, llm_model=llm_model, text=text, prompt=prompt, process_name="Classification"
    )

    classification_completion = parse_response_json(completion)

    return classification_completion


async def async_extract(document: Document, llm_client: AsyncAzureOpenAI, llm_model: str) -> dict[str, str]:
    """Use openAI ChatGPT services to extract extra fields from document text, asynchronously

    Args:
        document: Document to be extracted
        llm_client: async client for openAI ChatGPT
        llm_model: model name to use for extraction

    Returns:
        dict of the model's extraction
    """
    logger.info(f"Extraction starting for {document.doc_id}")

    text = "\f".join(document.text)
    logger.info(f"Full text length: {len(text)}")

    prompt = make_extraction_prompt(text, document.doc_type, document.has_qr())

    completion = await call_chat_completions(
        llm_client=llm_client, llm_model=llm_model, text=text, prompt=prompt, process_name="Extraction"
    )

    extraction_completion = parse_response_json(completion)

    try:
        extraction_completion = document.postprocess_extraction_fields(extraction_completion)
    except Exception as e:
        logger.error(f"Error while postprocessing extraction fields: {e}")
        return {}
    return extraction_completion
