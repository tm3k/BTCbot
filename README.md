# Confirmed working on python 3.7
# pip install python-binance
# pip install finta

# Get an api key from binance and slap that bitch into creds
# Bot continuously scans btcusd 15minute chart and will alert you when price is below 0 on %b by adding 'OVERSOLD' to the trade column in the dataframe
# [REDACTED]
# Example: https://twitter.com/__tm3k/status/1347570733887590401
# The type of trades it signals are often a high volatility scalp setup. 
# I like to trade this by staying in position from 10 minutes to a couple hours, tops.
# Code needs to be inverted to work in a downtrend, currently does not function properly in a downtrend.
# Added an inverted version of the bot to run in downtrends
# Currently trying to merge the code together to only signal buys or sells during certain trends, currently developing a strategy using the 20 period ema in conjunction with being above and below %b
# Added code that joins a trend following strategy with the %b strategy
# Program takes the first ema and last ema and compares them, if the first ema is higher than the last one its a downtrend and vice versa.
