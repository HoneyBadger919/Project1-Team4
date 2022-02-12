from datetime import datetime
import time
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv
import os
import pandas as pd
from alpaca_trade_api.rest import TimeFrame, TimeFrameUnit

# load environment variables and import API keys

load_dotenv()
alpaca_api_key = os.getenv('ALPACA_API_KEY')
alpaca_secret_key = os.getenv('ALPACA_SECRET_KEY')
# Create the Alpaca API object
alpaca = tradeapi.REST(
    alpaca_api_key,
    alpaca_secret_key,
    api_version="v2")

# import the tickers of the observed stocks
"""
TO BE FIXED *** eliminate '\n' and spaces in the imported list
stock_list = []

with open('./input/stocks.txt') as s:
    for stock in s:
        stock_list.append(str(stock))
"""

"""Initialize the first dataframe"""

# Format current date as ISO format
start_date = pd.Timestamp("2022-02-10", tz="UTC").isoformat()
end_date = pd.Timestamp.utcnow().isoformat()
tickers = ['MSFT', 'AAPL', 'TSLA', 'NFLX']
# timeframe = '15m'
stocks_data = alpaca.get_barset(
    tickers,
    '15Min',
    start = start_date,
    end = end_date
).df
print(stocks_data)


while True:
    
    c = False
    while c == False:
        if (datetime.now().minute % int(15) == 0 and
            stocks_data.index[-1].minute != datetime.now().minute
            ):
            c = True
    #exit the while loop and update the dataframe

    stocks_data = alpaca.get_barset(
    tickers,
    '15Min',
    start = start_date,
    end = end_date
).df
    update data.....