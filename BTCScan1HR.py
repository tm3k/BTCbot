from binance.client import Client
from finta import TA
from datetime import datetime, date
import time as t
import creds # Binance API key
import ticker_list2 # List of all tickers on binance. 
import pandas as pd
import numpy as np
import datetime
import tweepy
import mplfinance as mpf

# Set up binance API
api_key = creds.APIkey
api_secret = creds.SecretKey
client = Client(api_key, api_secret)

# Set up tweepy API
auth = tweepy.OAuthHandler(creds.consumer_key, creds.consumer_secret)
auth.set_access_token(creds.access_token, creds.access_token_secret)
api = tweepy.API(auth)


while True:
    
    # Gets all symbol tickers into a list. 
    tickers = client.get_orderbook_tickers() #All tickers and quotes
    x=0 #iter
    complete_ticker_list = []
    for i in tickers: #for each stock in tickers, print only the ticker value
        y = tickers[x]
        x+=1
        symbol = y['symbol']
        complete_ticker_list.append(symbol)

    #Function to get ohlc values for a cryptocurrency on binance, and calculate if its above 1 or below 0 on %B
    def create_db(stock):
        open_val = []
        high_val = []
        low_val = []
        close_val = []
        time_val = []                                                         #KLINE_INTERVAL_15MINUTE
        ticker = [] 
        pandasdti = []
        volume = []                                                            #KLINE_INTERVAL_1DAY
                                                                              #KLINE_INTERVAL_4HOUR
        for kline in client.get_historical_klines_generator(f"{stock}", Client.KLINE_INTERVAL_1HOUR, "3 days ago UTC"):
            
            #Code that converts unix timestamp to readable output
            timestamp = kline[0] #UTC time code
            timestamp = timestamp / 1000 #divides by 1000 because timestamp expects time in seconds but it comes in milliseconds and was giving the wrong date
            timestamp = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')
            time_val.append(timestamp)
            
            ##converts unix time code to pandas DatetimeIndex object
            datetimee = pd.to_datetime(timestamp) 
            pandasdti.append(datetimee)

            #Adds ohlc values to lists
            open_val.append(float(kline[1]))
            high_val.append(float(kline[2]))
            low_val.append(float(kline[3]))
            close_val.append(float(kline[4]))
            volume.append(float(kline[5]))
            ticker.append(stock)
            
        # Combines ohlc value lists into one object then creates a pandas dataframe with that data.
        zippedList = list(zip(open_val, high_val, low_val, close_val))
        df = pd.DataFrame(zippedList, columns = ['open' , 'high', 'low', 'close'])

        # Creates second set of data for plotting it has to be formatted differently with a pandas datetimeindex object
        zippedList2 = list(zip(pandasdti, open_val, high_val, low_val, close_val))
        df2 = pd.DataFrame(zippedList2, columns = ['datetime', 'open' , 'high', 'low', 'close'])
        df2 = df2.set_index(['datetime'])
        df2['volume'] = volume
        
        # pandas df object containing bband values for plotting and merges them into df2
        bband = TA.BBANDS(df2) #pandas df object containing bband values
        df2['BB_UPPER'] = bband['BB_UPPER'] 
        df2['BB_MIDDLE'] = bband['BB_MIDDLE'] 
        df2['BB_LOWER'] = bband['BB_LOWER'] 
        
        # %B indicator added to DF
        bb = TA.PERCENT_B(df)
        bb = np.nan_to_num(bb) #replaces NaN values with 0.0 
        df["%BB"] = bb #Adds %b value column to df
        trade_signal = [] 
        

        for i in bb:
            
            if i == 0:
                trade_signal.append(''),              
            elif i > 1:
                trade_signal.append(''),               
            elif i < 0:
                trade_signal.append('Oversold'),    
            elif i <= 1 and i >= 0:
                trade_signal.append('')
            
        #Adds trade column to df
        df['Trade'] = pd.DataFrame(trade_signal)

        # Insert date and ticker to front of DF
        df.insert(0,"Date",time_val)
        df.insert(1,"Ticker",ticker)

        # Format for console, prints dataframe
        pd.set_option('display.width', None)
        pd.set_option('display.max_rows', None)
        
        # Iterates through rows and looks for oversold tickers
        tail = df.tail(1)
        print(f"{tail}\n") # Shows the last db row of each stock (last day of the 100 day period)
        tickerx = df['Ticker']
        signal = df['Trade']
        datex = df['Date']
        price = df['close']
        var = signal.tail(1)
        booly = var.str.contains('Oversold')
    

        if booly[71] == True and overall_trend == 'Up':
            tweet = f"\n{tickerx[71]} - {price[71]} - Oversold\n"
            print(tweet)
            plot(df2,tickerx)
            picpath = 'upload2.png'
            api.update_with_media(picpath,tweet)
        
    # Method to create plot
    def plot(df,ticker):
        mc = mpf.make_marketcolors(up='w',down='b')
        s  = mpf.make_mpf_style(marketcolors=mc)
        ap0 = [ mpf.make_addplot(df2['BB_UPPER'],color='b'),  # uses panel 0 by default
                mpf.make_addplot(df2['BB_LOWER'],color='b'),
                mpf.make_addplot(df2['BB_MIDDLE'],color='b'),  # uses panel 0 by default
            ]
        mpf.plot(df2, type='candle', axtitle = f"{ticker[0]} 1 HOUR", xrotation=20, datetime_format=' %A, %d-%m-%Y', savefig='upload2.png', volume = True, style = s,addplot=ap0, fill_between=dict(y1=df2['BB_LOWER'].values, y2=df2['BB_UPPER'].values, alpha=0.15))
        
    # Method to feed ticker into main function
    def feed_ticker(complete_ticker_list2):
        for i in ticker_list2.ticker_list2:
             create_db(i)
             t.sleep(2)

    #Method that starts the program
    feed_ticker(complete_ticker_list)
    t.sleep(1200) #20 minutes wait
