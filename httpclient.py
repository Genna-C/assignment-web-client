#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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
import json
# you may use urllib to encode data appropriately
from urllib.parse import urlparse, urlencode

# These are used if Port and Host are not specified 

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        top = data.split("\r\n")[0]  
        return int(top.split(" ")[1])

    def get_headers(self,data):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0', "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.7", "Accept-Language" : "en-US,en;q=0.9", "Accept-Encoding" : "gzip, deflate, br", "Upgrade-Insecure-Requests" : "1"}
        for header in headers:
            data += f"{header}: {headers[header]}\r\n"    
        data += f"\r\n"
        return data

    def get_body(self, data):
        return data.split("\r\n\r\n")[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    def split_host(self, url):
        split_url = urlparse(url) 
        HOST = split_url.hostname
        PORT = split_url.port
        if not PORT: PORT = 80
        return HOST, PORT
        
    def validate_url(self, url):
        parsed_url = urlparse(url) 
        add_url = parsed_url.scheme + parsed_url.netloc
        if parsed_url.scheme == "http": 
            add_url = "https://" + parsed_url.netloc
        
        if len(urlparse(url).path) > 1: 
             add_url += parsed_url.path
        return add_url 
            
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

    def GET(self, url, args=None):
        HOST, PORT = self.split_host(url)
        self.connect(HOST, PORT) 
        body = f"GET {urlparse(url).path} HTTP/1.1\r\nHost: {HOST}\r\n" 
        body = self.get_headers(body) 
 
        self.sendall(body) 
        response = self.recvall(self.socket) 
        self.close() 
        
        print("------------")
        print("for request %s " %body) 
        print("Printing Response: %s" %self.get_headers(response)) 
        print("------------")
        
        return HTTPResponse(self.get_code(response), self.get_body(response))

    def POST(self, url, args=None):
        HOST, PORT = self.split_host(url)
        self.connect(HOST, PORT)
        request = "POST / HTTP/1.1\r\nHost: %s\r\n\Content-Type: application/x-www-form-url-encoded\r\nContent-Length: " %url

        if args: 
            length = len(urlencode(args)) 
            request += "%s\r\n\r\n" %length
            request += "{0}\r\n\r\n".format(urlencode(args))
        else:
            request += "0\r\n\r\n"
            
        self.socket.sendall(request.encode("utf-8")) 
        response = self.recvall(self.socket) 
 
        self.close()
        return HTTPResponse(self.get_code(response), self.get_body(response))

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
