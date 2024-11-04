import json
import re

from loguru import logger

json_pattern = re.compile(r"{(?:[^{}]|(.*))*}")


def parse_response_json(response: str | None) -> dict[str, str]:
    """Parse LLM response to json dictionary

    Args:
        response: llm response, json string

    Returns:
        parsed json dictionary
    """
    try:
        completion_json = re.search(json_pattern, response).group()  # type: ignore
        extraction_completion = json.loads(completion_json)
    except Exception as e:
        logger.error(f"Error while encoding OpenAI completion: {e}")
        extraction_completion = {}

    return extraction_completion
