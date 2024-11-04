from azure.ai.documentintelligence.models import AnalyzeResult


def read_barcode_from_ocr(ocr_result: AnalyzeResult) -> dict[str, str]:
    """Read list of barcodes from ocr result, return the first valid one

    Args:
        ocr_result: result of Document Intelligence Analysis

    Returns:
        dict with first valid barcode data
    """
    qr_list = []
    for page in ocr_result.pages:
        if page.barcodes:
            for barcode in page.barcodes:
                if barcode.kind == "QRCode":
                    qr_list.append(barcode.value)

    qr_data = {}
    for qr_code in qr_list:
        if validate_qr_code(qr_code):
            qr_data = qr_code_to_dict(qr_code)
            break

    return qr_data


def validate_qr_code(qr_code: str) -> bool:
    """Check if qr code has a valid SAF-T PT format.

    Args:
        qr_code: qr code data in string form

    Returns:
        bool whether code is valid or not
    """
    qr_dict = qr_code_to_dict(qr_code)
    QR_FIELDS = {
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "H",
        "I1",
        "Q",
        "R",
    }
    # whether the qr_dict contains the set of minimal fields in a valid atcud qr
    return QR_FIELDS <= set(qr_dict)


def qr_code_to_dict(qr_code: str) -> dict[str, str]:
    """Parse qr code into dictionary

    Args:
        qr_code: qr code in string format

    Returns:
        qr code dictionary
    """
    if (":" in qr_code) and ("*" in qr_code):
        qr_dict = dict([pair.split(":") for pair in qr_code.split("*")])
    else:
        qr_dict = {}
    return qr_dict
