from docker.models.containers import Container

class Language():
    """This class defines a supported language, with its extension and the command
    to create a container with its compiler"""

    def __init__(self, name, extension):
        self.name = name
        self.extension = extension
        self.default_filename = "source"
    
    @property
    def source_file(self):
        return self.default_filename + self.extension

    def get_compiler(self, docker) -> Container:
        pass

class C(Language):
    def __init__(self):
        super().__init__("c", ".c")

    def get_compiler(self, docker, chunk) -> Container:
        return docker.containers.create(
            image = "gcc:11",
            command = "gcc -fpermissive -o artifact source.c",
            volumes = {chunk: {'bind': "/chunk", 'mode': 'rw'}},
            working_dir = "/chunk",
            network_disabled = True
        )
    
class Cpp(Language):
    def __init__(self):
        super().__init__("c++", ".cpp")

    def get_compiler(self, docker, chunk) -> Container:
        return docker.containers.create(
            image = "gcc:11",
            command = "g++ -fpermissive -o artifact source.cpp",
            volumes = {chunk: {'bind': "/chunk", 'mode': 'rw'}},
            working_dir = "/chunk",
            network_disabled = True
        )
    
class Java(Language):
    def __init__(self):
        super().__init__("java", ".java")
        self.default_filename = "Main"

    def get_compiler(self, docker, chunk) -> Container:
        return docker.containers.create(
            image = "eclipse-temurin:latest",
            command = f"javac {self.source_file}",
            volumes = {chunk: {'bind': "/chunk", 'mode': 'rw'}},
            working_dir = "/chunk",
            network_disabled = True
        )
