#!/bin/bash

set -ex

docker build -t kesteraernoudt/p1dobiss .
docker push kesteraernoudt/p1dobiss
