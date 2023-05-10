#!/venv/bin/python

# external dependencies
from flask import Response

def serveIndex():
    f = open(f"client/html/index.html", "r")
    return f.read()


def serveNodeModule(module):
    moduleName = module.replace(".js", "")
    f = open(f"client/node_modules/{moduleName}/dist/{moduleName}.js", "r")
    
    return Response(response=f.read(),
                    status=200,
                    mimetype="text/javascript")


def serveCustomCssModule(module):
    moduleName = module.replace(".css", "")
    f = open(f"client/css/{moduleName}.css", "r")

    return Response(response=f.read(),
                    status=200,
                    mimetype="text/css")


def serveCustomJsModule(module):
    moduleName = module.replace(".js", "")
    f = open(f"client/js/{moduleName}.js", "r")

    return Response(response=f.read(),
                    status=200,
                    mimetype="text/javascript")


def serveNodeModuleMapModule(mapModule):
    moduleName = mapModule.replace(".js", "")
    moduleNameWOMap = moduleName.replace(".map", "")
    f = open(f"client/node_modules/{moduleNameWOMap}/dist/{moduleName}", "r")
    
    return Response(response=f.read(),
                    status=200,
                    mimetype="text/javascript")
