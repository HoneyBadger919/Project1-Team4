from datetime import datetime
import time
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv
import os
import pandas as pd
import questionary

# load environment variables and import API keys

load_dotenv()
alpaca_api_key = os.getenv('ALPACA_API_KEY')
alpaca_secret_key = os.getenv('ALPACA_SECRET_KEY')
# Create the Alpaca API object
alpaca = tradeapi.REST(
    alpaca_api_key,
    alpaca_secret_key,
    api_version="v2")

# make the user decide the stocks he wants to keep track of

tickers = questionary.checkbox(
    'Select the tickers you want to keep track of',
    choices=['AMZN','AAPL','TSLA','NFLX','GOOG']
).ask()


"""Initialize the first dataframe"""

# Format current date as ISO format
start_date = (pd.Timestamp.utcnow() - pd.Timedelta(4,'h')).isoformat()
end_date = pd.Timestamp.utcnow().isoformat() 
# timeframe = '15m'
stocks_data = alpaca.get_barset(
    tickers,
    '5Min',
    start = start_date,
    end = end_date
).df
print(stocks_data)


while True:
    
    c = False
    while c == False:
        if (pd.Timestamp.utcnow().minute % int(5) == 0 and
            stocks_data.index[-1].minute != pd.Timestamp.utcnow().minute
        ):
            c = True
    #exit the while loop and update the dataframe

    stocks_data = alpaca.get_barset(
        tickers,
        '5Min',
        start = start_date,
        end = pd.Timestamp.utcnow().isoformat()
    ).df
    print(stocks_data)