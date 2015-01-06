# RESTUser

A minimal REST API on HTTP + Unix sockets for creating users.

    POST unix:/path/to/restuser.sock:/username

to create a new user. Reply is a JSON dict of the pwd struct:

```json
{
 "dir": "/home/foo",
 "gid": 1000,
 "name": "foo",
 "shell": "/bin/bash",
 "uid": 1000
}
```

Run with:

    sudo mkdir /var/run/restuser
    sudo python restuser.py --socket=restuser.sock

Mount the socket in a docker container with:

    docker run -v restuser.sock:/var/run/restuser.sock -t yourimage

This will mount the host's `restuser.sock` as `/var/run/restuser.sock` on the container,
giving the container permission to create users on the host machine.


## Test

You can test both the server and a client in docker containers.

Build the images:

    docker build -t restuser .
    docker build -t restuser-test test

Run the server:

    docker run --name users -d -t restuser

Run the test client:

    docker run --volumes-from=users -it restuser-test

Verify the new users:

    docker exec -it users tail -n 5 /etc/passwd

Finally, violently destroy the server:

    docker rm -f users
