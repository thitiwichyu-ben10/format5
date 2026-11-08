# Quotation Agent API

FastAPI service รับ JSON ใบเสนอราคา ตรวจสอบข้อมูล คำนวณยอดเงิน และส่งกลับไฟล์ DOCX จาก Master Template

## Company data
ข้อมูลบริษัทเว้นว่างไว้ให้เติมเองใน `config/company.json` ส่วนหน้าตาเอกสารแก้ไขได้ที่ `templates/quotation_template.docx`

## Local run
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.api:app --reload
```
Docs: `http://localhost:8000/docs` | Health: `http://localhost:8000/health`

## API
- `GET /health` — readiness check
- `POST /generate` — ส่ง JSON ตาม `schemas/quotation.schema.json`; response เป็นไฟล์ DOCX

```bash
curl -X POST http://localhost:8000/generate \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  --data-binary @examples/quotation.json --output quotation.docx
```

ถ้าตั้ง environment variable `QUOTATION_API_KEY` ระบบจะบังคับ Bearer token; หากไม่ตั้งจะไม่บังคับ key
**แนะนำให้ตั้ง key บน Render ก่อนเปิดใช้งาน** และห้าม commit secret ลง GitHub

## Deploy Render
1. Push ทุกไฟล์ขึ้น GitHub โดย `render.yaml` ต้องอยู่ root ของ branch `main`
2. Render > New + > Blueprint > เลือก repository และ branch `main`
3. Render อ่าน `render.yaml` และสร้าง Web Service
4. ทดสอบ `https://<service>.onrender.com/health`
5. Render Dashboard > Service > Environment เพิ่ม `QUOTATION_API_KEY`

Start command: `uvicorn app.api:app --host 0.0.0.0 --port $PORT`

## Important
- Render Free อาจ sleep เมื่อไม่มี traffic
- DOCX ถูกสร้างใน temporary folder และลบหลังส่งกลับ ไม่ได้เก็บถาวร
- API ส่งออก DOCX เท่านั้น; PDF ต้องเพิ่ม LibreOffice หรือบริการแปลง PDF
- สูตรส่วนลด/VAT เป็นค่าเริ่มต้น ให้ฝ่ายบัญชียืนยันก่อนใช้จริง
- ก่อน production ควรเพิ่ม rate limiting, audit logs และ persistent storage

## Tests
```bash
pytest
```
