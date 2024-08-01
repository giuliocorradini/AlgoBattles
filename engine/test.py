import asyncio
from rstream import Producer
import json
import base64

async def send_message_rmq():
    async with Producer(host="localhost", username="guest", password="guest") as producer:

        STREAM_NAME = "build"
        STREAM_RETENTION = 100000

        await producer.create_stream(STREAM_NAME, exists_ok=True, arguments={"MaxLengthBytes": STREAM_RETENTION})

        source_code = """
#include <stdio.h>
int main() {
    printf("hello world\\n");
    return 0;
}
"""
        message = {
            "type": "build",
            "uid": "userX_puzzleY_attemptN", # a unique user-problem-compile instance association
            "language": "c",
            "source": base64.b64encode(source_code.encode('utf-8')).decode('utf-8')
        }
        await producer.send(stream=STREAM_NAME, message=json.dumps(message).encode('utf-8'))

if __name__ == "__main__":
    asyncio.run(send_message_rmq())