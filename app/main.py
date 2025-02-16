from contextlib import asynccontextmanager
import logging
import platform
from fastapi import APIRouter, FastAPI
import pkg_resources
import asyncio
from app import settings
from app.core.logger_setup import setup_logging
import time

import grpc
from tinode_grpc import pb
from tinode_grpc import pbx

from app.service.utils import get_id

# ToDo:
APP_NAME = "tn_test_task"
APP_VERSION = "2.0.0b2"  # ToDo: version?
LIB_VERSION = pkg_resources.get_distribution("tinode_grpc").version
GRPC_VERSION = pkg_resources.get_distribution("grpcio").version
TINODE_HOST = "tinode:16060"

SECURE = False
SSL_HOST = None

logger = logging.getLogger("App")
requests_queue = asyncio.Queue()
responses_map = {}

#for dependency
async def get_queue():
    return requests_queue


# tasks before app start and after
@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    # init_channel
    yield
    # Clean up if it is nessesary


def init_channel():
        logger.debug("Connecting...")

        channel = None
        if SECURE:
            opts = (("grpc.ssl_target_name_override", SSL_HOST),) if SSL_HOST else None
            channel = grpc.secure_channel(
                TINODE_HOST, grpc.ssl_channel_credentials(), opts
            )
        else:
            channel = grpc.insecure_channel(TINODE_HOST)

        def client_generate():
            async def asyncfunc():
               return await requests_queue.get()

            while True:
                msg = asyncio.run(asyncfunc())
                if msg is None:
                    continue
                logger.debug("Prepare to send msg {}".format(msg))
                yield msg

        # Session initialization sequence: {hi}
        hi_msg = pb.ClientMsg(
            hi=pb.ClientHi(
                id=str(get_id()), #ToDo - it's optional? Remove?
                user_agent="{}/{} ({}/{}) gRPC-python/{}+{}".format(
                    APP_NAME,
                    APP_VERSION,
                    platform.system(),
                    platform.release(),
                    LIB_VERSION,
                    GRPC_VERSION,
                ),
            ),
        )

        requests_queue.put_nowait(hi_msg)

        # Call the server
        stream = None
        retries = 0
        while stream is None and retries < 10:
            try:
                stream = pbx.NodeStub(channel).MessageLoop(client_generate())
            except Exception as e:
                retries += 1
                stream = None
                asyncio.sleep(10)

        for msg in stream:
            if msg.HasField("ctrl"):
                ctrl = msg.ctrl
                logger.info("Got msg {}: {}".format(msg, ctrl))
                # Handle responses form grpc server
                msg_id = None

                if msg_id in responses_map:
                    responses_map[msg_id].set_result(msg)
                    del responses_map[msg_id]


app = FastAPI(
    title=settings.project_name,
    openapi_url="/openapi.json",
    lifespan=lifespan,
    loglevel="debug",
)

# routers:
#api_router = APIRouter()
#api_router.include_router(auth_router)
from app.service.api import auth_router
app.include_router(auth_router)

if __name__ == "__main__":
    # TODO: migration mechanism?
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug", reload=True)
