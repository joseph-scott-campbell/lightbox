import urequests
import json


class finance:
    def get_data(symbol):
        prices = {}  # creaing dictionary to take price data

        # getting data from yahoo finance private API

        request = urequests.get("https://query1.finance.yahoo.com/v7/finance/spark?symbols=" + symbol + "&range=1d&interval=5m")

        # loading data into JSON
        stock_data = json.loads(request.content.decode("utf-8"))
        request.close()  # closing HTTP request

        # parsing JSON to extract relevant values
        prices["current"] = stock_data["spark"]["result"][0]["response"][0]["meta"]["regularMarketPrice"]
        prices["past"] = stock_data["spark"]["result"][0]["response"][0]["meta"]["previousClose"]

        return prices

    def get_percent_change(symbol):
        prices = finance.get_data(symbol)  # get data as dict from get_data()
        if prices["current"] <= prices["past"]:  # prices went down
            change = prices["past"] - prices["current"]
            percent_change = (change / prices["past"]) * 100
            return -abs(percent_change)  # percent change as a negative
        elif prices["current"] >= prices["past"]:  # prices went up
            change = prices["current"] - prices["past"]
            percent_change = (change / prices["past"]) * 100
            return percent_change
