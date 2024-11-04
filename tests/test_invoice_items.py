from idr.document.invoice_items import format_invoice_items

sample_extraction = {
    "document_due_date": "01/05/2024",
    "currency": "EUR",
    "invoiced_items_description": [
        "Renda Mensal - Prestação nº 34",
        "IPO - Prestação nº 34",
        "Fee - Prestação nº 34",
        "Serviços - Prestação nº 34",
        "Imposto Mensal - Prestação nº 34",
        "Garantia - Prestação nº 34",
        "Renda Mensal - Prestação nº 23",
        "Fee - Prestação nº 23",
        "Serviços - Prestação nº 23",
        "Imposto Mensal - Prestação nº 23",
        "Garantia - Prestação nº 23",
        "Renda Mensal - Prestação nº 10",
        "Fee - Prestação nº 10",
        "Serviços - Prestação nº 10",
        "Imposto Mensal - Prestação nº 10",
        "Garantia - Prestação nº 10",
    ],
    "invoiced_items_quantity": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
    "unit_price": [
        536.86,
        0.54,
        0.62,
        49.93,
        18.03,
        2.3,
        282.39,
        2.62,
        41.81,
        12.92,
        2.3,
        620.83,
        0.0,
        44.12,
        18.03,
        2.3,
    ],
    "acquiring_country": "PT",
    "payment_term": "PP",
    "po_number": "",
    "iban": "",
    "bic_swift": "",
    "extraction_comments": "The document is a Fatura-Recibo, hence the payment term is 'PP' (Pronto Pagamento). PO number, IBAN, and BIC/SWIFT were not found in the document.",
    "missing_mandatory_fields": [],
    "missing_optional_fields": ["po_number", "iban", "bic_swift"],
    "document_issue_date": "12/02/2019",
    "associated_invoice_number": "",
    "total_tax_amount": "375.05",
    "document_total_with_tax": "2012.62",
    "atcud_code": "SAMPLECODE",
    "vat_exempt_tax_base": "6.90",
    "vat_reduced_tax_base": "",
    "reduced_rate_vat_total": "",
    "intermediate_rate_vat_base": "",
    "intermediate_rate_vat_total": "",
    "standard_rate_vat_base": "1630.67",
    "standard_rate_vat_total": "375.05",
    "stamp_duty": "",
    "withholding_tax": "",
    "other_information": "",
}


def test_invoice_items_format():
    formatted = format_invoice_items(sample_extraction)
    expected_keys = set(sample_extraction.keys()) - {
        "invoiced_items_description",
        "invoiced_items_quantity",
        "unit_price",
    }
    expected_keys.add("invoiced_items")

    assert set(formatted.keys()) == expected_keys, f"Expected keys: {expected_keys}, but got {set(formatted.keys())}"

    invoiced_items: list[dict[str, str]] = formatted["invoiced_items"]  # type: ignore
    assert len(invoiced_items) == 16
    assert set(invoiced_items[0].keys()) == {"description", "quantity", "unit_price"}
