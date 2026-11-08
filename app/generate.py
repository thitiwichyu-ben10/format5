from pathlib import Path
from docx import Document
from docx.shared import Pt
from app.calculate import calculate_totals
ROOT = Path(__file__).resolve().parents[1]
def load_json(path):
    import json
    return json.loads(Path(path).read_text(encoding="utf-8"))
def replace_tokens(doc, mapping):
    for p in doc.paragraphs:
        for r in p.runs:
            for k,v in mapping.items():
                if k in r.text: r.text = r.text.replace(k, str(v))
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    for r in p.runs:
                        for k,v in mapping.items():
                            if k in r.text: r.text = r.text.replace(k, str(v))
def fill_template(data, company, output_path):
    doc = Document(ROOT / "templates" / "quotation_template.docx")
    mapping = {
      "{{COMPANY_NAME}}": company.get("company_name",""), "{{COMPANY_ADDRESS}}": company.get("address",""),
      "{{COMPANY_PHONE}}": company.get("phone",""), "{{COMPANY_EMAIL}}": company.get("email",""),
      "{{COMPANY_TAX_ID}}": company.get("tax_id",""), "{{COMPANY_LOGO_TEXT}}": company.get("logo_text",""),
      "{{BANK_DETAILS}}": company.get("bank_details",""), "{{AUTHORIZED_SIGNATORY}}": company.get("authorized_signatory",""),
      "{{QUOTATION_NUMBER}}": data["quotation_number"], "{{QUOTATION_DATE}}": data["quotation_date"],
      "{{VALID_UNTIL}}": data.get("valid_until",""), "{{CUSTOMER_NAME}}": data["customer"]["name"],
      "{{CUSTOMER_ADDRESS}}": data["customer"].get("address",""), "{{CUSTOMER_TAX_ID}}": data["customer"].get("tax_id",""),
      "{{CUSTOMER_CONTACT}}": data["customer"].get("contact",""), "{{CUSTOMER_PHONE}}": data["customer"].get("phone",""),
      "{{CUSTOMER_EMAIL}}": data["customer"].get("email",""), "{{SUBJECT}}": data.get("subject",""),
      "{{NOTES}}": data.get("notes",""), "{{PAYMENT_TERMS}}": data.get("payment_terms",""),
      "{{DELIVERY_TERMS}}": data.get("delivery_terms","")
    }
    totals = calculate_totals(data["items"], data.get("discount",0), data.get("vat_rate",7), data.get("vat_included",False))
    mapping.update({
      "{{SUBTOTAL}}": f'{totals["subtotal"]:,.2f}', "{{DISCOUNT}}": f'{totals["discount"]:,.2f}',
      "{{BEFORE_VAT}}": f'{totals["before_vat"]:,.2f}', "{{VAT_RATE}}": f'{totals["vat_rate"]:,.2f}',
      "{{VAT_AMOUNT}}": f'{totals["vat_amount"]:,.2f}', "{{GRAND_TOTAL}}": f'{totals["grand_total"]:,.2f}'
    })
    replace_tokens(doc, mapping)
    # Table index 1 is the line-item table (table 0 is customer/quotation metadata).
    item_table = doc.tables[1]
    for idx, item in enumerate(data["items"], start=1):
        cells = item_table.add_row().cells
        vals = [idx, item["description"], item.get("unit",""), item["quantity"],
                f'{float(item["unit_price"]):,.2f}',
                f'{float(item["quantity"])*float(item["unit_price"]):,.2f}']
        for cell, val in zip(cells, vals):
            cell.text = str(val)
            for p in cell.paragraphs:
                for r in p.runs:
                    r.font.name = "TH Sarabun New"; r.font.size = Pt(14)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    doc.save(output_path)
    return totals
