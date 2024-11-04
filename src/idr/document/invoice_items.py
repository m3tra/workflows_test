"""
IDR 2024

Module to post-process invoice items
"""


def format_invoice_items(extraction_data: dict[str, str | list]) -> dict[str, str | list[dict]]:
    """Format list of invoice items from GenAI from dict of lists to list of dicts

    Expects invoiced items in format

    {
        ...,
        "invoiced_items_description": ['ITEM1','ITEM2', 'ITEM3'],
        "invoiced_items_quantity": [1,2,3],
        "unit_price": [6.10, 10.23, 100.24],
        ...
    }

    Args:
        extraction_data: invoice extraction content

    Returns:
        invoice extraction content in correct format:
    {
        ...,
        "invoiced_items": [
            'ds],
        ...
    }
    """
    descriptions = extraction_data.pop("invoiced_items_description")
    quantities = extraction_data.pop("invoiced_items_quantity")
    unit_prices = extraction_data.pop("unit_price")
    extraction_data["invoiced_items"] = [
        {"description": desc, "quantity": qty, "unit_price": price}
        for desc, qty, price in zip(descriptions, quantities, unit_prices)
    ]

    return extraction_data
