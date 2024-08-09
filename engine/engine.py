"""
The engine module interfaces with a Docker environment and is responsible for compiling and running the code
in a sandboxed (containerized) environment.

This module communicates with Django using a message broker.
"""

import os
import logging
import docker
import base64
import json

import docker.models
import docker.models.containers

class Chunk():
    def __init__(self, uid, workingdir):
        relative = os.path.join(workingdir, uid)
        self.__chunk = os.path.abspath(relative)

        os.mkdir(self.__chunk)

    @property
    def absdir(self):
        return self.__chunk

class Engine():
    VOLUME_NAME = "algobattles-engine"

    def __init__(self) -> None:
        self.configure()
        
    def configure(self):
        self.client = docker.from_env()
        self.workingdir = "abengine-workdir"
        os.makedirs(self.workingdir, exist_ok=True)
    
    def __get_extension_for_language(self, language):
        if language == "c":
            return ".c"
        if language == "c++":
            return ".cpp"
    
    def _save_source(self, chunk: Chunk, source, language):
        ext = self.__get_extension_for_language(language)

        with open(os.path.join(chunk.absdir, "source" + ext), "w") as fp:
            fp.write(source)

    def _is_supported_language(self, lang):
        supported = set((
            "c", "c++"
        ))
        
        return lang.lower() in supported

    def _check_source(self, language, source, uid):
        """Check if request is a valid build request, then decodes source code (which is in base64 form)"""

        if not self._is_supported_language(language):
            logging.error("Unsupported language")
            self.signal("build", uid, None, "fail", errors="Unsupported language")
            return None

        source = base64.b64decode(source).decode("utf-8")
        return source

    def _c_compiler(self, chunk) -> docker.models.containers.Container:
        return self.client.containers.create(
            image = "gcc:latest",
            command = "gcc -o artifact source.c",
            volumes = {chunk: {'bind': "/chunk", 'mode': 'rw'}},
            working_dir = "/chunk",
            network_disabled = True
        )

    def _cpp_compiler(self, chunk) -> docker.models.containers.Container:
        return self.client.containers.create(
            image = "gcc:latest",
            command = "g++ -o artifact source.cpp",
            volumes = {chunk: {'bind': "/chunk", 'mode': 'rw'}},
            working_dir = "/chunk",
            network_disabled = True
        )

    def compile(self, language, source, uid, *args, **kwargs):
        """Compile a source. Create container, and start compile process."""
        chunk = Chunk(uid, self.workingdir)
        print(f"Chunky chunk {chunk}")
        source = self._check_source(language, source, uid)
        self._save_source(chunk, source, language)

        if language == "c":
            worker = self._c_compiler(chunk.absdir)
        elif language == "c++":
            worker = self._cpp_compiler(chunk.absdir)

        try:
            worker.start()
            exit = worker.wait()
            logging.debug(f"Completed")
            if exit["StatusCode"] == 0:
                self.signal("build", uid, chunk=chunk, status="success")
            else:
                logs = worker.logs(stdout=False, stderr=True).decode('utf-8')
                self.signal("build", uid, chunk=chunk, status="fail", errors=logs)

        except Exception as e:
            print(e)

        finally:
            worker.remove()

        return chunk.absdir

    def test(self, chunk, uid):
        """Test compiled binary against private test cases."""

        worker = self.client.containers.create(
            image = "algobattles-solver",
            volumes = {chunk: {'bind': "/chunk", 'mode': 'rw'}},
            network_disabled = True,
            command=f"python solver.py {1000000}"
        )

        try:
            worker.start()
            exit = worker.wait()
            logging.debug(f"Completed")
            if exit["StatusCode"] == 0:
                results = worker.logs(stdout=True, stderr=False).decode('utf-8')
                results = json.loads(results)
                self.signal("test", uid, chunk=chunk, status="success", results=results)
            else:
                logs = worker.logs(stdout=False, stderr=True).decode('utf-8')
                self.signal("test", uid, chunk=chunk, status="fail", errors=logs)

        except Exception as e:
            print(e)

        finally:
            worker.remove()

    def signal(self, process, uid, chunk, status, **kwargs):
        """Signal the end of a process (compile, testrun) with a result and a value
        When compiling, if status is "success", this message will update the web client telling
        the program compiled, and will trigger a test run.
        """
    
        message = {
            "type": process,
            "uid": uid,
            "chunk": chunk,
            "status": status # success or fail
        }

        if status == "fail":
            message |= {
                "errors": kwargs.get("errors")  # compiler errors
            }

        elif status == "success" and process == "test":
            message |= {"results": kwargs.get("results")}

        #self.connector.signal(message)
        logging.debug(f"Message to connector {message}")
        if status == "fail":
            logging.warn(kwargs["errors"])

if __name__ == "__main__":
    e = Engine()
    source = """
#include <stdio.h>

int main() {
    printf(\"Test abengine\\n\");
    return 77;
}"""

    e.compile("C", source, "user1_puzzle1_attempt1")
    