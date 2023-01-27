#  coding: utf-8
import socketserver, os
from pathlib import Path

# This fork is written by: Mohammad Hammad

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(1024).strip().decode()
        print("Got a request of: %s\n" % self.data, end="")

        # Parse request
        request_info = self.data.splitlines()[0]       # Don't care about anything besides the first line for the purposes of this assignment
        request_type, request_url = request_info.split()[0:2]

        if request_type == "GET":
            self.handle_get(request_url)
        else:
            self.handle_unsupported()

        print()


    def handle_get(self, url):
        #We first perform some url checking to see if any redirection needs to happen
        url_type = Path(url).suffix[1:]
        #Correct path ending if needed
        if url_type=="" and url[-1] != "/":
            self.handle_redirect(url)
            return
        
        #Requesting a directory is the equivalent of requesting its index.html
        if url[-1] == "/":
            url = url + "index.html"
            url_type = "html"

        #Get absolute path of URL requests
        www_path = os.path.abspath(f"./www{url}")

        #Check that the request is only in www and lower, AND NOT HIGHER (SECURITY ISSUE!!!)
        if not www_path.startswith(os.path.abspath("./www")):
            self.handle_notfound()
            return

        #Process request now
        try:
            with open(www_path, "r") as file:  #url construction accounts for html and css mime-types, please note that this method can't be consistently extended to other mime-types
                page = file.read()

        except FileNotFoundError:
            self.handle_notfound()

        else:
            self.handle_found(url_type, page)

    

    def handle_found(self, url_type, page):
        print("File requested found")
        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/{url_type}\r\n\r\n" + page
        self.request.sendall(response.encode())


    def handle_notfound(self):
        print("File requested does not exist")
        response = "HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n" + "404 Page Not Found"
        self.request.sendall(response.encode())


    def handle_redirect(self, url):
        new_url = url + "/"
        print("Request redirected to", new_url)
        response = f"HTTP/1.1 301 Moved Permanently\r\nLocation: {new_url}\r\n\r\n"
        self.request.sendall(response.encode())


    def handle_unsupported(self):
        print("Method not supported")
        response = "HTTP/1.1 405 Method Not Allowed\r\nContent-Type: text/html\r\n\r\n" + "405 Method Not Allowed"
        self.request.sendall(response.encode())
    
    


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
