import os
import threading

import uvicorn

from app.grpc_server import serve as grpc_serve


REST_HOST = os.environ.get("REST_HOST", "0.0.0.0")
REST_PORT = int(os.environ.get("REST_PORT", "8000"))
GRPC_PORT = int(os.environ.get("GRPC_PORT", "50051"))


def run_rest():
	uvicorn.run("app.rest:app", host=REST_HOST, port=REST_PORT, reload=False, workers=1)


def run_grpc():
	grpc_serve(port=GRPC_PORT)


if __name__ == "__main__":
	grpc_thread = threading.Thread(target=run_grpc, daemon=True)
	grpc_thread.start()
	run_rest()
