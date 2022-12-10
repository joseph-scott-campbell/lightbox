# required for connecting to wifi
import rp2
import network

# needed for restarting the code
import machine

# needed for webserver
import socket
import re

# misc
import time

from neopixel import Neopixel
from finance import finance

# Configuration Variables

# Stock Data

STOCKS = {"NASDAQ": {"symbol": "^IXIC", "pin": 16},
          "Dow Jones": {"symbol": "^DJI", "pin": 17}}

# Wifi Credentials
SSID = "TP-Link_51CA"
PASSWORD = "password"
rp2.country("US")  # regional code

# Neopixel
BRIGHTNESS = 80
NEOPIXEL_LEN = 8  # length of neopixel strip

# Initalizing Neopixel
strip = Neopixel(NEOPIXEL_LEN, 0, 16, "RGB")


def connect():
    wlan = network.WLAN(network.STA_IF)  # initalizing wlan object
    wlan.active(True)  # running wlan

    wlan.connect(SSID, PASSWORD)  # credentials to log into wifi network

    number_of_tries = 0
    while not wlan.isconnected() and wlan.status() >= 0 and number_of_tries <= 25:
        print("Waiting to connect...")
        time.sleep(1)
        number_of_tries += 1
    if number_of_tries > 25:
        print("Failed to connect to wifi")
        print("Creating configuration network")
        ap = network.WLAN(network.AP_IF)
        ap.active(True)
        ap.config(essid="StockBox Configuration", authmode="open")
        webserver()  # starting config webserver
        machine.reset()
    else:
        print(wlan.ifconfig())


def webserver():
    #  a very simple custom webserver because the existing
    #  alternatives are too complex for my purposes
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
        if uri == "break":
            print("breaking")
            break
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
webserver()  # starting webserver

# Using try and except general to make it more resiliant
try:
    while True:
        for stock in STOCKS:
            # fetching data from STOCKS dictionary
            STOCKS[stock]["neopixel"] = Neopixel(NEOPIXEL_LEN, 0, STOCKS[stock]["pin"], "RGB")
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
