#!/bin/bash
echo "building and testing code in python 3 image"

commitId=$(git log -1 --pretty=%H)
echo "$commitId for docker tag"
PYTHON_Version="3.7"
CMD_NAME="akamai query"

DOCKERNAME="aaalquis/akamai-query-docker"

echo "buidling dockername: $DOCKERNAME"
docker build -f python3.7.Dockerfile -t $DOCKERNAME:$commitId .

echo "tagging dockername: $DOCKERNAME"

echo "docker tag $DOCKERNAME:$commitId $DOCKERNAME:latest"
docker tag $DOCKERNAME:$commitId $DOCKERNAME:latest 

echo "docker tag $DOCKERNAME:$commitId $DOCKERNAME:v0.1"
docker tag $DOCKERNAME:$commitId $DOCKERNAME:v0.1

echo "docker tag $DOCKERNAME:$commitId $DOCKERNAME:py$PYTHON_Version"
docker tag $DOCKERNAME:$commitId $DOCKERNAME:py$PYTHON_Version 

echo "running docker run -v $(pwd):/cli-test --rm $DOCKERNAME python3 runtests.py"
docker run -v $(pwd):/cli-test --rm $DOCKERNAME:$commitId python3 runtests.py
