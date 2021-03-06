#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

API_SERVER_IMAGE_NAME=test_server_image
API_CONSUMER_IMAGE_NAME=test_consumer_image
ROBOT_IMAGE_NAME=test_robot_image
IMAGE_TAG=latest

SUBNET_NAME=test_subnet

HOSTNAME_1=node01.app.internal.com
HOSTNAME_2=node02.app.internal.com
HOSTNAME_3=node03.app.internal.com

HOST_IP_1=192.168.2.1
HOST_IP_2=192.168.2.2
HOST_IP_3=192.168.2.3
CONSUMER_IP=192.168.2.4

CONTAINER_NAME_1=test_server_1
CONTAINER_NAME_2=test_server_2
CONTAINER_NAME_3=test_server_3
API_CONSUMER_CONTAINER_NAME=api_consumer
ROBOT_CONTAINER_NAME=robot_verification

docker network create --driver bridge --subnet 192.168.2.0/24 --gateway=192.168.2.10 ${SUBNET_NAME}
docker build -t ${API_SERVER_IMAGE_NAME}:${IMAGE_TAG} -f Dockerfile_Api_Server .
docker build -t ${API_CONSUMER_IMAGE_NAME}:${IMAGE_TAG} -f Dockerfile_Api_Consumer .
docker build -t ${ROBOT_IMAGE_NAME}:${IMAGE_TAG} -f Dockerfile_Robot .

docker run -dti --hostname ${HOSTNAME_1} --ip ${HOST_IP_1} --add-host ${HOSTNAME_1}:${HOST_IP_1} --name ${CONTAINER_NAME_1} --network ${SUBNET_NAME} ${API_SERVER_IMAGE_NAME}:${IMAGE_TAG}
docker run -dti --hostname ${HOSTNAME_2} --ip ${HOST_IP_2} --add-host ${HOSTNAME_2}:${HOST_IP_2} --name ${CONTAINER_NAME_2} --network ${SUBNET_NAME} ${API_SERVER_IMAGE_NAME}:${IMAGE_TAG}
docker run -dti --hostname ${HOSTNAME_3} --ip ${HOST_IP_3} --add-host ${HOSTNAME_3}:${HOST_IP_3} --name ${CONTAINER_NAME_3} --network ${SUBNET_NAME} ${API_SERVER_IMAGE_NAME}:${IMAGE_TAG}
set -x
docker run -dti -p 5001:5001 --name ${API_CONSUMER_CONTAINER_NAME} --ip ${CONSUMER_IP} --network ${SUBNET_NAME} --add-host ${HOSTNAME_1}:${HOST_IP_1} --add-host ${HOSTNAME_2}:${HOST_IP_2} --add-host ${HOSTNAME_3}:${HOST_IP_3} ${API_CONSUMER_IMAGE_NAME}:${IMAGE_TAG}
docker run -dti --name ${ROBOT_CONTAINER_NAME} --network ${SUBNET_NAME} --add-host ${HOSTNAME_1}:${HOST_IP_1} --add-host ${HOSTNAME_2}:${HOST_IP_2} --add-host ${HOSTNAME_3}:${HOST_IP_3} -v ${SCRIPT_DIR}/test:/robot/ ${ROBOT_IMAGE_NAME}:${IMAGE_TAG}
