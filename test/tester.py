import json
import socket

from tornado import gen
from tornado.httpclient import AsyncHTTPClient, HTTPError
from tornado.ioloop import IOLoop
from tornado.netutil import Resolver


class UnixResolver(Resolver):
    """UnixResolver from https://gist.github.com/bdarnell/8641880"""
    def initialize(self, resolver, socket_path):
        self.resolver = resolver
        self.socket_path = socket_path
 
    def close(self):
        self.resolver.close()
 
    @gen.coroutine
    def resolve(self, host, port, *args, **kwargs):
        if host == 'unix+restuser':
            raise gen.Return([(socket.AF_UNIX, self.socket_path)])
        result = yield self.resolver.resolve(host, port, *args, **kwargs)
        raise gen.Return(result)


resolver = UnixResolver(resolver=Resolver(), socket_path='/var/run/restuser/restuser.sock')
AsyncHTTPClient.configure(None, resolver=resolver)
loop = IOLoop.current()
client = AsyncHTTPClient()


@gen.coroutine
def add_user(name):
    try:
        resp = yield client.fetch('http://unix+restuser/' + name, method='POST', body='{}')
    except HTTPError as e:
        print(e.response.code, e.response.body.decode('utf8', 'replace'))
        return
    user = json.loads(resp.body.decode('utf8', 'replace'))
    print(json.dumps(user, indent=1, sort_keys=True))


loop.run_sync(lambda : add_user('foo'))
loop.run_sync(lambda : add_user('bar'))
loop.run_sync(lambda : add_user('baz'))
loop.run_sync(lambda : add_user('invalid%20name'))
loop.run_sync(lambda : add_user('foo'))
