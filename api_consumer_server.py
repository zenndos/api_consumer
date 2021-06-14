import time
import requests
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
HOSTS = [
    'node01.app.internal.com',
    'node02.app.internal.com',
    'node03.app.internal.com'
]
PORT = 5000
ROLLBACK_ATTEMPT_LIMIT = 10


@app.route('/v1/group/', methods=['POST'])
def create():
    json_content = request.get_json(force=True)
    LOG.debug(f"json data is: {json_content}")
    if 'groupId' in json_content:
        response = create_group_on_all_hosts(json_content['groupId'])
        return response
    LOG.info("invalid request")
    return Response(status=500)


@app.route('/v1/group/', methods=['DELETE'])
def delete():
    json_content = request.get_json(force=True)
    LOG.debug(f"json data is: {json_content}")
    if 'groupId' in json_content:
        GROUPS.remove(json_content['groupId'])
        return Response(status=200)
    LOG.info("invalid request")
    return Response(status=500)


def create_group_on_all_hosts(groupId):
    hosts_for_rollback = []
    for host in HOSTS:
        try:
            response = create_group_request(groupId, host)
            if response.status_code == 201:
                LOG.info(f"Successfully created {groupId} on {host}")
                hosts_for_rollback.append(host)
            else:
                LOG.info(
                    "Unexpected response with {response.status_code} from "
                    "{host} while trying to create {groupId}"
                )
                create_group_rollback()
                return Response(status=response.status_code)
        except Exception:
            LOG.exception("Exception while creating group")
            create_group_rollback(groupId, hosts_for_rollback)
            return Response(status=500)
        return Response(status=200)


def delete_group_on_all_hosts(groupId):
    hosts_for_rollback = []
    for host in HOSTS:
        try:
            response = delete_group_request(groupId, host)
            if response.status_code == 200:
                LOG.info(f"Successfully deleted {groupId} on {host}")
                hosts_for_rollback.append(host)
            else:
                LOG.info(
                    "Unexpected response with {response.status_code} from "
                    "{host} while trying to delete {groupId}"
                )
                delete_group_rollback()
                return Response(status=response.status_code)
        except Exception:
            LOG.exception("Exception while creating group")
            delete_group_rollback(groupId, hosts_for_rollback)
            return Response(status=500)
        return Response(status=200)


def create_group_rollback(groupId, hosts_for_rollback):
    for host in hosts_for_rollback:
        rollback_the_host(create_group_request, groupId, host)


def rollback_the_host(rollback_func, groupId, host):
    for attempt in range(0, ROLLBACK_ATTEMPT_LIMIT):
        try:
            rollback_result = attempt_to_rollback(
                rollback_func, groupId, host
            )
            if rollback_result:
                LOG.info(
                    "Successful attempt number {attempt} to rollback {host}"
                )
                return

            LOG.info(
                "Unsuccessful attempt number {attempt} to rollback {host}"
            )
        except Exception:
            LOG.exception(
                "Exception while making attempt number {attempt} to "
                "rollback on {host}"
            )
    LOG.info("Failed to rollback {host}")


def attempt_to_rollback(rollback_func, groupId, host):
    rollback_response = rollback_func(groupId, host)
    if response.status_code in (200, 201,):
        get_response = get_group_request(groupId, host)
        if rollback_func == create_group_rollback:
            if get_response.status_code == 200:
                if groupId in get_response.json()["groupId"]:
                    return True
        elif rollback_func == delete_group_rollback:
            if response.status_code == 400:
                return True
    return False


def create_group_request(groupId, host):
    url = "{}:{}".format(host, PORT)
    response = requests.post(URL, json={"groupId": groupId})
    return response


def delete_group_request(groupId, host):
    url = "{}:{}".format(host, PORT)
    response = requests.delete(URL, json={"groupId": groupId})
    return response

def get_group_request(groupId, host):
    url = "{}:{}".format(host, PORT)
    response = requests.get(URL, json={"groupId": groupId})
    return response


if __name__ == '__main__':
    cherry_py_app = WSGIPathInfoDispatcher({'/': app})
    hostname = 'localhost'
    port = 5001
    LOG.info(f"Starting the server on {hostname}:{port}")
    server = WSGIServer((hostname, port), cherry_py_app)
    server.start()
