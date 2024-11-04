# IntelligentDocumentReader
API to use in the Innowave project to extract structured information from invoices and other financial documents.

May 2024.

Developed in Python 3.12.2


## Install environment

UV library is not necessary but recommended

`conda create -n py312idr python=3.12 -y`

`pip install uv`


### Installing lib magic and zbar on *nix


On mac os you can try
    `brew install libmagic`

and the linking trick

    https://stackoverflow.com/questions/71984213/macbook-m1raise-importerrorunable-to-find-zbar-shared-library-importerror

to install zbar.

On linux systems you need to install both libzbar0 and libmagic1
    `apt-get update && apt-get install libzbar0 -y && apt-get install libmagic1 -y`




## Create requirements

UV library is recommended but not necessary:

`uv pip compile requirements.in -o requirements.txt`


## Install requirements

UV library is not necessary but recommended

`uv pip install -r requirements.txt`


## Environment variables

Create an `.env` file to be able to run this API

```
MAX_DOC_LENGTH = 14500
```
The maximum length of the document text sent to the LLMs (each prompt has a different size limitation)


```
AZURE_OPENAI_ENDPOINT_v4 =  ****
AZURE_OPENAI_API_KEY_v4 = ****
AZURE_OPENAI_VERSION_v4 =  "2024-02-01"
AZURE_OPENAI_DEPLOYMENT_v4 =  "4-extractor"

AZURE_OPENAI_ENDPOINT_v35_turbo = ****
AZURE_OPENAI_API_KEY_v35_turbo = ****
AZURE_OPENAI_VERSION_v35_turbo =   "2024-02-01"
AZURE_OPENAI_DEPLOYMENT_v35_turbo =  "35t-classifier"
```
Connection to the LLM models (you need permission to access the endpoints and APIs ****)

v35_turbo is used for classification (ChatGPT 3.5-turbo)

v4 is used for extraction (ChatGPT 4)


```
FORM_ENDPOINT = ****
FORM_KEY = ****
```
Connection to the form recognizer (you need permission to access the endpoint and API ****)


```
STORAGE_CONNECTION_STRING = ****
DOC_CONTAINER = "documents"
QR_CONTAINER = "qr-code"
META_CONTAINER = "metadata"
TEXT_CONTAINER = "text"
COMMENTS_CONTAINER = "comments"
```
Connection to the Azure Blob Storage (you need permission to access connection string ****)


## Run locally

Make sure to have the necessary .env file before creating this image.

Select the proper python environment (with the installed requirements)

In linux there are dependencies on the linux packages `libzbar0` and`libmagic1` that you can install with `apt-get`

In the project dir:

`uvicorn api:app --host 0.0.0.0 --port 8000`

The API can then be accessed in the port `localhost:8000`.

## Docker 

Only runs in linux, for windows run in wsl (you need to enable docker in wsl)

### Build docker image

Make sure to have the necessary .env file before creating this image.

In the project dir:

`docker build . -t idr-fastapi:latest`

### Run docker container

You just need to run the previously created image.

`docker run -p 8000:80 idr-fastapi`

The API can then be accessed in the port `localhost:8000`.

<!--
Not implemented

## Test

uv pip install pytest pytest-cov

pytest tests -s --pdb --cov src/IntelligentDocumentReader -->