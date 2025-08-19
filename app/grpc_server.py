import os
import tempfile
from concurrent import futures

import grpc

from app.model import transcribe_to_srt
from app.generated import asr_pb2, asr_pb2_grpc

DEFAULT_SOURCE = os.environ.get("ASR_SOURCE_LANG", "en")
DEFAULT_TARGET = os.environ.get("ASR_TARGET_LANG", "en")


class AsrService(asr_pb2_grpc.AsrServiceServicer):
	def Transcribe(self, request, context):
		source_lang = request.source_lang or DEFAULT_SOURCE
		target_lang = request.target_lang or DEFAULT_TARGET
		# Сохраним байты во временный файл (многие аудио-стеки ожидают путь)
		with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(request.filename or "audio.wav")[1]) as tmp:
			tmp.write(request.audio)
			tmp_path = tmp.name
		text, srt = transcribe_to_srt(tmp_path, source_lang=source_lang, target_lang=target_lang)
		return asr_pb2.TranscribeResponse(srt=srt, text=text)


def serve(port: int = 50051):
	server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
	asr_pb2_grpc.add_AsrServiceServicer_to_server(AsrService(), server)
	server.add_insecure_port(f"[::]:{port}")
	server.start()
	server.wait_for_termination()
