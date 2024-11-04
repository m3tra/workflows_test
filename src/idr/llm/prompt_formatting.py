from loguru import logger
from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)

from idr.llm.classification_prompts import (
    CLASS_MAIN_PROMPT_TEMPLATE,
    CLASS_MAX_LENGTH,
    CLASS_SIMPLE_PROMPT_TEMPLATE,
    CLASS_SYSTEM_PROMPT,
)
from idr.llm.extraction_prompts import (
    EXT_MAIN_PROMPT_TEMPLATE,
    EXT_MANDATORY_ARRAY_FIELDS,
    EXT_MANDATORY_FIELDS,
    EXT_MAX_LENGTH,
    EXT_OPTIONAL_FIELDS,
    EXT_SYSTEM_PROMPT,
)


def make_classification_prompt(text: str, has_qr: bool, qr_info: dict[str, str]) -> list[ChatCompletionMessageParam]:
    """Format classification prompt

    Args:
        text: text to be classified
        has_qr: true if qr code was found
        qr_info: qr code info, empty dict if not found

    Returns:
        list of messages  (system + user) to send as prompt
    """
    if len(text) > CLASS_MAX_LENGTH:
        text = text[:CLASS_MAX_LENGTH]
    if has_qr:
        sup_vat = qr_info["A"]
        aq_vat = qr_info["B"]
        prompt = [
            ChatCompletionSystemMessageParam(role="system", content=CLASS_SYSTEM_PROMPT),
            ChatCompletionUserMessageParam(
                role="user", content=CLASS_SIMPLE_PROMPT_TEMPLATE.format(sup_vat, aq_vat, text)
            ),
        ]
        logger.info("Classification with a simple prompt")

    else:
        prompt = [
            ChatCompletionSystemMessageParam(role="system", content=CLASS_SYSTEM_PROMPT),
            ChatCompletionUserMessageParam(role="user", content=CLASS_MAIN_PROMPT_TEMPLATE.format(text)),
        ]
        logger.info("Classification with a regular prompt")
    return prompt


def make_extraction_prompt(
    text: str,
    doc_type: str,
    has_qr: bool,
) -> list[ChatCompletionMessageParam]:
    """Create a prompt for the ChatGPT model

    Args:
        mandatory_fields: mandatory fields for the model
        mandatory_array_fields: mandatory array fields for the model
        optional_fields: optional fields for the model
        text: text to be extracted

    Returns:
        list of prompt messages for the ChatGPT model
    """

    "Create a prompt for just the valid fields for the file_type of the document"

    mandatory_fields = "\n".join(
        [k for k, v in EXT_MANDATORY_FIELDS.items() if include_field_in_prompt(doc_type, has_qr, v)]
    )
    mandatory_array_fields = "\n".join(
        [k for k, v in EXT_MANDATORY_ARRAY_FIELDS.items() if include_field_in_prompt(doc_type, has_qr, v)]
    )
    optional_fields = "\n".join(
        [k for k, v in EXT_OPTIONAL_FIELDS.items() if include_field_in_prompt(doc_type, has_qr, v)]
    )

    if len(text) > EXT_MAX_LENGTH:  # limiting text length empirically to avoid getting to max prompts
        text = text[:EXT_MAX_LENGTH]

    prompt = [
        ChatCompletionSystemMessageParam(role="system", content=EXT_SYSTEM_PROMPT),
        ChatCompletionUserMessageParam(
            role="user",
            content=EXT_MAIN_PROMPT_TEMPLATE.format(
                mandatory_fields,
                mandatory_array_fields,
                optional_fields,
                text,
            ),
        ),
    ]
    return prompt


def include_field_in_prompt(doc_type: str, has_qr: bool, v: set[str]) -> bool:
    """Check if field is to be extracted

    Args:
        doc_type: document type from SAF-T PT
        has_qr: whether the document has a QR code
        v: set of valid document types that the field prompt is valid

    Returns:
        bool: whether the field prompt should be included
    """
    if has_qr:
        return (doc_type in v) and ("QR" not in v)
    else:
        return doc_type in v
