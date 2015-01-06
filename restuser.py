"""Simple REST service for creating users with useradd"""

from __future__ import print_function

import json
import os
import sys
from pwd import getpwnam
from subprocess import Popen, PIPE

from tornado import gen, web
from tornado.log import app_log
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.netutil import bind_unix_socket
from tornado.options import define, parse_command_line, options

class UserHandler(web.RequestHandler):
    
    def get_user(self, name):
        """Get a user struct by name, None if no such user"""
        try:
            return getpwnam(name)
        except KeyError:
            return None
    
    def write_error(self, status_code, **kwargs):
        """Simple (not html) errors"""
        exc = kwargs['exc_info'][1]
        self.write(exc.log_message or str(error))
    
    def new_user(self, name):
        """Create a new user.
        
        Return the new user's struct
        """
        groups = self.settings.get('groups', None)
        shell = self.settings.get('shell', '/bin/bash')
        cmd = ['useradd', '-m', '-s', shell]
        if groups:
            cmd.extend(['-G', groups])
        # add -k SKEL_DIR to populate hone from skeleton dir
        cmd.append(name)
        
        app_log.info("Running %s", cmd)
        p = Popen(cmd, stderr=PIPE)
        _, err = p.communicate()
        if p.returncode:
            err = err.decode('utf8', 'replace').strip()
            raise web.HTTPError(400, err)
        return self.get_user(name)
    
    def post(self, name):
        user = self.get_user(name)
        if user is None:
            user = self.new_user(name)
        d = {}
        for attr in ['name', 'dir', 'shell', 'uid', 'gid']:
            d[attr] = getattr(user, 'pw_' + attr)
        self.finish(json.dumps(d))


def main():
    define('ip', default=None, help='IP to listen on')
    define('port', default=None, help='port to listen on')
    define('socket', default=None, help='unix socket path to bind (instead of ip:port)')
    define('groups', default='', help='comma separated group list for new users `students,other`')
    
    parse_command_line()
    
    if not options.socket and not (options.port):
        print("must specify at least socket or port", file=sys.stderr)
        sys.exit(1)
    
    app = web.Application([
        (r'/([^/]+)', UserHandler),
    ])
    if options.socket:
        socket = bind_unix_socket(options.socket, mode=0o600)
        server = HTTPServer(app)
        server.add_socket(socket)
    else:
        app.listen(options.port, options.ip)
    try:
        IOLoop.current().start()
    except KeyboardInterrupt:
        print("\ninterrupted\n", file=sys.stderr)
        return
    
    

if __name__ == '__main__':
    main()