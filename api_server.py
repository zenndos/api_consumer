import time
import socket
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
    LOG.debug(f"json data is: {json_content}")
    if 'groupId' in json_content:
        if json_content['groupId'] in GROUPS:
            LOG.info("group id already exists")
            return Response(status=400)
        GROUPS.append(json_content['groupId'])
        return Response(status=201)
    LOG.info("invalid request")
    return Response(status=500)


@app.route('/v1/group/', methods=['DELETE'])
@random_error_response
def delete():
    json_content = request.get_json(force=True)
    LOG.debug(f"json data is: {json_content}")
    if 'groupId' in json_content:
        if json_content['groupId'] not in GROUPS:
            LOG.info("group not found")
            return Response(status=404)
        GROUPS.remove(json_content['groupId'])
        return Response(status=200)
    LOG.info("invalid request")
    return Response(status=500)


@app.route('/v1/group/<groupId>', methods=['GET'])
def get(groupId):
    if groupId not in GROUPS:
        LOG.info("group not found")
        return Response(status=400)
    response_dict = {'groupId': groupId}
    return Response(
        status=200,
        response=json.dumps(response_dict) + '\n',
    )


@app.route('/v1/group/all/', methods=['GET'])
def test_endpoint():
    """This is a test endpoint, only to be used for verification. This
       is not subhect to potential random error responses
    """
    return Response(
        status=200,
        response=json.dumps(GROUPS) + '\n',
    )


if __name__ == '__main__':
    cherry_py_app = WSGIPathInfoDispatcher({'/': app})
    hostname = socket.gethostname()
    port = 5000
    LOG.info(f"Starting the server on {hostname}:{port}")
    server = WSGIServer((hostname, port), cherry_py_app)
    server.start()
