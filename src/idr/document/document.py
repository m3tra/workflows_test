from datetime import datetime

import magic
from loguru import logger

from idr.document.invoice_items import format_invoice_items
from idr.document.pdf_reader import read_pdf
from idr.llm.extraction_prompts import ALL_FIELDS

# QRcodes translation from SAF-T PT to camunda fields
QR2FIELDS = {
    "supplier_nif": "A",
    "acquirer_nif": "B",
    "acquiring_country": "C",
    "document_type": "D",
    "document_issue_date": "F",
    "document_number": "G",
    "atcud_code": "H",
    "supplier_country": "I1",
    "vat_exempt_tax_base": "I2",
    "vat_reduced_tax_base": "I3",
    "reduced_rate_vat_total": "I4",
    "intermediate_rate_vat_base": "I5",
    "intermediate_rate_vat_total": "I6",
    "standard_rate_vat_base": "I7",
    "standard_rate_vat_total": "I8",
    "stamp_duty": "M",
    "total_tax_amount": "N",
    "document_total_with_tax": "O",
    "withholding_tax": "P",
    # "hash_chars": "Q",
    # "certificate_number": "R",
    "other_information": "S",
}


class Document:
    """Class to store multiple documentation info

    Raises:
        ValueError: When the document type is not valid

    """

    #

    def __init__(self, id: str, url: str = ""):
        """Initiates the document class with the ID and default variables

        Args:
            id (str): file ID (working as it's path)
            url (str, optional): file url. Defaults to "".
        """
        self.doc_id: str = id
        self.url: str = url
        self.stream: bytes

        # each element should be a page (for image files or text-less PDF the fist element should be empty)
        self.text: list[str] = []

        self.is_image: bool = False
        self.qr_info: dict = {}
        self.valid: bool = False
        self.doc_type: str = ""
        self.fields = {}
        self.comments: list[str] = []

    def read_filetype(self) -> None:
        """Detects file type for further processing.
        TODO: THIS MODIFIES THE INPUT OBJECT

        Raises:
            ValueError: When the document type is not valid
        """

        file_type = magic.from_buffer(self.stream)

        if "PDF" in file_type:
            self.text = read_pdf(self.stream)
        elif "image" in file_type:
            self.text = [""]
        else:
            logger.error(f"Invalid document type: {file_type}")
            raise ValueError("Invalid document type. \n Valid types: PDF, jpeg, PNG)")

    def has_qr(self) -> bool:
        return len(self.qr_info) > 0

    def set_qr_code_data(self, qr_data: dict[str, str]) -> None:
        """Sets attributes for QR Code data found from OCR
        TODO: THIS MODIFIES THE INPUT OBJECT
        Args:
            qr_data: dictionary with valid qr code data
        Returns:
            None
        """
        self.qr_info = qr_data
        self.doc_type = qr_data["D"]
        self.valid = True

    def translate_qr_to_fields(self) -> dict:
        """Translates a decoded QR code in the SAF-T PT format to a dictionary with the corresponding camunda fields.

        Returns:
            dict: dictionary with the relevant information from the QR code in the camunda fields format
        """
        if not self.qr_info:
            return {}
        new_fields = {}
        for field, code in QR2FIELDS.items():
            if code in self.qr_info:
                new_fields[field] = self.qr_info[code]
        # Format QR code date correctly
        new_fields["document_issue_date"] = datetime.strptime(new_fields["document_issue_date"], "%Y%m%d").strftime(
            "%d/%m/%Y"
        )
        return new_fields

    def parse_classification_fields(self, class_completion: dict):
        """Parses the classification completion from the LLM model to update the Document fields.

        TODO: THIS MODIFIES THE INPUT OBJECT
        """
        self.valid = class_completion["valid_document"] == "Y"
        self.fields["valid_document"] = class_completion["valid_document"]
        self.fields["supplier_name"] = class_completion["supplier_name"]
        self.fields["acquirer_name"] = class_completion["acquirer_name"]
        self.comments.append(class_completion["classification_comments"])
        self.fields["classification_comments"] = class_completion["classification_comments"]

        if self.has_qr():
            self.fields["acquirer_vat"] = self.qr_info["C"] + self.qr_info["B"]
            # if invoice has QR code, supplier must have a portuguese fiscal entity
            self.fields["supplier_vat"] = "PT" + self.qr_info["A"]
            self.fields["supplier_country"] = "PT"

            self.doc_type = self.qr_info["D"]
            self.fields["document_type"] = self.qr_info["D"]
            self.fields["document_number"] = self.qr_info["G"]
            self.fields["has_atcud"] = "Y"
        else:
            self.fields["supplier_vat"] = class_completion["supplier_vat"]
            self.fields["acquirer_vat"] = class_completion["acquirer_vat"]
            self.fields["supplier_country"] = class_completion["supplier_country"]
            self.doc_type = class_completion["document_type"]
            self.fields["document_type"] = class_completion["document_type"]
            self.fields["document_number"] = class_completion["document_number"]
            self.fields["has_atcud"] = class_completion["has_atcud"]

    def postprocess_extraction_fields(self, extraction_completion: dict) -> dict:
        """Postprocess extraction data, formatting and adding some business rules
        TODO: THIS MODIFIES THE INPUT OBJECT

        Args:
            extraction_completion: dict of llm extraction completions

        Raises:
            ValueError: if required fields are missing

        Returns:
            formatted dict of extraction
        """
        if self.has_qr():
            qr_fields = self.translate_qr_to_fields()
        else:
            qr_fields = {}

        if "missing_mandatory_fields" not in extraction_completion:
            extraction_completion["missing_mandatory_fields"] = []
        if "missing_optional_fields" not in extraction_completion:
            extraction_completion["missing_optional_fields"] = []

        for field in ALL_FIELDS:  # we want to return empty fields even for the not existant for this kind of document
            if field not in extraction_completion:
                if field in qr_fields:
                    # Add fields if they are present in the QRcode but not in the extraction
                    extraction_completion[field] = qr_fields[field]
                else:
                    # Add empty if they are not defined anywhere (probabilly not valid for this document type)
                    extraction_completion[field] = ""
            elif extraction_completion[field] == "<missing>":
                # fields are explicitly flaged as <missing> by the LMM models, but we want to rewturn them as ""
                extraction_completion[field] = ""
                # verify if they are declared in a missing category
                if (
                    field not in extraction_completion["missing_mandatory_fields"]
                    and field not in extraction_completion["missing_optional_fields"]
                ):
                    raise ValueError(f"Field '{field}' was not flagged as missing in the dedicated variables")

        # Guarantee that all currency fields are formatted as string
        extraction_completion = {k: str(v) if isinstance(v, float) else v for k, v in extraction_completion.items()}

        extraction_completion = format_invoice_items(extraction_completion)
        return extraction_completion
