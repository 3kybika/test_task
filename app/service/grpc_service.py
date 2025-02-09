import platform
import grpc
from asyncio import Queue, Future
import logging
from fastapi import Depends

# ToDo motor for mogoDB?
import pkg_resources
from tinode_grpc import pb
from tinode_grpc import pbx

from app.service.utils import get_id

logger = logging.getLogger("custom")

APP_NAME = "tn_test_task"
APP_VERSION = "2.0.0b2"  # ?!
LIB_VERSION = pkg_resources.get_distribution("tinode_grpc").version
GRPC_VERSION = pkg_resources.get_distribution("grpcio").version
TINODE_HOST = "localhost:16060"

SECURE = False
SSL_HOST = None


def get_queue() -> Queue:
    queue_in = Queue()
    return queue_in


class GrpcService:
    def __init__(self, queue_in=Depends(get_queue)):
        self.queue_in: Queue = queue_in  # queue of queries for sending to tinode
        self.responses = {}  # dict by msg.id as key - responces from tinode
        self.secure = SECURE
        self.init_channel()

    async def client_generate(self):
        while True:
            msg = await self.queue_in.get()
            if msg is None:
                return
            yield msg

    async def client_post(self, msg):
        self.queue_in.put_nowait(msg)

    def handle_ctrl(self, message):
        # Handle responses form grpc server
        logger.info("Got msg {}: {}".format(message.id, message))
        msg_id = message.id
        if msg_id in self.responses:
            self.responses[msg_id].set_result(message)
            del self.responses[msg_id]

    async def message_loop(self):
        async for msg in self.stream:
            if msg.HasField("ctrl"):
                self.handle_ctrl(msg.ctrl)

    async def init_channel(self):
        logger.debug("Connecting...")

        channel = None
        if SECURE:
            opts = (("grpc.ssl_target_name_override", SSL_HOST),) if SSL_HOST else None
            channel = grpc.secure_channel(
                TINODE_HOST, grpc.ssl_channel_credentials(), opts
            )
        else:
            channel = grpc.insecure_channel(TINODE_HOST)

        # Call the server
        self.stream = pbx.NodeStub(channel).MessageLoop(self.client_generate())

        # Session initialization sequence: {hi}
        hi_msg = pb.ClientMsg(
            hi=pb.ClientHi(
                id=str(get_id()),
                user_agent="{}/{} ({}/{}) gRPC-python/{}+{}".format(
                    APP_NAME,
                    APP_VERSION,
                    platform.system(),
                    platform.release(),
                    LIB_VERSION,
                    GRPC_VERSION,
                ),
            ),
            ver=LIB_VERSION,
            lang="EN",
            background=False,
        )

        self.queue_in.put_nowait(hi_msg)
        self.message_loop(self.stream)

    async def send_msg(self, msg, await_res):
        msg_id = msg.id
        await self.queue_in.put((msg_id, msg))

        # create corouteine for response hanled
        if await_res:
            # ToDo timeout
            response_future = Future()
            self.responses[msg_id] = response_future

        return await response_future
