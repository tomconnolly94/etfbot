#!/venv/bin/python

# external dependencies


# internal dependencies


class FakeFile():

    fileContent = ""

    def __init__(self, fakeFileContent):
        self.fileContent = fakeFileContent

    def __enter__(self):
        return self

    def __exit__(self, arg1, arg2, arg3):
        return self

    def read(self):
        return self.fileContent
