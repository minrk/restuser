# dockerfile for testing the restuser server
# run with `docker run --volumes-from=restuser -it test`
# it should create a few users, and gracefully handle a failed user creation

FROM ubuntu:latest

RUN apt-get update && apt-get install -y python3 python3-pip

RUN mkdir -p /var/run/restuser
VOLUME /var/run/restuser

RUN mkdir -p /srv/restuser
WORKDIR /srv/restuser
COPY requirements.txt /srv/restuser/
RUN pip3 install -r requirements.txt

COPY tester.py /srv/restuser/

CMD ["python3", "/srv/restuser/tester.py"]
