from decimal import Decimal
import pytest
from app.calculate import calculate_totals
from app.validate import validate_quotation
from pathlib import Path
import json
def test_totals():
    t=calculate_totals([{"quantity":2,"unit_price":100}],0,7,False)
    assert t["grand_total"] == Decimal("214.00")
def test_discount_limit():
    with pytest.raises(ValueError):
        calculate_totals([{"quantity":1,"unit_price":100}],101)
def test_example_schema():
    root=Path(__file__).resolve().parents[1]
    data=json.loads((root/"examples/quotation.json").read_text(encoding="utf-8"))
    assert validate_quotation(data)
