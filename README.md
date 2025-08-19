# ASR сервис на базе NVIDIA Canary-1B-v2 (NeMo)

Сервис предоставляет REST API (FastAPI) и gRPC для распознавания речи/перевода с тайм-кодами и возвращает результат в формате SRT субтитров.

Основан на модели `nvidia/canary-1b-v2` из NeMo/HuggingFace.

## Быстрый старт (Docker)

Требования: Docker 24+. Для ускорения — GPU (NVIDIA драйвер + `nvidia-container-toolkit`).

```bash
# Сборка образа
docker build -t nemo-asr:latest .

# Запуск (CPU)
docker run --rm -p 8000:8000 -p 50051:50051 nemo-asr:latest

# Запуск (GPU)
docker run --rm --gpus all -p 8000:8000 -p 50051:50051 nemo-asr:latest
```

## REST API

- POST /asr — `multipart/form-data` с полем `file`, опционально `source_lang`, `target_lang` (по умолчанию `en` → `en`).
- Ответ: JSON `{ "srt": "...", "text": "..." }`.

Пример:
```bash
curl -X POST "http://localhost:8000/asr" \
  -F "file=@sample.wav" \
  -F "source_lang=en" \
  -F "target_lang=en"
```

## gRPC

- Порт: 50051
- Proto: `protos/asr.proto`
- Метод: `Transcribe(TranscribeRequest) -> TranscribeResponse`

Сообщения:
- `TranscribeRequest`: `bytes audio`, `string filename`, `string source_lang`, `string target_lang`
- `TranscribeResponse`: `string srt`, `string text`

## Переменные окружения

- `ASR_SOURCE_LANG` — язык источника по умолчанию (en)
- `ASR_TARGET_LANG` — язык цели по умолчанию (en)
- `HF_HOME` — путь к кэшу HuggingFace (по умолчанию `/root/.cache/huggingface`)

## Замечания

- Модель крупная (~1B параметров). Для практической скорости рекомендуется GPU.
- При переводе (`target_lang != source_lang`) доступны сегментные тайм-коды. Для транскрипции доступны word/segment, сервис использует сегменты для генерации SRT.

## Ссылки

- Модель: [Hugging Face — nvidia/canary-1b-v2](https://huggingface.co/nvidia/canary-1b-v2)
