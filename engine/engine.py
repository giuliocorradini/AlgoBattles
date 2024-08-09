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

from .language import C, Cpp

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

    languages = {
        "c": C(),
        "c++": Cpp()
    }

    def __init__(self) -> None:
        self.configure()
        
    def configure(self):
        self.client = docker.from_env()
        self.workingdir = "abengine-workdir"
        os.makedirs(self.workingdir, exist_ok=True)
    
    def _save_source(self, chunk: Chunk, source, language):
        with open(os.path.join(chunk.absdir, language.source_file), "w") as fp:
            fp.write(source)

    def _check_source(self, langid, source, uid):
        """Check if the language id provided is supported by this engine, and decodes the source
        code from base64"""

        language = self.languages.get(langid)

        if language is None:
            logging.error("Unsupported language")
            self.signal("build", uid, None, "fail", errors="Unsupported language")
            return None, None

        source = base64.b64decode(source).decode("utf-8")
        return source, language

    def compile(self, langid, source, uid, *args, **kwargs):
        """Compile a source. Create container, and start compile process."""
        chunk = Chunk(uid, self.workingdir)
        source, language = self._check_source(langid, source, uid)
        self._save_source(chunk, source, language)

        worker = language.get_compiler(self.client, chunk.absdir)
        if not worker:
            raise ValueError("Cannot create worker compiler")

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
    
    def _put_tests_file(self, chunk, tests):
        with open(os.path.join(chunk, "tests.txt"), "w") as fp:
            json.dump(tests, fp)

    def test(self, chunk, uid, tests):
        """Test compiled binary against private test cases."""

        self._put_tests_file(chunk, tests)

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
