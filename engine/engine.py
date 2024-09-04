"""
The engine module interfaces with a Docker environment and is responsible for compiling and running the code
in a sandboxed (containerized) environment.

This module communicates with Django using a message broker.
"""

import os
import shutil
import logging
import docker
import base64
import json

import docker.models
import docker.models.containers

from .language import C, Cpp

from AlgoBattles import settings

class CompileTimeError(Exception):
    def __init__(self, logs):
        super().__init__(logs)
        self.logs = logs

class Chunk():
    def __init__(self, uid, workingdir):
        relative = os.path.join(workingdir, uid)
        self.__chunk = os.path.abspath(relative)

        os.mkdir(self.__chunk)

    @property
    def absdir(self):
        return self.__chunk
    
    def remove(self):
        shutil.rmtree(self.absdir)

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
        self.workingdir = settings.ENGINE_WORKDIR
        os.makedirs(self.workingdir, exist_ok=True)
    
    def _save_source(self, chunk: Chunk, source, language):
        with open(os.path.join(chunk.absdir, language.source_file), "w") as fp:
            fp.write(source)

    def _check_source(self, langid, source, uid):
        """Check if the language id provided is supported by this engine, and decodes the source
        code from base64"""

        langid = langid.lower()
        language = self.languages.get(langid)

        if language is None:
            logging.error("Unsupported language")
            self.signal("build", uid, None, "fail", errors="Unsupported language")
            return None, None

        source = base64.b64decode(source).decode("utf-8")
        return source, language

    def compile(self, langid: str, source: str, uid: str, *args, **kwargs):
        """Compile a source. Create container, and start compile process."""
        chunk = Chunk(uid, self.workingdir)
        source, language = self._check_source(langid, source, uid)
        self._save_source(chunk, source, language)

        errors = None

        worker = language.get_compiler(self.client, chunk.absdir)
        if not worker:
            raise ValueError("Cannot create worker compiler")

        try:
            worker.start()
            exit = worker.wait()
            logging.debug(f"Completed")

            if exit["StatusCode"] != 0:
                errors = worker.logs(stdout=False, stderr=True).decode('utf-8')

        except Exception as e:
            print(e)

        finally:
            worker.remove()
        
        if errors is None:
            return chunk.absdir
        
        else:
            chunk.remove()
            raise CompileTimeError(errors)
    
    def _put_tests_file(self, chunk, tests):
        with open(os.path.join(chunk, "tests.txt"), "w") as fp:
            json.dump(tests, fp)

    def test(self, chunk, uid, tests, timeout=0, memlimit=0):
        """Test compiled binary against private test cases."""

        self._put_tests_file(chunk, tests)

        worker = self.client.containers.create(
            image = "algobattles-solver",
            volumes = {chunk: {'bind': "/chunk", 'mode': 'rw'}},
            network_disabled = True,
            command=f"python solver.py {timeout} {memlimit}"
        )

        try:
            worker.start()
            exit = worker.wait()
            logging.debug(f"Completed")
            if exit["StatusCode"] == 0:
                results = worker.logs(stdout=True, stderr=False).decode('utf-8')
                logging.info(worker.logs(stderr=True, stdout=False).decode('utf-8'))
                ret = ("solver_success", results)
            else:
                logs = worker.logs(stdout=False, stderr=True).decode('utf-8')
                ret = ("solver_fail", logs)

        except Exception as e:
            logging.error(str(e))
            ret = ("engine_fail", e)

        finally:
            worker.remove()
            shutil.rmtree(chunk)

        return ret
    
    @classmethod
    def get_instance(cls):
        if not hasattr(cls, "instance"):
            cls.instance = Engine()

        return cls.instance
    