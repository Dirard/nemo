import os
from typing import List, Tuple

from nemo.collections.asr.models import ASRModel


_MODEL = None


def get_model() -> ASRModel:
	global _MODEL
	if _MODEL is None:
		# Используем переменные окружения для кэша HF
		hf_home = os.environ.get("HF_HOME", "/root/.cache/huggingface")
		os.environ.setdefault("HF_HOME", hf_home)
		# Загрузка мультизадачной модели (ASR/AST)
		_MODEL = ASRModel.from_pretrained(model_name="nvidia/canary-1b-v2")
		_MODEL.eval()
	return _MODEL


def s_to_srt_timestamp(seconds: float) -> str:
	# Преобразование секунд в формат SRT 00:00:00,000
	h = int(seconds // 3600)
	m = int((seconds % 3600) // 60)
	s = int(seconds % 60)
	ms = int(round((seconds - int(seconds)) * 1000))
	return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def segments_to_srt(segments: List[Tuple[float, float, str]]) -> str:
	# Генерация текста SRT из списка сегментов (start, end, text)
	lines: List[str] = []
	for idx, (start_s, end_s, text) in enumerate(segments, start=1):
		start_ts = s_to_srt_timestamp(start_s)
		end_ts = s_to_srt_timestamp(end_s)
		lines.append(str(idx))
		lines.append(f"{start_ts} --> {end_ts}")
		lines.append(text.strip())
		lines.append("")
	return "\n".join(lines)


def transcribe_to_segments(audio_paths: List[str], source_lang: str, target_lang: str) -> Tuple[str, List[Tuple[float, float, str]]]:
	model = get_model()
	# Для сегментных тайм-кодов используем timestamps=True.
	# В NeMo Canary word-level + segment-level для транскрипции, segment-level для перевода.
	outputs = model.transcribe(audio_paths, source_lang=source_lang, target_lang=target_lang, timestamps=True)
	if not outputs:
		return "", []
	out = outputs[0]
	text = getattr(out, "text", "")
	# При транскрипции: out.timestamp['segment'] — список со start/end/segment
	# При переводе: поддерживаются segment-level timestamps
	segments_meta = out.timestamp.get("segment") if hasattr(out, "timestamp") else None
	segments: List[Tuple[float, float, str]] = []
	if segments_meta:
		for seg in segments_meta:
			start = float(seg.get("start", 0.0))
			end = float(seg.get("end", 0.0))
			segment_text = seg.get("segment", "").strip()
			if segment_text:
				segments.append((start, end, segment_text))
	# Если по какой-то причине сегментов нет — создаём один блок целиком
	if not segments and text:
		segments = [(0.0, 0.0, text)]
	return text, segments


def transcribe_to_srt(audio_path: str, source_lang: str, target_lang: str) -> Tuple[str, str]:
	text, segments = transcribe_to_segments([audio_path], source_lang, target_lang)
	srt = segments_to_srt(segments)
	return text, srt
