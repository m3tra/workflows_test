EXT_SYSTEM_PROMPT = """You are part of an OCR system that extracts information from invoices sent to a company.
The extracted documentation should be:
        - The answer should be in a JSON format like
        - Use mainly English and European Portuguese when necessary (e.g. when citing)."""

EXT_MAIN_PROMPT_TEMPLATE = """Extract the following data from the following document which is an invoice sent to the company. 

The field names are in quotation marks \" \" and notes about the fields are in parenthesis ( ) including explanation and format requirements if needed. 
Some value examples are sometimes provided within the explanation between ' '
Mandatory Fields are separated from the Array-like Fields and Optional Fields.
Mandatory Fields should be present in the document except for unprecedented errors.
Array-like Mandatory Fields must be written in a list format even if there is only one entry (all of these fields should have the same number of entries).
If you can't parse any of the mandatory fields, fill the value with "<missing>" and add them to a new variable called "missing_mandatory_fields".
Optional Fields must be present in the JSON but might be filled in with "<missing>" or if it is numeric '0.00' if no information can be parsed.
If you can't parse any of the optional fields, fill the value with the token "<missing>" and add them to a new variable called "missing_optional_fields".

Mandatory Fields:
{}

Array-like Mandatory Fields:
{}

Optional Fields:
{}

Extra Fields:
 - "missing_mandatory_fields" (list of the names of the fields that could not be parsed for mandatory fields, return an empty list if everything was parsed)
 - "missing_optional_fields" (list of the names of the fields that could not be parsed for optional fields, return an empty list if everything was parsed)

Extraction rules:
 - Make sure the "document_issue_date" and "document_due_date" differ by the number of days specified in the "payment_term" ('PP' means 0 days)
 - Use the value "<missing>" when the value can not be parsed for text fields or 0.00 in the number fields.
 - Number fields should be passed as a float with 2 decimal places and a '.' as the decimal separator (.2f).
 - The JSON keys are the names indicated above in quotation marks.
                
<document_content>
{}
</document_content>

JSON with extracted info:
"""
# prompts have a value for easy filtering for each document type
# FATURA: "FR" "FS"
# FATURA RECIBO: "FR"
# NOTA DE DÉBITO:  "NC"
# RECIBO: "RE"
# NOTA DE CRÉDITO: "NC"
# Info present in QR code: "QR"

EXT_MANDATORY_FIELDS = {
    ' - "document_issue_date" (Document issue date in the format DD/MM/YYYY)': {
        "FR",
        "FS",
        "FT",
        "ND",
        "NC",
        "RE",
        "QR",
    },
    ' - "document_due_date" (Date for the last day of payment in the DD/MM/YYYY format)': {"FR", "FS", "FT", "ND"},
    ' - "associated_invoice_number" (number of the associated invoice)': {"ND", "NC", "RE"},
    " - \"currency\" (a 3-letter currency code, use 'EUR' as default)": {"FR", "FS", "FT", "ND", "NC", "RE"},
    ' - "total_tax_amount" (total of the tax amounts, number in the .2f format and currency code)': {
        "FR",
        "FS",
        "FT",
        "ND",
        "NC",
        "RE",
        "QR",
    },
    ' - "document_total_with_tax" (total money, number in the .2f format)': {
        "FR",
        "FS",
        "FT",
        "ND",
        "NC",
        "RE",
        "QR",
    },
}

EXT_MANDATORY_ARRAY_FIELDS = {
    ' - "invoiced_items_description" (description of products or services provided in the document)': {
        "FR",
        "FS",
        "FT",
        "ND",
        "NC",
        "RE",
    },
    ' - "invoiced_items_quantity" (quantity of each article in a numeric format)': {"FR", "FS", "FT", "ND", "NC", "RE"},
    ' - "unit_price" (price of each article per unit without taxes)': {"FR", "FS", "FT", "ND", "NC", "RE"},
}


