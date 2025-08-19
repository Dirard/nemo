# syntax=docker/dockerfile:1

FROM python:3.10-slim AS base

ENV DEBIAN_FRONTEND=noninteractive \
	PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PIP_NO_CACHE_DIR=1 \
	HF_HOME=/root/.cache/huggingface

RUN apt-get update && apt-get install -y --no-install-recommends \
	ffmpeg libsndfile1 build-essential ca-certificates curl sed \
	&& rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Скопируем исходники
COPY protos ./protos
COPY app ./app
COPY README.md ./

# Сгенерируем gRPC код
RUN python -m grpc_tools.protoc -I./protos \
	--python_out=./app/generated \
	--grpc_python_out=./app/generated \
	./protos/asr.proto && \
	echo "# Package init for generated stubs" > app/generated/__init__.py && \
	echo "from . import asr_pb2, asr_pb2_grpc" >> app/generated/__init__.py && \
	sed -i 's/^import asr_pb2 as asr__pb2/from \. import asr_pb2 as asr__pb2/' app/generated/asr_pb2_grpc.py

EXPOSE 8000 50051

CMD ["python", "-m", "app.main"]
