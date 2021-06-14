import time
import random

from functools import wraps

from cheroot.wsgi import Server as WSGIServer
from cheroot.wsgi import PathInfoDispatcher as WSGIPathInfoDispatcher

from flask import request
from flask import json

from flask import Flask
from flask import Response

from utils import setup_logger


LOG = setup_logger()

app = Flask(__name__)
GROUPS = []


def random_error_response(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        random_int = random.randint(0, 10)
        if random_int >= 4:
            return func(*args, **kwargs)
        if random_int <= 2:
            LOG.debug("connection timeout response")
            timeout = request.args.get(
                'timeout', default = 0.5, type = float
            )
            time.sleep(timeout)
            return Response(status=408)
        LOG.debug("random error response")
        return Response(status=500)
    return wrapper


@app.route('/v1/group/', methods=['POST'])
@random_error_response
def create():
    json_content = request.get_json(force=True)
    LOG.info(f"json data is: {json_content}")
    if 'groupId' in json_content:
        if json_content['groupId'] in GROUPS:
            LOG.info("group id already exists")
            return Response(status=400)
        GROUPS.append(json_content['groupId'])
        return Response(status=201)
    LOG.info("invalid request")
    return Response(status=500)

@app.route('/v1/group/<groupId>', methods=['GET'])
@random_error_response
def get(groupId):
    if groupId not in GROUPS:
        LOG.info("group not found")
        return Response(status=400)
    response_dict = {'groupId': groupId}
    return Response(
        status=200,
        response=json.dumps(response_dict) + '\n',
    )


if __name__ == '__main__':
    cherry_py_app = WSGIPathInfoDispatcher({'/': app})
    server = WSGIServer(('localhost', 5000), cherry_py_app)
    LOG.info("Starting the server")
    server.start()
