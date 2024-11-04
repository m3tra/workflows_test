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
#     display_name: bctt_docs39
#     language: python
#     name: python3
# ---

# %%
import json
from pathlib import Path

import numpy as np
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


# %%
path = "../data/result/"
entries = Path(path)
file_list = []
for entry in entries.rglob("*"):
    file_list.append(str(entry))

# %%
json_list = []
for filename in file_list:
    if filename.endswith(".json"):
        with open(filename) as f:
            json_data = json.load(f)
            for i, action in enumerate(json_data.pop("Ações pedidas")):
                json_data[f"Ação pedida {i+1}"] = action
            json_list.append(json_data)

# %%
df = pd.DataFrame(json_list)
df = df.replace("n/A", np.NaN).set_index("File").reset_index()
df.to_excel("../data/result_excel.xlsx")


# %%
