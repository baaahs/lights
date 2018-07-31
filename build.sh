#!/usr/bin/env bash

docker build . --tag=baaahs/light-server:latest
docker push baaahs/light-server:latest
