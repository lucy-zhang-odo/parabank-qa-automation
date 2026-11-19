"""Money helpers. Amounts are compared as Decimal, never as float."""
from decimal import Decimal


def to_decimal(value) -> Decimal:
    """Convert an API number (float/int/str) to Decimal without float rounding noise."""
    return Decimal(str(value)).quantize(Decimal("0.01"))


def parse_ui_amount(text: str) -> Decimal:
    """Convert UI text such as '$1,515.50' or '-$25.00' to Decimal."""
    t = text.strip().replace(",", "").replace("$", "")
    return Decimal(t).quantize(Decimal("0.01"))
