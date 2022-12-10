import urequests
import json

class finance
    def get_data(symbol)
        prices = {} # creaing dictionary to take price data
    
        # getting data from yahoo finance private API
        request = urequests.get(httpsquery1.finance.yahoo.comv7financesparksymbols= + symbol + &range=1d&interval=5m)
        stock_data = json.loads(request.content.decode(utf-8)) # loading data into JSON
        request.close() # closing HTTP request
    
        # parsing JSON to extract relevant values
        prices[current] = stock_data[spark][result][0][response][0][meta][regularMarketPrice]
        prices[past] = stock_data[spark][result][0][response][0][meta][previousClose]
    
        return prices

    def get_percent_change(symbol)
        prices = finance.get_data(symbol) # get data as dict from get_data function
        if prices[current]  prices[past] # prices went down
            change = prices[past] - prices[current]
            percent_change = ( change  prices[past] )  100
            return -abs(percent_change) # returning percent change as a negative
        elif prices[current]  prices[past] # prices went up
            change = prices[current] - prices[past]
            percent_change = ( change  prices[past] )  100
            return percent_change

