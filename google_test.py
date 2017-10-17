import pandas as pd
import io
import requests
import time
import yahoo_finance as yf
import datetime as dt
 
def google_stocks(symbol, startdate = (1, 1, 2005), enddate = None):
 
    startdate = str(startdate[0]) + '+' + str(startdate[1]) + '+' + str(startdate[2])
 
    if not enddate:
        enddate = time.strftime("%m+%d+%Y")
    else:
        enddate = str(enddate[0]) + '+' + str(enddate[1]) + '+' + str(enddate[2])
 
    stock_url = "http://www.google.com/finance/historical?q=" + symbol + \
                "&startdate=" + startdate + "&enddate=" + enddate + "&output=csv"
 
    raw_response = requests.get(stock_url).content
 
    stock_data = pd.read_csv(io.StringIO(raw_response.decode('utf-8')))
 
    return stock_data
 
def yahoo_date(d):
    return str(d.year)+'-'+str(d.month)+'-'+str(d.day)

def yahoo_finance():
    aapl = yf.Share('AAPL')
    print(aapl.get_open())

    print(aapl.get_historical(yahoo_date(dt.datetime(2017, 1, 3)), yahoo_date(dt.datetime(2017, 10, 1))))

 
if __name__ == '__main__':
    # apple_data = google_stocks('SUN')
    # print(apple_data)
 
    # apple_truncated = google_stocks('SUN', enddate = (1, 1, 2017))
    # print(apple_truncated)
    yahoo_finance()