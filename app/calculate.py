from decimal import Decimal, ROUND_HALF_UP
CENT = Decimal("0.01")
def money(v):
    return Decimal(str(v)).quantize(CENT, rounding=ROUND_HALF_UP)
def calculate_totals(items, discount=0, vat_rate=7, vat_included=False):
    subtotal = money(sum((Decimal(str(x["quantity"])) * Decimal(str(x["unit_price"])) for x in items), Decimal("0")))
    discount = money(discount)
    if discount < 0 or discount > subtotal:
        raise ValueError("ส่วนลดต้องอยู่ระหว่าง 0 ถึงยอดก่อนหักส่วนลด")
    taxable = money(subtotal - discount)
    rate = Decimal(str(vat_rate)) / Decimal("100")
    if vat_included:
        vat = money(taxable - taxable / (Decimal("1") + rate))
        before_vat = money(taxable - vat)
        grand = taxable
    else:
        before_vat = taxable
        vat = money(before_vat * rate)
        grand = money(before_vat + vat)
    return {"subtotal": subtotal, "discount": discount, "before_vat": before_vat,
            "vat_rate": money(vat_rate), "vat_amount": vat, "grand_total": money(grand)}
