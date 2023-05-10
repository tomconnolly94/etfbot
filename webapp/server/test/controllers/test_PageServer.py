#!/venv/bin/python

# external dependencies
import unittest
from flask.wrappers import Response
import mock

# internal dependencies
from server.controllers.PageServer import serveCustomCssModule, serveCustomJsModule, serveIndex, serveNodeModule, serveNodeModuleMapModule
from server.test.testUtilities import FakeFile


class Test_PageServer(unittest.TestCase):

    @mock.patch("builtins.open", create=True)
    def test_serveIndex(self, openMock):

        # config fake data
        fakeFileContent = "fakeFileContent"

        # config mocks
        openMock.return_value = FakeFile(fakeFileContent)

        content = serveIndex()

        self.assertEqual(fakeFileContent, content)


    @mock.patch("builtins.open", create=True)
    def test_serveNodeModule(self, openMock):

        # config fake data
        fakeFileContent = b"fakeFileContent"
        fakeModuleName = "fakeModuleName"
        fakeModuleNameJS = f"{fakeModuleName}.js"

        # config mocks
        openMock.return_value = FakeFile(fakeFileContent)

        actualResponse = serveNodeModule(fakeModuleNameJS)

        self.assertEqual([fakeFileContent], actualResponse.response)
        self.assertEqual("200 OK", actualResponse.status)
        self.assertEqual("text/javascript", actualResponse.mimetype)
        openMock.assert_called_with(f"client/node_modules/{fakeModuleName}/dist/{fakeModuleNameJS}", "r")


    @mock.patch("builtins.open", create=True)
    def test_serveCustomCssModule(self, openMock):

        # config fake data
        fakeFileContent = b"fakeFileContent"
        fakeModuleName = "fakeModuleName"
        fakeModuleNameCSS = f"{fakeModuleName}.css"

        # config mocks
        openMock.return_value = FakeFile(fakeFileContent)

        actualResponse = serveCustomCssModule(fakeModuleNameCSS)

        self.assertEqual([fakeFileContent], actualResponse.response)
        self.assertEqual("200 OK", actualResponse.status)
        self.assertEqual("text/css", actualResponse.mimetype)
        openMock.assert_called_with(f"client/css/{fakeModuleNameCSS}", "r")
        

    @mock.patch("builtins.open", create=True)
    def test_serveCustomJsModule(self, openMock):

        # config fake data
        fakeFileContent = b"fakeFileContent"
        fakeModuleName = "fakeModuleName"
        fakeModuleNameJS = f"{fakeModuleName}.js"

        # config mocks
        openMock.return_value = FakeFile(fakeFileContent)

        actualResponse = serveCustomJsModule(fakeModuleNameJS)

        self.assertEqual([fakeFileContent], actualResponse.response)
        self.assertEqual("200 OK", actualResponse.status)
        self.assertEqual("text/javascript", actualResponse.mimetype)
        openMock.assert_called_with(f"client/js/{fakeModuleNameJS}", "r")


    @mock.patch("builtins.open", create=True)
    def test_serveNodeModuleMapModule(self, openMock):

        # config fake data
        fakeFileContent = b"fakeFileContent"
        fakeModuleName = "fakeModuleName"
        fakeModuleNameJS = f"{fakeModuleName}.js"
        fakeModuleNameMapJS = f"{fakeModuleName}.map.js"
        fakeModuleNameMap = f"{fakeModuleName}.map"

        # config mocks
        openMock.return_value = FakeFile(fakeFileContent)

        actualResponse = serveNodeModuleMapModule(fakeModuleNameMapJS)

        self.assertEqual([fakeFileContent], actualResponse.response)
        self.assertEqual("200 OK", actualResponse.status)
        self.assertEqual("text/javascript", actualResponse.mimetype)
        openMock.assert_called_with(f"client/node_modules/{fakeModuleName}/dist/{fakeModuleNameMap}", "r")
