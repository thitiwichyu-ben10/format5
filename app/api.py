import os, re, shutil, tempfile
from pathlib import Path
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
from app.generate import ROOT, fill_template, load_json
from app.validate import validate_quotation

app = FastAPI(title="Quotation Agent API", version="1.0.0",
              description="สร้างใบเสนอราคา DOCX จาก JSON และ Master Template")
def verify_key(authorization):
    expected = os.getenv("QUOTATION_API_KEY", "").strip()
    if expected:
        supplied = authorization[7:].strip() if authorization and authorization.lower().startswith("bearer ") else ""
        if supplied != expected:
            raise HTTPException(status_code=401, detail="Missing or invalid API key")

@app.get("/")
def root():
    return {"service":"quotation-agent-api","status":"running","docs":"/docs","health":"/health"}

@app.get("/health")
def health():
    return {"status":"ok"}

@app.post("/generate")
async def generate(request: Request, authorization: str | None = Header(default=None)):
    verify_key(authorization)
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Request body must be valid JSON")
    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="JSON body must be an object")
    try:
        validate_quotation(data)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    config = ROOT / "config" / "company.json"
    template = ROOT / "templates" / "quotation_template.docx"
    if not config.exists() or not template.exists():
        raise HTTPException(status_code=500, detail="Company config or DOCX template is missing")
    temp = Path(tempfile.mkdtemp(prefix="quotation-"))
    number = re.sub(r"[^A-Za-z0-9_-]", "_", data["quotation_number"])[:80] or "quotation"
    target = temp / f"quotation_{number}.docx"
    try:
        fill_template(data, load_json(config), target)
    except Exception as exc:
        shutil.rmtree(temp, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"Document generation failed: {exc}")
    return FileResponse(target,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=target.name,
        background=BackgroundTask(shutil.rmtree, temp, ignore_errors=True))
