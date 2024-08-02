import asyncio
from rstream import Producer
import json
import base64

BUILD_STREAM_NAME = "build"
EXEC_STREAM_NAME = "testexec"
STREAM_RETENTION = 100000

async def send_build_message(producer):
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
    await producer.send(stream=BUILD_STREAM_NAME, message=json.dumps(message).encode('utf-8'))

async def send_build_message_cpp(producer):
    source_code = """
#include <iostream>
using namespace std;

int main() {
cout << "hello world" << endl;
return 0;
}
"""
    message = {
        "type": "build",
        "uid": "userX_puzzleY_attemptN1", # a unique user-problem-compile instance association
        "language": "c++",
        "source": base64.b64encode(source_code.encode('utf-8')).decode('utf-8')
    }
    await producer.send(stream=BUILD_STREAM_NAME, message=json.dumps(message).encode('utf-8'))


async def send_test_message(producer):
    message = {
        "type": "test",
        "uid": "userX_puzzleY_attemptN1", # a unique user-problem-compile instance association
    }
    await producer.send(stream=EXEC_STREAM_NAME, message=json.dumps(message).encode('utf-8'))


async def send_message_rmq(action):
    async with Producer(host="localhost", username="guest", password="guest") as producer:
        await producer.create_stream(BUILD_STREAM_NAME, exists_ok=True, arguments={"MaxLengthBytes": STREAM_RETENTION})
        await producer.create_stream(EXEC_STREAM_NAME, exists_ok=True, arguments={"MaxLengthBytes": STREAM_RETENTION})

        await action(producer)


if __name__ == "__main__":
    asyncio.run(send_message_rmq(send_test_message))
    #asyncio.run(send_message_rmq(send_build_message_cpp))