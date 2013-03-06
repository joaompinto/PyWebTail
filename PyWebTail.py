#!/usr/bin/pyhon
# -*- coding: utf-8 -*- 

"""
PyWebTail.py
  Utility that creates a minimal HTTP web server that can be used to export 
  a log file tail. 
  It uses Python's BaseHTTPServer, removing the burden of installing and
  configuring a full web server for such a trivial purpose.
"""

import sys
import os
from time import time, strftime, localtime
from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from optparse import OptionParser


__author__ = "João Pinto"
__copyright__ = "Copyright 2013, João Pinto"
__credits__ = ["João Pinto"]
__license__ = "GPL-3"
__version__ = "1.0"
__maintainer__ = "João Pinto"
__email__ = "lamego.pinto@gmail.com"
__status__ = "Production"


def parse_args():
    """ Parse command line arguments """
    parser = OptionParser()
    parser.add_option("-n", "--lines K", 
                      action="store", type="int", dest="lines", default=10,
                      help="output the last K lines, instead of the last 10")    
    parser.add_option("-l", "--listener-port", 
                      action="store", type="int", dest="port",
                      help="Specifies the HTTP listener port")
    (options, args) = parser.parse_args()
    return (options, args)


def tail(f, lines=10, _block_size=512):
    """ Return tail of file """
    data = ''
    block_counter = -1   
    f.seek(0, os.SEEK_END)
    file_size = f.tell()
    lines_count = 0
    while lines_count < lines:
        try:
            f.seek(block_counter * _block_size, os.SEEK_END)
        except IOError:  # too small, or too many lines
            f.seek(0)
            data = f.read(file_size)
            return data.splitlines()
        tmp_data = f.read(_block_size)
        lines_count += tmp_data.count('\n')
        data = tmp_data + data
        block_counter -= 1
    return data.splitlines()[-lines:]
        
class TailHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()  
        html="""
<html><!--- refresh with a random url to avoid caching --->
<head><meta http-equiv="refresh" content="10;URL=/%s"></head>
<body>
<b>%s</b><br>
""" % (str(time()), strftime("%a, %d %b %Y %X %Z", localtime()))
        self.wfile.write(html)
        with open(self.server.tail_filename) as tail_file:
            tail_lines = tail(tail_file, self.server.tail_lines)            
            self.wfile.write('<br>'.join(tail_lines))
        self.wfile.write('</body></html>')            

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    pass

def main():
    (options, args) = parse_args()
    if not options.port or len(args) < 1:
        print "Usage: %s ( log_file | logs_directory ) -l port" \
            % sys.argv[0]
        sys.exit(2)
    tail_filename = args[0]
    server = ThreadingHTTPServer( 
            ("0.0.0.0", options.port), TailHandler )
    server.tail_filename = tail_filename
    server.tail_lines = options.lines
    server.serve_forever()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print "Interrupted"
        
