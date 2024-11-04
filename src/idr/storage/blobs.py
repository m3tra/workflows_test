import json
import os

from azure.storage.blob.aio import BlobServiceClient
from loguru import logger

from idr.config import BLOB_CONTAINER_MAPPING
from idr.document import Document


async def validate_credentials(env_conn_str, env_container) -> tuple[str, str]:
    conn_str = os.getenv(env_conn_str)
    container = os.getenv(env_container)

    if conn_str is None or container is None:
        raise ValueError("Unavailable blob connection")

    return conn_str, container


async def get_service_client(env_container: str) -> tuple[BlobServiceClient, str]:
    try:
        connection_string, container_name = await validate_credentials("STORAGE_CONNECTION_STRING", env_container)

        service_client = BlobServiceClient.from_connection_string(conn_str=connection_string)
        return service_client, container_name

    except Exception as e:
        logger.error("Error while connecting to Azure Services")
        raise e


async def get_blob_list(relative_path: str, env_container: str = "DOC_CONTAINER") -> list[str]:
    service_client, container_name = await get_service_client(env_container)
    blob_list = []
    async with service_client:
        container_client = service_client.get_container_client(container_name)
        async for blob in container_client.list_blobs(name_starts_with=relative_path):
            blob_list.append(blob.name)

    return blob_list


async def check_blob(blob_path: str, env_container: str = "DOC_CONTAINER") -> bool:
    try:
        service_client, container_name = await get_service_client(env_container)
        async with service_client:
            blob_client = service_client.get_blob_client(container_name, blob_path)
            return await blob_client.exists()
    except Exception as e:
        logger.error(f"Error while connecting to Azure Blob Container {env_container}")
        raise e


async def read_blob(blob_path: str, env_container: str = "DOC_CONTAINER") -> bytes:
    try:
        service_client, container_name = await get_service_client(env_container)
        async with service_client:
            container_client = service_client.get_container_client(container_name)
            async with container_client:
                blob_client = container_client.get_blob_client(blob_path)
                async with blob_client:
                    stream = await blob_client.download_blob()
                    data = await stream.readall()
        return data
    except Exception as e:
        logger.error(f"Error while reading a blob {blob_path} in the container {env_container}")
        raise e


async def write_blob(blob_path: str, content: dict | list | str, env_container: str = "DOC_CONTAINER") -> bool:
    try:
        service_client, container_name = await get_service_client(env_container)
        async with service_client:
            container_client = service_client.get_container_client(container_name)
            async with container_client:
                blob_client = container_client.get_blob_client(blob_path)
                async with blob_client:
                    json_data = json.dumps(content)
                    await blob_client.upload_blob(json_data, overwrite=True)
        return True
    except Exception as e:
        logger.error(f"Error while writing a blob {blob_path} in the container {env_container}")
        raise e


async def get_document(file_id: str, url: str = "") -> Document:
    """Get document from blob storage"""
    doc = Document(file_id, url=url)

    if await check_blob(file_id):
        doc.stream = await read_blob(file_id)
    else:
        raise ValueError("File not found")
    for datatype, env_container in list(BLOB_CONTAINER_MAPPING.items())[1:]:
        if await check_blob(file_id, env_container):
            data = await read_blob(file_id, env_container)
            setattr(doc, datatype, json.loads(data))

    if doc.text:
        if isinstance(doc.text, dict):
            doc.text = list(doc.text.values())
    if "document_type" in doc.fields:
        doc.doc_type = doc.fields["document_type"]
    if "valid_document" in doc.fields:
        doc.valid = doc.fields["valid_document"]
    return doc


def get_document_from_file(path: str) -> Document:
    """simple method to load from file, no validation"""

    doc = Document(id=path, url="")
    with open(path, "rb") as file:
        doc.stream = file.read()

    return doc
