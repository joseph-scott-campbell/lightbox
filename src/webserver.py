import socket
import re


class webserver():
    def run():
        # need to run each time, use external loop
        # a very simple custom webserver because the existing
        # alternatives are too complex for my purposes
        addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

        s = socket.socket()
        s.bind(addr)
        s.listen(1)

        print('listening on', addr)

        file = open("/www/index.html", "r")  # getting html page from file
        html = file.read()  # converting the file pointer into a string

        # Starting a infinate webserver loop
        # accepting connection
        conn, addr = s.accept()
        print('client connect from', addr)

        # receiving 1024 bytes of data
        request = conn.recv(1024)

        # filtering get requesting using magic regex
        match = re.search("GET\s+(\S+)\s+", request.decode())
        uri = match.group(1)
        uri = uri.replace("/", "")  # getting rid of the "/" in the uri

        print(uri)
        # sending http request
        conn.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        conn.send(html)  # sending the html
        conn.close()  # closing the connection
        return(uri)  # parsing the uri
        # close the socket
        s.close()

    def fix_html(uri):
        uri = uri.replace("%20", " ")
        uri = uri.replace("%21", "!")
        uri = uri.replace("%22", '"')
        uri = uri.replace("%23", "#")
        uri = uri.replace("%24", "$")
        uri = uri.replace("%25", "%")
        uri = uri.replace("%26", "&")
        uri = uri.replace("%27", "'")
        uri = uri.replace("%28", "(")
        uri = uri.replace("%29", ")")
        uri = uri.replace("%2A", "*")
        uri = uri.replace("%2B", "+")
        uri = uri.replace("%2C", ",")
        uri = uri.replace("%2D", "-")
        uri = uri.replace("%2E", ".")
        uri = uri.replace("%2F", "/")
        uri = uri.replace("%3A", ":")
        uri = uri.replace("%3D", "=")
        uri = uri.replace("%3E", ">")
        uri = uri.replace("%3F", "?")
        uri = uri.replace("%40", "@")
        uri = uri.replace("%5B", "[")
        uri = uri.replace("%5C", "\\")
        uri = uri.replace("%5D", "]")
        uri = uri.replace("%5E", "^")
        uri = uri.replace("%5F", "_")
        uri = uri.replace("%60", "`")
        uri = uri.replace("%7B", "{")
        uri = uri.replace("%7C", "|")
        uri = uri.replace("%7D", "}")
        uri = uri.replace("%7E", "~")
        uri = uri.replace("%7F", " ")

        return uri()
