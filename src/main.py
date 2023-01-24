# required for connecting to wifi
import rp2
import network

# used for storing data
import json

# needed for restarting the code
import machine

# needed for webserver
import socket
import re

# needed for parsing URIs
import urllib.parse

# misc
import time

from neopixel import Neopixel
from finance import finance

# Configuration Variables

# Stock Data

STOCKS = {"stock1": {"symbol": "", "pin": 16},
          "stock2": {"symbol": "", "pin": 17},
          "stock3": {"symbol": "", "pin": 18},
          "stock4": {"symbol": "", "pin": 19},
          "stock5": {"symbol": "", "pin": 20}}

# Wifi Data

WIFI = {"SSID": "", "PASSWORD": "", "COUNTRY": "US"}

# Debugging Settings
WEBSERVER_DEBUG_MODE = True
NETWORK_DEBUG_MODE = True

# Wifi Credentials
SSID = "TP-Link_51CA"
PASSWORD = "password"
rp2.country("US")  # regional code

# Neopixel
BRIGHTNESS = 80
NEOPIXEL_LEN = 8  # length of neopixel strip

# Inititalizing NeoPixels
for stock in STOCKS:
    STOCKS[stock]["neopixel"] = Neopixel(NEOPIXEL_LEN, 0, STOCKS[stock]
                                         ["pin"], "RGB")


def connect():
    time.sleep(1)

    # get named of all SSIDs in range
    ssids = [ssid[0].decode() for ssid in network.WLAN().scan()]

    # Giving information for network debugging
    if NETWORK_DEBUG_MODE:
        print("Available SSIDs: " + str(ssids))
        print("SSID Var in SSID: " + str(SSID in ssids))
    # if the SSID is in range then connect to it
    if SSID in ssids:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            time.sleep(1)
        print("Connected to", SSID)
        print("IP Address:", wlan.ifconfig()[0])
    else:
        # start access point
        wlan = network.WLAN(network.AP_IF)
        wlan.config(essid="test", key="password")
        wlan.active(True)
        # print information for connecting to network
        print("SSID:", wlan.config("essid"))
        webserver()  # starting configuration webserver


def uri_parser(uri):
    # parsing the uri based on the input boxes in
    # www/index.html
    # if the uri is "break" then it will break the webserver loop
    if uri == "break":
        return True
    # if the uri is "reset" then it will reset the device
    elif uri == "reset":
        machine.reset()
    else:
        # setting the variables to the values in the uri
        # the uri is in the format of "ssid=SOMETHING&password=SOMETHING&stock1
        #                              =SOMETHING&stock2=SOMETHING&stock3=SOMET
        #                              HING&stock4=SOMETHING&stock5=SOMETHING"
        # so it's split on the "&" and then split on the "="
        # the first value is the variable name and the second is the value
        # the variables are then set to the values
        uri = urllib.parse.parse_qs(uri)
        for i in uri:
            # filling fields
            if i in STOCKS:
                STOCKS[i]["symbol"] = uri[i][0]
            elif i.upper() in WIFI:
                WIFI[i.upper()] = uri[i][0]

        with open("stocks.json", "w") as f:
            json.dump(STOCKS, f)
        with open("wifi.json", "w") as f:
            json.dump(WIFI, f)
        print(STOCKS)


def webserver():
    #  a very simple custom webserver because the existing
    # alternatives are too complex for my purposes
    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

    s = socket.socket()
    s.bind(addr)
    s.listen(1)

    print('listening on', addr)

    file = open("/www/index.html", "r")  # getting html page from index.html
    html = file.read()  # converting the file pointer into a string

    # Starting a infinate webserver loop
    while True:
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
        uri_parser(uri)  # parsing the uri
    # close the socket
    s.close()


def calculate_color(percent_change):
    # RGB values are to be put in tuple later
    red = 0
    green = 0
    blue = 0
    # changing which color is changed based on if it's positive or negative
    if percent_change >= 0:
        green = (BRIGHTNESS * percent_change)
    elif percent_change < 0:
        red = abs((BRIGHTNESS * percent_change))  # getting abs value

    # have to use green, red, blue with this library for some reason
    return (green, red, blue)  # returning variables are tuple


connect()  # connecting to wifi network

# giving information for debugging
if WEBSERVER_DEBUG_MODE:
    webserver()  # starting webserver

# Using try and except general to make it more resiliant
try:
    while True:
        for stock in STOCKS:
            # fetching data from STOCKS dictionary
            pixel_color = calculate_color(finance.get_percent_change(STOCKS[stock]["symbol"]))
            print(stock)
            print(pixel_color)
            for pixel in range(NEOPIXEL_LEN):
                STOCKS[stock]["neopixel"].set_pixel(pixel, pixel_color)
            STOCKS[stock]["neopixel"].show()
        time.sleep(5)
# using bare except because I want it to restart regardless of error
except:  # if there is an error, restart the code
    print("Error")
    machine.reset()
