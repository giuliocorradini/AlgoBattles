"""
The engine module interfaces with a Docker environment and is responsible for compiling and running the code
in a sandboxed (containerized) environment.

This module communicates with Django using a message broker.
"""

import os
import logging
import docker
#from .connector import Connector

logging.basicConfig(level=logging.DEBUG)

class Engine():
    VOLUME_NAME = "algobattles-engine"

    def __init__(self) -> None:
        self.configure()
        
    def configure(self):
        self.client = docker.from_env()
        self.workingdir = "abengine-workdir"
        os.makedirs(self.workingdir, exist_ok=True)

        #self.connector = Connector()

    def new_chunk(self, uid):
        chunk = os.path.join(self.workingdir, uid)
        os.mkdir(chunk)

        return os.path.abspath(chunk)
    
    def save_source(self, chunk, source):
        with open(os.path.join(chunk, "source.c"), "w") as fp:
            fp.write(source)

    def handle_compile_request(self, request):
        logging.debug(f"Handling compile request from connector {request}")
        pass

    def compile(self, language, source, uid):
        """Compile a source. Create container, and start compile process."""
        chunk = self.new_chunk(uid)
        self.save_source(chunk, source)

        
        worker = self.client.containers.create(
            image = "gcc:latest",
            command = "gcc -o artifact source.c",
            volumes = {chunk: {'bind': "/chunk", 'mode': 'rw'}},
            working_dir = "/chunk",
            network_disabled = True
        )

        try:
            worker.start()
            exit = worker.wait()
            logging.debug(f"Completed")
            if exit["StatusCode"] == 0:
                self.signal("compile", uid, status="success")
            else:
                logs = worker.logs(stdout=False, stderr=True).decode('utf-8')
                self.signal("compile", uid, status="fail", errors=logs)

        except Exception as e:
            print(e)
            worker.remove()

    def signal(self, process, uid, **kwargs):
        """Signal the end of a process (compile, testrun) with a result and a value
        When compiling, if status is "success", this message will update the web client telling
        the program compiled, and will trigger a test run.
        """
    
        message = {
            "process": process,
            "uid": uid,
        }

        if process == "compile":
            message |= {
                "status": kwargs.get("status"), # success or fail
                "errors": kwargs.get("errors")  # compiler errors
            }

        #self.connector.signal(message)
        logging.debug(f"Message to connector {message}")
        if kwargs.get("status") == "fail":
            logging.debug(kwargs["errors"])

if __name__ == "__main__":
    e = Engine()
    source = """
#include <stdio.h>

int main() {
    printf(\"Test abengine\\n\");
    return 77;
}"""

    e.compile("C", source, "user1_puzzle1_attempt1")
    