EXT_OPTIONAL_FIELDS = {
    ' - "acquiring_country" (2 letter code that represents the country of the receiver)': {
        "FR",
        "FS",
        "FT",
        "ND",
        "NC",
        "RE",
    },
    " - \"payment_term\" (either Pronto Pagamento or equivalent as 'PP', the number of days that the payment can be made e.g. '30 days' or '60 days', 'PP' if it is a Fatura-Recibo)": {
        "FR",
        "FS",
        "FT",
        "ND",
    },
    " - \"atcud_code\" (unique code with an alphanumeric group all uppercase, a dash '-', and a numeric group)": {
        "FR",
        "FS",
        "FT",
        "ND",
        "NC",
        "QR",
    },
    ' - "po_number"  (numbers or numbers of the purchase or service provided)': {"FR", "FS", "FT", "ND"},
    ' - "vat_exempt_tax_base" (Total amount of the VAT exempt tax base, number in the .2f, format)': {
        "FR",
        "FS",
        "FT",
        "ND",
        "NC",
        "RE",
        "QR",
    },
    ' - "vat_reduced_tax_base" (Total amount of the tax base subject to the reduced rate of VAT, number in the .2f format)': {
        "FR",
        "FS",
        "FT",
        "ND",
        "NC",
        "RE",
        "QR",
    },
    ' - "reduced_rate_vat_total" (Total amount of VAT at the reduced rate in the document, number in the .2f format)': {
        "FR",
        "FS",
        "FT",
        "ND",
        "NC",
        "RE",
        "QR",
    },
    ' - "intermediate_rate_vat_base" (Total amount of the tax base subject to the intermediate rate of VAT, number in the .2f format)': {
        "FR",
        "FS",
        "FT",
        "ND",
        "NC",
        "RE",
        "QR",
    },
    ' - "intermediate_rate_vat_total" (Total amount of VAT at the intermediate rate in the document, number in the .2f format)': {
        "FR",
        "FS",
        "FT",
        "ND",
        "NC",
        "RE",
        "QR",
    },
    ' - "standard_rate_vat_base" (Total amount of the tax base subject to the standard rate of VAT, number in the .2f format)': {
        "FR",
        "FS",
        "FT",
        "ND",
        "NC",
        "RE",
        "QR",
    },
    ' - "standard_rate_vat_total" (Total amount of VAT at the standard rate in the document, number in the .2f format)': {
        "FR",
        "FS",
        "FT",
        "ND",
        "NC",
        "RE",
        "QR",
    },
    ' - "stamp_duty" (Total amount of stamp duty in the document, number in the .2f format)': {
        "FR",
        "FS",
        "FT",
        "ND",
        "NC",
        "RE",
        "QR",
    },
    ' - "withholding_tax" (Total amount of withholding tax, number in the .2f format)': {
        "FR",
        "FS",
        "FT",
        "ND",
        "NC",
        "RE",
        "QR",
    },
    ' - "iban" (IBAN number that identifies a bank account, starts with a 2-letter country code and has 13 to 31 digits depending on the country of origin PT has 23)': {
        "FR",
        "FS",
        "FT",
        "ND",
        "NC",
        "RE",
    },
    ' - "bic_swift" (Code that identifies the bank or institution with 8 or 11 characters)': {
        "FR",
        "FS",
        "FT",
        "ND",
        "NC",
        "RE",
    },
    ' - "other_information" (other relevant info present in the document)': {"FR", "FS", "FT", "ND", "NC", "RE", "QR"},
    ' - "extraction_comments" (Relevant comments left by you about the document interpretation and information extraction)': {
        "FR",
        "FS",
        "FT",
        "ND",
        "NC",
        "RE",
    },
}

EXT_MAX_LENGTH = 30000

ALL_FIELDS = [
    "document_issue_date",
    "document_due_date",
    "associated_invoice_number",
    "currency",
    "total_tax_amount",
    "document_total_with_tax",
    "invoiced_items_description",
    "invoiced_items_quantity",
    "unit_price",
    "acquiring_country",
    "payment_term",
    "atcud_code",
    "po_number",
    "vat_exempt_tax_base",
    "vat_reduced_tax_base",
    "reduced_rate_vat_total",
    "intermediate_rate_vat_base",
    "intermediate_rate_vat_total",
    "standard_rate_vat_base",
    "standard_rate_vat_total",
    "stamp_duty",
    "withholding_tax",
    "iban",
    "bic_swift",
    "other_information",
    "extraction_comments",
]
