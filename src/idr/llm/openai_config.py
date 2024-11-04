from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class AzureOpenAIConfig:
    endpoint: str
    key: str
    version: str
    deployment: str

    @classmethod
    def from_env(cls, suffix: str = "") -> AzureOpenAIConfig:
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT" + suffix)
        key = os.getenv("AZURE_OPENAI_API_KEY" + suffix)
        version = os.getenv("AZURE_OPENAI_VERSION" + suffix)
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT" + suffix)

        if endpoint is None or key is None or version is None or deployment is None:
            raise ValueError("Invalid Credentials")

        return cls(endpoint, key, version, deployment)
