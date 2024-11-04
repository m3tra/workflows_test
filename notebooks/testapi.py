# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     custom_cell_magics: kql
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.11.2
#   kernelspec:
#     display_name: idr
#     language: python
#     name: python3
# ---

# %%
import asyncio
import json
import sys
from difflib import SequenceMatcher

import matplotlib.pyplot as plt
import numpy as np
import polars as pl
import requests

# %%
sys.path.append("..")
from idr.api import extract_fields_document, read_and_classify_document
from idr.storage.blobs import get_document

# %% [markdown]
# ## Get files list

# %%
base_url = "http://web-idr-docanalyser-dev.azurewebsites.net:80/"
model_body = {
    "file_url": "string",
    "file_path": "string",
}


# %%
base_path = "invoices/778"
doclist_response = requests.post(base_url + f"list_documents/{base_path}")
doclist_dict = json.loads(doclist_response.content)
print(doclist_dict["length"])

# %% [markdown]
# ## Define list manually

# %%
doclist_dict = {
    "path": "invoices/CTT - Correios de Portugal S.A. - FR CTT2023FR881079601_59 - PaidAlexandraNB-1720715855472393.pdf",
    "length": 1,
    "list": [
        "invoices/77805_LOCARENT - Companhia Portuguesa de Aluguer de Viaturas S.A. - 240101252493-1720438347956368.pdf",  # Switched values for supplier and acquirer, item desc is not complete
        "invoices/A2024005562_8980_UCISAEFCSucursalenPortugal_Febrero2024__F-17219238470200353.pdf",  # Switched values for supplier and acquirer
        "img_test/asnef.png",  # Same as previous but image
        "invoices/CTT - Correios de Portugal S.A. - FR CTT2023FR881079601_59 - PaidAlexandraNB-1720715855472393.pdf",  # 2a via -> documento original
        "invoices/77446_Dark Clarity, Lda - FT 1_243-17225054932489383.pdf",  # item desc is not correct
        "invoices/9882842797-17225041847198083.pdf",  # supplier_country é IE supp é microsoft
    ],
}

# %% [markdown]
# # Get documents
# (use before rnc or ext)

# %%
getdoc_jobs = []
for ex_doc_path in doclist_dict["list"]:
    getdoc_jobs.append(get_document(ex_doc_path))
docs = await asyncio.gather(*getdoc_jobs)

# %% [markdown]
# ## Run Read and Classify
# (rnc)

# %%
rnc_jobs = []


for ex_doc in docs:
    rnc_jobs.append(read_and_classify_document(document=ex_doc))

rnc_df = pl.DataFrame(await asyncio.gather(*rnc_jobs))


# %% [markdown]
# ### Explore Classification

# %%
rnc_df.drop("text")

# %%
print("/n".join(rnc_df[1]["text"][0]))

# %%
rnc_df.columns

# %%
rnc_df["qr_code_data"]

# %%

rnc_df[
    ["acquirer_name", "acquirer_vat", "supplier_name", "supplier_vat", "supplier_country", "original_copy", "has_atcud"]
]

# %%
print("\n".join(rnc_df["classification_notes"]))

# %% [markdown]
# ## Run extraction
# (ext)

# %%
ext_jobs = []

for ex_doc in docs:
    ext_jobs.append(extract_fields_document(document=ex_doc))

ext_responses = await asyncio.gather(*ext_jobs)
ext_df = pl.DataFrame(ext_responses)

# %% [markdown]
# ## Explore extraction

# %%
ext_responses[0].keys()

# %%
ext_fields = []
for ext_r in ext_responses:
    ext_fields.append(ext_r)
ext_fields_df = pl.DataFrame(ext_fields)

# %%
ext_fields_df

# %%
ext_fields_df.columns

# %%
ext_fields_df["unit_price"]

# %% [markdown]
# ## Similarity tests for output regularity

# %%


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


# %%
docs_numb = len(rnc_df)
text1_similarity = np.eye(docs_numb)
for i in range(docs_numb - 1):
    for j in range(i + 1, docs_numb):
        text1_similarity[i, j] = similar(rnc_df["classification_notes"][i], rnc_df["classification_notes"][j])
        text1_similarity[j, i] = text1_similarity[i, j]
plt.matshow(text1_similarity)

# %%
docs_numb = len(rnc_df)
text_similarity = np.eye(docs_numb)
for i in range(docs_numb - 1):
    for j in range(i + 1, docs_numb):
        text_similarity[i, j] = similar("/f".join(rnc_df["text"][i]), "/f".join(rnc_df["text"][j]))
        text_similarity[j, i] = text_similarity[i, j]
plt.matshow(text_similarity)

# %%
docs_numb = len(rnc_df)
text_similarity = np.eye(docs_numb)
for i in range(docs_numb - 1):
    for j in range(i + 1, docs_numb):
        text_similarity[i, j] = similar("/f".join(rnc_df["file_path"][i]), "/f".join(rnc_df["file_path"][j]))
        text_similarity[j, i] = text_similarity[i, j]
plt.matshow(text_similarity)

# %%
