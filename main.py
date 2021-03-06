import alpaca_trade_api as tradeapi
from dotenv import load_dotenv
import os
import pandas as pd
import questionary
import smtplib #added for sms
from utils import send


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

timeframe = questionary.select(
    'Select the timeframe you want to base your strategy on:',
    choices=['1Min','5Min','15Min']
).ask()

t_num = timeframe.split('Min')[0]


"""Initialize the first dataframe"""

# Format current date as ISO format
start_date = (pd.Timestamp.utcnow() - pd.Timedelta(4,'h')).isoformat()
end_date = pd.Timestamp.utcnow().isoformat() 
# timeframe = '15m'
stocks_data = alpaca.get_barset(
    tickers,
    timeframe,
    start = start_date,
    end = end_date
).df
stocks_data = stocks_data.dropna()
print(stocks_data)


while True:
    
    c = False
    while c == False:
        if (pd.Timestamp.utcnow().minute % int(t_num) == 0 and
            stocks_data.index[-1].minute != pd.Timestamp.utcnow().minute
        ):
            c = True
    #exit the while loop and update the dataframe

    stocks_data = alpaca.get_barset(
        tickers,
        timeframe,
        start = start_date,
        end = pd.Timestamp.utcnow().isoformat()
    ).df
    stocks_data = stocks_data.dropna()
    
    #create a dataframe of the close prices
    
    close_df = pd.DataFrame()

    for ticker in tickers:
        close_df[str(ticker)] = stocks_data[str(ticker)]['close']

    #calculate 14 period rsi for dataframe
    rsi_period = 14
    chg = close_df.diff(1)
    gain = chg.mask(chg<0,0)
    loss = chg.mask(chg>0,0)
    avg_gain = gain.ewm(com = rsi_period-1,min_periods=rsi_period).mean()
    avg_loss = loss.ewm(com = rsi_period-1,min_periods=rsi_period).mean()
    rs = abs(avg_gain / avg_loss)
    rsi_close = 100 - (100/(1+rs))

    # code to generate signal
    rsi_sell = (rsi_close>70) & (rsi_close.shift(1)<=70)
    rsi_buy = (rsi_close<30) & (rsi_close.shift(1)>=30)
    
    rsi_signals=pd.concat([rsi_buy.iloc[-1],rsi_sell.iloc[-1]],axis=1)
    rsi_signals.columns=['RSI Buy', 'RSI Sell']

    # calculate ma for dataframe
    ma_short = close_df.ewm(span=12, adjust=False).mean()
    ma_long = close_df.ewm(span=26, adjust=False).mean()
    
    # code to generate signals and dataframe
    ma_sell = ((ma_short <= ma_long) & (ma_short.shift(1) >= ma_long.shift(1)))
    ma_buy = ((ma_short >= ma_long) & (ma_short.shift(1) <= ma_long.shift(1)))

    ma_signals=pd.concat([ma_buy.iloc[-1], ma_sell.iloc[-1]], axis=1)
    ma_signals.columns=['MA Buy','MA Sell']
    all_signals=pd.concat([rsi_signals,ma_signals],axis=1)
    

    # send message if any values in dataframe are true
    if True in all_signals.values:
        some_text = f'you have a stock signal {all_signals}'
        send(some_text)
