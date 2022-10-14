#!/usr/bin/env python3
# coding: utf-8
# Copyright 2022 Johnson Zhao
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=''):
        self.code = int(code)
        self.body = str(body)

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        print(f'Host: {host} Port: {port}')
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        resp = data[0].split(' ')
        resp_code = resp[1]
        print('\nResponse Code: ' + resp_code)
        return resp_code

    def get_headers(self, data):
        headers = data[0]
        headers_list = headers.split('\r\n')
        print('Headers:\n' + headers)
        return headers

    def get_body(self, data):
        body = data[1]
        #print("\n\n\nData:" + body)
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    ''' python docs
    urlparse("scheme://netloc/path;parameters?query#fragment")

    ParseResult(scheme='scheme', netloc='netloc', path='/path;parameters', params='', query='query', fragment='fragment')
    '''
    def GET(self, url, args=None):
        print('HTTP GET')
        code = 500
        body = ''
        h_port = 80
        h_host = url
        h_path = '/'
        url_parsed = urllib.parse.urlparse(url)
        print("Parsed URL:\n" + str(url_parsed))

        if url_parsed.netloc:  # make sure URL is valid
            h_host = url_parsed.netloc
            # print('Invalid URL')
            # exit()            
        
        if url_parsed.path:
            h_path = url_parsed.path

        if ':' in h_host:  # if there is a port splice it
            split = h_host.split(':')
            h_host = str(split[0])
            h_port = int(split[1])
            print(f'Port changed to {h_port} from 80')

        #h_host = socket.gethostbyname(h_host)

        payload = f'GET {h_path} HTTP/1.1\r\nHost: {h_host}\r\nConnection: Close\r\n\r\n'

        self.connect(h_host, h_port)
        self.sendall(payload)
        h_data = self.recvall(self.socket)

        h_data = h_data.split('\r\n\r\n')
        code = self.get_code(h_data)
        headers = self.get_headers(h_data)
        body = self.get_body(h_data)
        self.close()

        return HTTPResponse(code, body)

    # POST 
    # header formatting reference: https://www.tutorialspoint.com/http/http_requests.htm
    def POST(self, url, args=None):
        print('HTTP POST')
        # connection variables
        code = 500
        body = ''      
        h_port = 80
        h_host = url
        h_path = '/'
        url_parsed = urllib.parse.urlparse(url)

        # content variables
        content = args
        content_type = 'text/html; charset=UTF-8'
        content_length = 0
        
        # move to function later
        print("Parsed URL:\n" + str(url_parsed))
        if url_parsed.netloc:
            h_host = url_parsed.netloc  
        if url_parsed.path:
            h_path = url_parsed.path
        if ':' in h_host:
            split = h_host.split(':')
            h_host = str(split[0])
            h_port = int(split[1])
            print(f'Port changed to {h_port} from 80')

        if not content == None:  # if there is content recalc length and send
            content_length = len(content)
            payload = f'GET {h_path} HTTP/1.1\r\nHost: {h_host}\r\nContent-Type: {content_type}\r\nContent-Length: {content_length}\r\nConnection: Close\r\n\r\n{content}\r\n\r\n'
        else:  # no content dont include
            payload = f'GET {h_path} HTTP/1.1\r\nHost: {h_host}\r\nContent-Type: {content_type}\r\nContent-Length: {content_length}\r\nConnection: Close\r\n\r\n'

        self.connect(h_host, h_port)
        self.sendall(payload)
        h_data = self.recvall(self.socket)

        h_data = h_data.split('\r\n\r\n')
        code = self.get_code(h_data)
        headers = self.get_headers(h_data)
        body = self.get_body(h_data)
        self.close()

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command(sys.argv[2], sys.argv[1].upper()))
    else:
        print(client.command(sys.argv[1]))
