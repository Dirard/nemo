import os
import tempfile
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from app.model import transcribe_to_srt

app = FastAPI(title="NeMo Canary ASR/AST Service")

DEFAULT_SOURCE = os.environ.get("ASR_SOURCE_LANG", "en")
DEFAULT_TARGET = os.environ.get("ASR_TARGET_LANG", "en")


@app.post("/asr")
def asr_endpoint(
	file: UploadFile = File(...),
	source_lang: str = Form(DEFAULT_SOURCE),
	target_lang: str = Form(DEFAULT_TARGET),
):
	with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename or "audio")[1] or ".wav") as tmp:
		tmp.write(file.file.read())
		tmp_path = tmp.name
	text, srt = transcribe_to_srt(tmp_path, source_lang=source_lang, target_lang=target_lang)
	return JSONResponse({"text": text, "srt": srt})
