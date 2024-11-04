CLASS_SYSTEM_PROMPT = """You are part of an OCR system that classifies financial documents sent to the company.
The extracted documentation should be:
        - The answer should be in a JSON format like
        - Use mainly English and European Portuguese when necessary.
        - The supplier and acquirer are separate entities
        - The VAT number belongs to the named entity"""

CLASS_MAIN_PROMPT_TEMPLATE = """Classify the following document which is a financial document sent to the company. The classification class names are in quotation marks " ", and notes about what they mean are in parenthesis ( ).
Following that, the valid classification values are presented, including an explanation of what they mean:
"document_type": (2-letter code for a type of document)
        - 'FT' for Fatura or Invoice, 
        - 'FS' for Fatura Simplificada or Simplified Invoice,
        - 'FR' for Fatura-recibo or Invoice Reciept,
        - 'ND' for Nota de débito or Debit Note,
        - 'RE' for Recibo or Receipt
        - 'NC' for Nota de crédito
        - 'NV' for Não Válido or not valid
"document_number": (unique code with a 1 to 4 upper case letters group, an optional space, and a second group with digits and a slash '/' making a total max of 30 characters, normally the letters included are the document type)
"valid_document": (1 letter for the document validity, if it is a financial document of Financial transactions made for the company)
        - 'N' for No meaning Not valid
        - 'Y' for Yes meaning Valid
"original_copy": (1 letter to say if the original document is present, a duplicate or "segunda via" in Portuguese are also considered original. A reprint or a non-valid invoice should not be an original)
        - 'N' for No meaning it is a reprint or a non-valid invoice
        - 'Y' for Yes meaning the original or duplicate is present in the document (it has both an original and a duplicate it is still a "Y")
"has_atcud": (1 letter to say if the ATCUD code is present. The ATCUD is an unique code composed by an 8 alphanumeric characters group, a dash '-', and another group with numbers)
        - 'N' for No meaning it does not have an ATCUD code
        - 'Y' for Yes meaning it has an ATCUD code
"supplier_name" (Name of the supplier company/entity, normally the issuer of the document)
"supplier_vat" (9 digit VAT number - NIF in Portugal - of the supplier add the 2 letter country code in the beginning if not present)
"acquirer_name" (Name of the acquirer company/entity, normally the customer company that received the document)
"acquirer_vat" (9 digit VAT number - NIF in Portugal - of the acquirer add the 2 letter country code in the beginning if not present)
"supplier_country" (2-letter code that represents the country where the transaction was made, possibly present as the initial characters of the 'supplier_vat' field)
"classification_comments": (Justification on the document type and validity)
        - str type with the justification for the classification


Output rules:
        - The JSON keys are the names indicated above in quotation marks.
        - Text should be mainly in English or European Portuguese when necessary.

        
<document_content>
{}
</document_content>

JSON with extracted info:
"""
# When there is a QR code
CLASS_SIMPLE_PROMPT_TEMPLATE = """Classify the following document which is a financial document sent to the company. The classification class names are in quotation marks " ", and notes about what they mean are in parenthesis ( ).
Following that, the valid classification values are presented, including an explanation of what they mean:
"valid_document": (1 letter for the document validity, if it is a financial document of Financial transactions made for the company)
        - 'N' for No meaning Not valid
        - 'Y' for Yes meaning Valid
"original_copy": (1 letter to say if the original document is present, a duplicate or "segunda via" in Portuguese are also considered original. A reprint or a non-valid invoice should not be an original)
        - 'N' for No meaning it is a reprint or a non-valid invoice
        - 'Y' for Yes meaning the original or duplicate is present in the document (it has both an original and a duplicate it is still a "Y")
"supplier_name" (Name of the supplier company/entity, the issuer of the document; MUST HAVE VAT number or NIPC {}, usually shows up at the header and footer of the document)
"acquirer_name" (Name of the acquirer company/entity, the company that received the document, MUST HAVE VAT number or NIPC {})
"classification_comments": (Justification on the document type and validity)
        - str type with the justification for the classification

Output rules:
        - The JSON keys are the names indicated above in quotation marks.
        - Text should be mainly in English or European Portuguese when necessary.
        
<document_content>
{}
</document_content>

JSON with extracted info:
"""

CLASS_MAX_LENGTH = 30000
