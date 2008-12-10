#!/usr/bin/env python

# Port to run on
PORT=8005

# Script to serve up the contents of the out/ directory.

import os, sys, time
from BaseHTTPServer import *
from SimpleHTTPServer import *


class CDevNull:
    """Replacement for os.devnull which crashes the server for some reason"""
    def write(*args):
        pass
    
class FixedHTTPRequestHandler(SimpleHTTPRequestHandler):
    def send_head(self):
        """Common code for GET and HEAD commands.

        This sends the response code and MIME headers.

        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.

        """
        path = self.translate_path(self.path)
            
        f = None
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return self.list_directory(path)
        ctype = self.guess_type(path)
        if ctype.startswith('text/'):
            mode = 'r'
        else:
            mode = 'rb'
        try:
            f = open(path, mode)
        except IOError:
            self.send_error(404, "File not found")
            return None
        self.send_response(200)
        self.send_header("Content-type", ctype)
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string())
        self.end_headers()
        return f

    
    
# Try to kill existing process
try:
    f = open(os.path.join('out', 'run-server.pid'))
except:
    print "No existing process"
else:
    pid = int(f.read())
    f.close()
    try:
        os.kill(pid, 15)
        print "Terminated existing process", pid
        time.sleep(0.5)
    except:
        print "Failed to kill existing process", pid

if '--stop' in sys.argv:
    sys.exit(0)
    
# Fork if requested
if '--fork' in sys.argv:
    child_pid = os.fork()
    forked = True
else:
    child_pid = os.getpid()
    forked = False

# Record server process id
if child_pid:
    f = open(os.path.join('out', 'run-server.pid'), 'w')
    f.write(str(child_pid))
    f.close()

# Start server
if child_pid == 0 or not forked:

    # Redirect stdout/err if forked
    print "Running server on port", PORT, "; process id is", os.getpid()
    if forked:
        sys.stdout = sys.stderr = CDevNull()
        
    # Run the server
    os.chdir('out')
    server = HTTPServer(('', PORT), FixedHTTPRequestHandler)
    server.serve_forever()
    

