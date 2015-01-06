# dockerfile for running the restuser service
# exposes /var/run/restuser as a volume,
# so host or other containers can create users in this container
# run with `docker run --name restuser -it restuser`

FROM ubuntu:latest

RUN apt-get update && apt-get install -y python3 python3-pip

RUN mkdir -p /var/run/restuser
VOLUME /var/run/restuser

RUN mkdir -p /srv/restuser
WORKDIR /srv/restuser
COPY requirements.txt /srv/restuser/
RUN pip3 install -r requirements.txt

COPY restuser.py /srv/restuser/

CMD ["python3", "/srv/restuser/restuser.py", "--socket=/var/run/restuser/restuser.sock"]
