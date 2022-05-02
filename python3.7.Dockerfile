FROM aaalquis/akamaicli_naked:v0.1

## Test Harness

RUN python3 --version
RUN pip3 --version

RUN pip3 install coverage
RUN coverage --version

COPY . /cli-test
WORKDIR /cli-test

RUN git init && git config user.email "aaalquis@akamai.com" && git config user.name "Aaron Alquist" && git add . && git commit -m "Initial"

RUN pip3 install --upgrade pip

RUN cat requirements.txt
RUN pip3 install -r requirements.txt

RUN pip3 freeze
RUN ls

RUN python3 --version
RUN pip3 --version

RUN akamai install file://$PWD

RUN ls
