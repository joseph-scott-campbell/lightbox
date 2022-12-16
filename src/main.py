# required for connecting to wifi
import rp2
import network

# needed for restarting the code
import machine

# misc
import time
import json

from neopixel import Neopixel
from finance import finance
from webserver import webserver
# Configuration Variables

with open("wifi.json", "r") as f:
    WIFI = json.load(f)
with open("stocks.json", "r") as f:
    STOCKS = json.load(f)

print(WIFI)
print(STOCKS)

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
NEOPIXELS = [1, 2, 3, 4, 5]

for stock in STOCKS:
    NEOPIXELS[STOCKS[stock]["number"]] = Neopixel(NEOPIXEL_LEN, 0,
                                                  STOCKS[stock]["pin"], "RGB")


def connect():
    time.sleep(1)

    # get named of all SSIDs in range
    ssids = [ssid[0].decode() for ssid in network.WLAN().scan()]

    # Giving information for network debugging
    if NETWORK_DEBUG_MODE:
        print("Available SSIDs: " + str(ssids))
        print("SSID Var in SSID: " + str(SSID in ssids))
    # if the SSID is in range then connect to it
    if WIFI["SSID"] in ssids:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            time.sleep(1)
        print("Connected to", WIFI["SSID"])
        print("IP Address:", wlan.ifconfig()[0])
    else:
        # start access point
        wlan = network.WLAN(network.AP_IF)
        wlan.config(essid="StockBox Configuration Network", key="StockBox")
        wlan.active(True)
        # print information for connecting to network
        print("SSID:", wlan.config("essid"))

        while True:
            uri = webserver.run()  # running config webserver

            # remove html escape codes and replace with actual characters
            uri = webserver.fix_html()
            uri_parser(uri)  # parse the uri


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
        uri = uri.split("&")
        for i in uri:
            i = i.split("=")
            if len(i) < 2:
                return

            # checking that input is vaild and filling fields
            if i[0] == "ssid":
                WIFI["SSID"] = i[1]
            elif i[0] == "password":
                WIFI["PASSWORD"] = i[1]
            elif i[0] == "stock1":
                STOCKS["stock1"]["symbol"] = i[1]
            elif i[0] == "stock2":
                STOCKS["stock2"]["symbol"] = i[1]
            elif i[0] == "stock3":
                STOCKS["stock3"]["symbol"] = i[1]
            elif i[0] == "stock4":
                STOCKS["stock4"]["symbol"] = i[1]
            elif i[0] == "stock5":
                STOCKS["stock5"]["symbol"] = i[1]

            # save the STOCKS and WIFI dictionaries to a file
            with open("stocks.json", "w") as f:
                json.dump(STOCKS, f)
            with open("wifi.json", "w") as f:
                json.dump(WIFI, f)

            print(i)


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
            pixel_color = calculate_color(finance.get_percent_change(
                STOCKS[stock]["symbol"]))

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
