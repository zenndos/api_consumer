#!/bin/bash

CONTAINER_NAME_1=test_server_1
CONTAINER_NAME_2=test_server_2
CONTAINER_NAME_3=test_server_3
API_CONSUMER_CONTAINER_NAME=api_consumer
ROBOT_CONTAINER_NAME=robot_verification

API_SERVER_IMAGE_NAME=test_server_image
API_CONSUMER_IMAGE_NAME=test_consumer_image
ROBOT_IMAGE_NAME=test_robot_image
IMAGE_TAG=latest

SUBNET_NAME=test_subnet

docker rm -f ${CONTAINER_NAME_1}
docker rm -f ${CONTAINER_NAME_2}
docker rm -f ${CONTAINER_NAME_3}
docker rm -f ${API_CONSUMER_CONTAINER_NAME}
docker rm -f ${ROBOT_CONTAINER_NAME}

docker image rm -f ${API_SERVER_IMAGE_NAME}:${IMAGE_TAG}
docker image rm -f ${API_CONSUMER_IMAGE_NAME}:${IMAGE_TAG}
docker image rm -f ${ROBOT_IMAGE_NAME}:${IMAGE_TAG}
docker network rm ${SUBNET_NAME}
