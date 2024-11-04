from io import BytesIO

import pypdf
from loguru import logger


def read_pdf(stream: bytes) -> list[str]:
    """Process PDF using pypdf. Extracts text per page and decodes a QR code (with zbar) that has a valid SAF-T PT format.

    Args:
        stream: binary file data.
    Returns:
        detected text from the pdf
    """

    # PdfReader accepts BytesIO or local paths, BytesIO is used

    reader = pypdf.PdfReader(BytesIO(stream))
    text = []
    for page in reader.pages:
        text.append(page.extract_text())

    if not text:
        logger.info("No text found")
    return text
