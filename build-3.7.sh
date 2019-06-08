#!/bin/bash
echo "building and testing code in python 3 image"

commitId=$(git log -1 --pretty=%H)
echo "$commitId for docker tag"
PYTHON_Version="3.7"
NAME="akamai-query"
CMD_NAME="akamai query"

DOCKERNAME="aaalquis/$NAME-py$PYTHON_Version"
echo $DOCKERNAME
docker build -f python3.7.Dockerfile -t $DOCKERNAME:$commitId .

#docker run -v $(pwd):/cli-test --rm $NAME  python3 runtests.py
#echo "docker run -v $(pwd):/cli-test --rm $NAME  /bin/bash"

echo 'running docker run -v $(pwd):/cli-test --rm $NAME python3 runtests.py'
docker run -v $(pwd):/cli-test --rm $NAME python3 runtests.py

echo 'running docker run -v $(pwd):/cli-test --rm $NAME $CMD_NAME help'
docker run -v $(pwd):/cli-test --rm $NAME $CMD_NAME help

#echo 'running docker run -v $(pwd):/cli-test --rm $NAME akamai lds help list'
#docker run -v $(pwd):/cli-test --rm $NAME $CMD_NAME help list

cat bin/$NAME | docker run --name testpy2$NAME -i --rm python:2.7.15-stretch 

docker rmi $DOCKERNAME:$commitId
