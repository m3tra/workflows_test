from azure.ai.documentintelligence.aio import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from loguru import logger
from openai import AsyncAzureOpenAI

from idr.config import (
    BLOB_CONTAINER_MAPPING,
    FORM_ENDPOINT,
    FORM_KEY,
    openai_config_classifier,
    openai_config_extractor,
)
from idr.document import (
    Document,
    async_classify,
    async_extract,
    async_read_ocr,
)
from idr.storage.blobs import (
    write_blob,
)

doc_intelligence_client = DocumentIntelligenceClient(
    endpoint=FORM_ENDPOINT,  # type: ignore
    credential=AzureKeyCredential(FORM_KEY),  # type: ignore
)
llm_client_class = AsyncAzureOpenAI(
    azure_endpoint=openai_config_classifier.endpoint,
    api_key=openai_config_classifier.key,
    api_version=openai_config_classifier.version,
)
llm_client_ext = AsyncAzureOpenAI(
    azure_endpoint=openai_config_extractor.endpoint,
    api_key=openai_config_extractor.key,
    api_version=openai_config_extractor.version,
)


async def read_document(document: Document) -> str:
    """Helper function to scan document with PDF reader and Azure Document Intelligence

    Args:
        document (Document): Document to read

    Returns:
        str: Y or N depending on whether the document was scanned (does not have text in PDF)
    """
    document.read_filetype()

    text_length = len("".join(document.text))
    if text_length < 100:
        is_scanned = "Y"
    else:
        is_scanned = "N"

    logger.info(f"Scanned Document (Y/N): {is_scanned}. Enriching with OCR...")

    try:
        ocr_text, qr_data = await async_read_ocr(
            document,
            client=doc_intelligence_client,
        )
        document.text = [ocr_text]
        if qr_data:
            document.set_qr_code_data(qr_data)
    except Exception as e:
        raise e

    return is_scanned


async def classify_document(document: Document) -> dict:
    """Helper function to classify a document with ChatGPT 3.5-turbo

    Args:
        document (Document): Document to classify

    Returns:
        dict: classification dictionary
            - original_copy: str
            - has_atcud : str
            - supplier_country: str
            - supplier_vat: str
            - supplier_name: str
            - acquirer_vat: str
            - acquirer_name: str
            - document_type: str
            - document_number: str
            - qr_code_data: dict
            - valid_document: bool
            - classification_notes: str
            - classification_json: dict
            - all_fields: dict
    """

    try:
        class_completion = await async_classify(
            document,
            llm_client=llm_client_class,
            llm_model=openai_config_classifier.deployment,
        )
    except Exception as e:
        raise e

    document.parse_classification_fields(class_completion)

    return {
        "original_copy": class_completion["original_copy"],
        "has_atcud": document.fields["has_atcud"],
        "supplier_country": document.fields["supplier_country"],
        "supplier_vat": document.fields["supplier_vat"],
        "supplier_name": document.fields["supplier_name"],
        "acquirer_vat": document.fields["acquirer_vat"],
        "acquirer_name": document.fields["acquirer_name"],
        "document_type": document.doc_type,
        "document_number": document.fields["document_number"],
        "qr_code_data": document.qr_info,
        "valid_document": document.valid,
        "classification_notes": document.comments[-1],
        "classification_json": class_completion,
        "all_fields": document.fields,
    }


async def read_and_classify_document(document: Document) -> dict:
    """Read and classify document

    Outputs results to blobs named after document.file_path
    """

    file_path = document.doc_id

    try:
        is_scanned = await read_document(document)
    except Exception as e:
        logger.error(f"Error while scanning text from document {document.doc_id}")
        raise e
    try:
        await write_blob(file_path, document.text, BLOB_CONTAINER_MAPPING["text"])
        await write_blob(file_path, document.qr_info, BLOB_CONTAINER_MAPPING["qr_info"])
        if document.has_qr():
            await write_blob(file_path, document.qr_info, BLOB_CONTAINER_MAPPING["qr_info"])
    except Exception as e:
        logger.error(f"Error while writing scan text from document {file_path}")
        raise e

    try:
        class_completion = await classify_document(document)
    except Exception as e:
        logger.error("Error while classifying")
        raise e
    try:
        await write_blob(file_path, document.fields, BLOB_CONTAINER_MAPPING["fields"])
        await write_blob(file_path, document.comments, BLOB_CONTAINER_MAPPING["comments"])
    except Exception as e:
        logger.error("Error while writing classification results")
        raise e

    return {
        "file_path": file_path,
        "text": document.text,
        "scanned_copy": is_scanned,
        **class_completion,
    }


async def extract_fields_document(document: Document) -> dict:
    try:
        ext_completion = await async_extract(
            document,
            llm_client=llm_client_ext,
            llm_model=openai_config_extractor.deployment,
        )
    except Exception as e:
        logger.error("Error while extracting extra fields")
        raise e

    for field in ext_completion:
        document.fields[field] = ext_completion[field]

    try:
        await write_blob(document.doc_id, document.fields, BLOB_CONTAINER_MAPPING["fields"])
    except Exception as e:
        logger.error("Error while writing extraction results")
        raise e

    return ext_completion
