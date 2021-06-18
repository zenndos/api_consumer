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


LOG = setup_logger('api_consumer')

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
        response = delete_group_on_all_hosts(json_content['groupId'])
        return response
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
                    f"Unexpected response with {response.status_code} from "
                    f"{host} while trying to create {groupId}"
                )
                try:
                    rollback_hosts_with_function(
                        delete_group_request, groupId, hosts_for_rollback
                    )
                    return Response(status=304)
                except Exception:
                    LOG.exception("exception while rollback")
                return Response(status=500)
        except Exception:
            LOG.exception("Exception while creating group")
            create_group_rollback(groupId, hosts_for_rollback)
            return Response(status=304)
    return Response(status=201)


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
                    f"Unexpected response with {response.status_code} from "
                    f"{host} while trying to delete {groupId}"
                )
                rollback_hosts_with_function(
                    create_group_request, groupId, hosts_for_rollback
                )
                return Response(status=304)
        except Exception:
            LOG.exception("Exception while creating group")
            delete_group_rollback(groupId, hosts_for_rollback)
            return Response(status=304)
    return Response(status=200)


def rollback_hosts_with_function(rollback_function, groupId, hosts):
    for host in hosts:
        rollback_the_host(rollback_function, groupId, host)


def rollback_the_host(rollback_func, groupId, host):
    for attempt in range(1, ROLLBACK_ATTEMPT_LIMIT):
        try:
            is_attempt_succeeded = attempt_to_rollback(
                rollback_func, groupId, host
            )
            if is_attempt_succeeded:
                LOG.info(
                    f"Successful attempt number {attempt} to rollback {host}"
                )
                return
            LOG.info(
                f"Unsuccessful attempt number {attempt} to rollback {host}"
            )
        except Exception:
            LOG.exception(
                f"Exception while making attempt number {attempt} to "
                f"rollback on {host}"
            )
    LOG.info(f"Failed to rollback {host}")


def attempt_to_rollback(rollback_func, groupId, host):
    LOG.debug(f"attempting to rollback with {rollback_func.__name__}")
    rollback_response = rollback_func(groupId, host)
    if rollback_response.status_code in (200, 201,):
        get_response = get_group_request(groupId, host)
        if rollback_func == create_group_request:
            if get_response.status_code == 200:
                if groupId in get_response.json()["groupId"]:
                    return True
            LOG.debug(
                f"Expected 200 status code while quering: {groupId} "
                f"but got {get_response.status_code}"
            )
        elif rollback_func == delete_group_request:
            if get_response.status_code == 404:
                return True
            LOG.debug(
                f"Expected 404 status code while quering: {groupId} "
                f"but got {get_response.status_code}"
            )
    return False


def create_group_request(groupId, host):
    url = "http://{}:{}/v1/group/".format(host, PORT)
    response = requests.post(url, json={"groupId": groupId})
    return response


def delete_group_request(groupId, host):
    url = "http://{}:{}/v1/group/".format(host, PORT)
    response = requests.delete(url, json={"groupId": groupId})
    return response

def get_group_request(groupId, host):
    url = "http://{}:{}/v1/group/{}".format(host, PORT, groupId)
    response = requests.get(url, json={"groupId": groupId})
    return response


if __name__ == '__main__':
    cherry_py_app = WSGIPathInfoDispatcher({'/': app})
    hostname = '0.0.0.0'
    port = 5001
    LOG.info(f"Starting the server on {hostname}:{port}")
    server = WSGIServer((hostname, port), cherry_py_app)
    server.start()
