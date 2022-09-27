import socketserver
import os
import datetime


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
    def status_405(self):
        print("405 INVOKED")
        data = "HTTP/1.1 405 Method Not Allowed \r\n"
        data += "Date:"
        data += datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        data += "\r\n"
        data += "Connection: close\r\n"
        data += "\r\n\r\n"
        

        return data

    def status_400(self):
        print("405 INVOKED")
        data = "HTTP/1.1 400 Bad Request \r\n"
        data += "Date:"
        data += datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        data += "\r\n"
        data += "Connection: close\r\n"
        data += "\r\n\r\n"
        return data

    def status_200(self, content_type, file_content):
        print("200 INVOKED")  
        data = "HTTP/1.1 200 OK\r\n" # from class notes
        content_type_string = "Content-Type: " + content_type
        data += content_type_string
        data += "\r\n\r\n"
        data += file_content.decode('utf-8')
        data += "\r\n"

        return data


    def status_301(self, relativePath):
        data = "HTTP/1.1 301 Moved Permanently\r\n" # from class notes
        data += "Date:"
        data += datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        data += "\r\n"
        data += "Connection: close\r\n"
        location = relativePath+"/"
        location_string = "Location: " + location
        data += location_string
        data += "\r\n"
        data += "Content-Length: 0\r\n"
        data += "\r\n\r\n"

        return data

    def status_404(self):
        data = "HTTP/1.1 404 Not Found\r\n"
        data += "Date:"
        data += datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        data += "\r\n"
        data += "Connection: close\r\n"
        data += "\r\n\r\n"

        return data    

#--------------------------------------------------------------------------------------------------------

    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)


        self.decode_data = self.data.decode('utf-8') # Decoded request
        httpRequest = self.decode_data.split('\n')[0]
        # self.request.sendall(bytearray("OK",'utf-8'))
        if httpRequest[:4] != "GET ":
            response = self.status_405() # Method not allowed
            self.request.sendall(bytearray(response, 'utf-8'))
            print("405 NOT ALLOWED")
            #exit()

        elif len(httpRequest.split(' ')) != 3:
            response = self.status_400() # missing or too many arguments
            self.request.sendall(bytearray(response, 'utf-8'))
            print("400 Bad Response")
            #exit()

        else: #valiud continue
            request_arr = [x.strip() for x in httpRequest.strip('[]').split(' ')]
            print("REQUEST ARRAY: ",request_arr)

            _ = request_arr[0]
            resource = request_arr[1]
            http_ver = request_arr[2]
            print(resource)

            path = 'www'

            print("PATH",path)
            print("RESOURCE",resource)
            path += resource
            print("FINAL given PATH:", path)
        
            if not os.path.exists(path):
                response = self.status_404() # Not found
                print("404 Not Found")
                self.request.sendall(bytearray(response, 'utf-8'))
                
                #exit() # freetests case 4
            else:
                #if ends in / ... else if file specified
                if ((not resource.endswith(".html")) and (not resource.endswith(".css"))): #append index.html
                    if not resource.endswith('/'):
                        path += "/index.html"
                    else:
                        path += 'index.html'
                    mime_type = 'text/html'

                    if not os.path.exists(path): # if assumed index.html DNE
                        response = self.status_404() # Not Found
                        print("404 Not Found")
                        self.request.sendall(bytearray(response, 'utf-8'))
                        
                        #exit()
                    else:
                        with open(path, 'rb') as fp:
                            buf = fp.read()
                            print("file read and loaded")

                            if (path.endswith(".html")):
                                mime_type = "text/html"
                            elif (path.endswith(".css")):
                                mime_type = "text/css"

                        response = self.status_200(mime_type, buf)
                        print("RESPONSE 200 file assumed and loaded")
                        self.request.sendall(bytearray(response, 'utf-8'))
                
                        #exit() # freetests case 2

                else: # else a file is specified OR folder without / ending
                    # check if its a folder without / ending
                    with open(path, 'rb') as fp:
                        buf = fp.read()
                        print("file read and loaded")

                        if (path.endswith(".html")):
                            mime_type = "text/html"
                        elif (path.endswith(".css")):
                            mime_type = "text/css"
                            print("MIMETYPE:", mime_type)
                            #exit()

                        response = self.status_200(mime_type, buf)
                        print("RESPONSE 200 file request recognized")
                        self.request.sendall(bytearray(response, 'utf-8'))
                    
                        #exit() #freetests case 1
                
                        




            




        
if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()