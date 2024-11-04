import importlib.metadata

from fastapi import FastAPI
from loguru import logger
from pydantic import BaseModel

from idr.logic import extract_fields_document, read_and_classify_document
from idr.storage.blobs import (
    get_blob_list,
    get_document,
)


class FileInput(BaseModel):
    file_url: str  # azure URL (not used just returned)
    file_path: str  # path to file inside the container


version = importlib.metadata.version("idr")


app = FastAPI(version=version)


@app.post("/list_documents/{path:path}")
async def list_document(path: str) -> dict:
    """API for listing docuemts in a path (useful for testing)

    Args:
        path (str): partial path to the directory to be listed in the blob storage (rooted in the documents container)

    Returns:
        dict: Input and result of the querie
            - path: partial path to the directory (input)
            - length: number of blobs in the directory
            - list: list of blobs in the directory
    """
    logger.info(f"Listing documents in {path}")
    try:
        blob_list = await get_blob_list(path)
    except Exception as e:
        logger.error(f"Error while listing {path}")
        raise e
    return {"path": path, "length": len(blob_list), "list": blob_list}


@app.post("/read_and_classify/")
async def read_and_classify(file: FileInput) -> dict:
    """API to scan and classify documents (used in camunda)
        - uses Document Intelligence
        - uses chatGPT 4o-mini

    Args:
        file (FileInput): json with url and path to the blob storage location of the file to be extracted
            - file_url: url to the file in the blob storage (currently not used)
            - file_path: path to the file in the blob storage (rooted in the documents container)

    Returns:
        dict: dict to be read as a json in camunda
            - file_url: url to the file in the blob storage (input)
            - file_path: path to the file in the blob storage (input)
            - text: full text of the document
            - has_atcud: flag indicating if the document has a QR code
            - scanned_copy: flag indicating if the document was scanned successfully
            - original_copy: flag indicating if the document was originally a copy
            - supplier_country: country of the supplier
            - supplier_vat: VAT of the supplier
            - supplier_name: name of the supplier
            - acquirer_vat: VAT of the acquirer
            - acquirer_name: name of the acquirer
            - document_type: type of document
            - document_number: number of document
            - qr_code_data: QR code data
            - valid_document: flag indicating if the document is valid
            - classification_notes: notes from classification
            - classification_json: dict of classification results
            - all_fields: dict of all fields extracted since the document was read
    """

    try:
        document = await get_document(file.file_path, file.file_url)
    except Exception as e:
        logger.error(f"Error while accessing the document, make sure the path is valid {file.file_path}")
        raise e

    out = await read_and_classify_document(document)
    out.update({"file_url": file.file_url})
    return out


@app.post("/extract_fields/")
async def extract_fields(file: FileInput) -> dict:
    """API to extract more fields from documents (used in camunda)
        - uses chatGPT 4

    Args:
        file (FileInput): json with url and path to the blob storage location of the file to be extracted
            - file_url: url to the file in the blob storage (currently not used)
            - file_path: path to the file in the blob storage (rooted in the documents container)

    Returns:
        dict: dict to be read as a json in camunda
            - file_url: url to the file in the blob storage (input)
            - file_path: path to the file in the blob storage (input)
            - extracted_fields: dict of fields extracted in this process
            - missing_mandatory_fields: list of missing mandatory fields
            - missing_optional_fields: list of missing optional fields
            - all_fields: dict of all fields extracted since the document was read
    """
    try:
        document = await get_document(file.file_path, file.file_url)
    except Exception as e:
        logger.error(f"Error while accessing the document, make sure the path is valid {file.file_path}")
        raise e

    out = await extract_fields_document(document)

    return {
        "file_url": file.file_url,
        "file_path": file.file_path,
        "extracted_fields": out,
        "missing_mandatory_fields": out["missing_mandatory_fields"],
        "missing_optional_fields": out["missing_optional_fields"],
        "all_fields": document.fields,
    }
