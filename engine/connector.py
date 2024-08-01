"""
The connector handles connections with the messaging broker. Listens for incoming code and build artifacts, enqueues compilation
artifacts for run and sends the results to the backend.
"""

import asyncio
import json

from rstream import (
    AMQPMessage,
    Consumer,
    MessageContext,
    ConsumerOffsetSpecification,
    OffsetType
)

import logging
from .engine import Engine

logging.basicConfig(level=logging.DEBUG)

def message_handler(coro):
    """Decorator that decodes a message and provide a dictionary object to the coroutine"""
    async def on_message(self, msg: AMQPMessage, message_context: MessageContext):
        stream = message_context.consumer.get_stream(message_context.subscriber_name)
        logging.debug(f"Got message: {msg} from stream {stream}")

        request = json.loads(msg)
        if type(request) is not dict:
            raise TypeError(f"Message {msg.properties.message_id} cannot be decoded into a dictionary")
        
        return await coro(self, request)

    return on_message
    


class Connector():
    """Handles messaging with backend"""
    BUILD_STREAM_NAME = "build"
    EXEC_STREAM_NAME = "testexec"
    STREAM_RETENTION = 100000

    def __init__(self, engine):
        self.consumer = Consumer(host="localhost", username="guest", password="guest")
        self.engine = engine

    async def _configure(self):
        """Subscribes to topics and connects callbacks"""

        await self.consumer.create_stream(stream=Connector.BUILD_STREAM_NAME, exists_ok=True, arguments={"MaxLengthBytes": Connector.STREAM_RETENTION})

        await self.consumer.subscribe(
            stream=Connector.BUILD_STREAM_NAME,
            callback=self.handle_build,
            offset_specification=ConsumerOffsetSpecification(OffsetType.FIRST, None)
        )

    @message_handler
    async def handle_build(self, request: dict):
        if request.get("type") != "build":
            logging.warning("Received a message that is not a build request")
            return False
        
        self.engine.handle_build(request)

    async def loop(self):
        await self.consumer.start()
        logging.debug("Consumer started")
        await self._configure()
        logging.debug("Consumer configured")
        await self.consumer.run()

if __name__ == '__main__':
    engine = Engine()
    connector = Connector(engine)
    asyncio.run(connector.loop())