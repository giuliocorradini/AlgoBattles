from docker.models.containers import Container

class Language():
    """This class defines a supported language, with its extension and the command
    to create a container with its compiler"""

    def __init__(self, name, extension):
        self.name = name
        self.extension = extension

    def __eq__(self, value: str):
        """Compare language based on its name"""

        return self.name == value

    def get_compiler(self, docker) -> Container:
        pass

class C(Language):
    def __init__(self):
        super().__init__("c", ".c")

    def get_compiler(self, docker, chunk) -> Container:
        return docker.containers.create(
            image = "gcc:latest",
            command = "gcc -o artifact source.c",
            volumes = {chunk: {'bind': "/chunk", 'mode': 'rw'}},
            working_dir = "/chunk",
            network_disabled = True
        )
    
class Cpp(Language):
    def __init__(self):
        super().__init__("c++", ".cpp")

    def get_compiler(self, docker, chunk) -> Container:
        return docker.containers.create(
            image = "gcc:latest",
            command = "g++ -o artifact source.cpp",
            volumes = {chunk: {'bind': "/chunk", 'mode': 'rw'}},
            working_dir = "/chunk",
            network_disabled = True
        )