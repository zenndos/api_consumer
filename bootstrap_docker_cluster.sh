#!/bin/bash

IMAGE_NAME=http_test_server
IMAGE_TAG=latest

SUBNET_NAME=test_subnet

HOSTNAME_1=node01.app.internal.com
HOSTNAME_2=node02.app.internal.com
HOSTNAME_3=node03.app.internal.com

HOST_IP_1=192.168.2.1
HOST_IP_2=192.168.2.2
HOST_IP_3=192.168.2.3

CONTAINER_NAME_1=test_server_1
CONTAINER_NAME_2=test_server_2
CONTAINER_NAME_3=test_server_3

docker network create --driver bridge --subnet 192.168.2.0/24 --gateway=192.168.2.10 ${SUBNET_NAME}
docker build -t ${IMAGE_NAME}:${IMAGE_TAG} -f Dockerfile .

docker run -dti --hostname ${HOSTNAME_1} --add-host ${HOSTNAME_1}:${HOST_IP_1} --name ${CONTAINER_NAME_1} --network ${SUBNET_NAME} ${IMAGE_NAME}:${IMAGE_TAG}
docker run -dti --hostname ${HOSTNAME_2} --add-host ${HOSTNAME_2}:${HOST_IP_2} --name ${CONTAINER_NAME_2} --network ${SUBNET_NAME} ${IMAGE_NAME}:${IMAGE_TAG}
docker run -dti --hostname ${HOSTNAME_3} --add-host ${HOSTNAME_3}:${HOST_IP_3} --name ${CONTAINER_NAME_3} --network ${SUBNET_NAME} ${IMAGE_NAME}:${IMAGE_TAG}
