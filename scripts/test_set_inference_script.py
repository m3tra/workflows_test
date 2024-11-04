import asyncio
import os
import aiofiles
from pprint import pprint

from pathlib import Path
import requests
from dotenv import load_dotenv
from pprint import pprint
from idr.storage.blobs import read_blob, get_document_from_file
import polars as pl
from idr.api import extract_fields_document, read_and_classify_document
from idr.document.document import Document

load_dotenv()

DOCUMENT_FOLDER = "data_extractions"

async def save_file(filepath: str | Path, content: bytes):
    async with aiofiles.open(filepath, "wb") as f:
        await f.write(content)


async def download_files(doclist: list[str]):

    os.makedirs(DOCUMENT_FOLDER, exist_ok=True)

    getdoc_jobs = []
    for ex_doc_path in doclist:


        doc = read_blob(ex_doc_path)
        filename = Path(ex_doc_path).name

        save_path = Path(DOCUMENT_FOLDER, filename)
        getdoc_jobs.append(save_file(save_path, await doc))

    await asyncio.gather(*getdoc_jobs)


def download_sample_files():
    base_url = "http://web-idr-docanalyser-dev.azurewebsites.net:80/"
    base_path = "invoices/"
    doclist_response = requests.post(base_url + f"list_documents/{base_path}")
    doclist: list[str] = doclist_response.json()["list"]
    unique_doclist = list(set(doclist))
    unique_doclist = sorted(unique_doclist)

    asyncio.run(download_files(unique_doclist))

async def classify_documents(docs: list[Document]) ->list[dict]:
    rnc_jobs = []
    for ex_doc in docs:
        
        rnc_jobs.append(read_and_classify_document(document=ex_doc))
    class_results = await asyncio.gather(*rnc_jobs)
    return class_results

async def extract_doc_data(docs: list[Document]) ->list[dict]:
    rnc_jobs = []
    for ex_doc in docs:
        
        rnc_jobs.append(extract_fields_document(document=ex_doc))

    extraction_results = await asyncio.gather(*rnc_jobs)
    return extraction_results

if __name__ == "__main__":

    # Here to avoid downloading if already in disk
    DOWNLOAD_FILES = False
    if DOWNLOAD_FILES:
        download_sample_files()
        

    doc_files = os.listdir(DOCUMENT_FOLDER)
    doc_files = ["77805_LOCARENT - Companhia Portuguesa de Aluguer de Viaturas S.A. - 240101252493-1720438347956368.pdf", "MICROSOFT.pdf", "77446_Dark Clarity, Lda - FT 1_243-1720020767484724.pdf", ""]
    doc_files = ["MICROSOFT.pdf", "AGEAS Portugal, Companhia de Seguros, S.A. – 0273145490-1727369821358583.pdf"]

    doc_files = [f"{DOCUMENT_FOLDER}/{doc_file}" for doc_file in doc_files]
    docs = [get_document_from_file(doc_file) for doc_file in doc_files]

    class_result = asyncio.run(classify_documents(docs))
    pprint(class_result[0])
    breakpoint()
    ext_result = asyncio.run(extract_doc_data(docs))
    pprint(ext_result[0])
    breakpoint()
    df_class = pl.DataFrame(class_result)
    df_ext = pl.DataFrame(ext_result)

    pprint(class_result)
    print(docs[0].text[0])
    breakpoint()
