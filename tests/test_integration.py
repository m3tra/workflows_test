import asyncio

from idr.api import extract_fields_document, read_and_classify_document
from idr.llm.extraction_prompts import ALL_FIELDS
from idr.storage.blobs import get_document_from_file

path_ = "tests/data/77807_MONERIS - SERVIÇOS DE GESTÃO, SA - FT 1FA.2024L_1409.pdf"


def test_from_document():
    """calls llm and maybe form recognizer"""

    doc = get_document_from_file(path=path_)

    rnc_out = asyncio.run(read_and_classify_document(document=doc))

    assert rnc_out["file_path"] == path_

    assert rnc_out["acquirer_vat"] == "PT508453488"

    assert rnc_out["original_copy"] == "Y"

    ext_out = asyncio.run(extract_fields_document(document=doc))

    rnc_out_keys = set([k for k in rnc_out.keys()])
    ext_out_keys = set([k for k in ext_out.keys()])

    assert rnc_out_keys == set(
        [
            "file_path",
            "text",
            "scanned_copy",
            "original_copy",
            "has_atcud",
            "supplier_country",
            "supplier_vat",
            "supplier_name",
            "acquirer_vat",
            "acquirer_name",
            "document_type",
            "document_number",
            "qr_code_data",
            "valid_document",
            "classification_notes",
            "classification_json",
            "all_fields",
        ]
    )

    assert ext_out_keys == (
        set(ALL_FIELDS) - {"invoiced_items_description", "invoiced_items_quantity", "unit_price"}
        | {"invoiced_items", "missing_mandatory_fields", "missing_optional_fields"}
    )


if __name__ == "__main__":
    test_from_document()
