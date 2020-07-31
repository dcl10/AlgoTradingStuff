# AlgoTradingStuff
This package aims to provide an easy way to interact with APIs of various
trading platforms. Currently it offers some limited support for interacting
with the OANDA v20 API.

Right now the `OandaAccount` class is by no means feature complete, but you can:
- Search all sub-accounts linked to your OANDA account
- Create `OandaAccount` objects based on your sub-accounts
- Use the `OandaAccount` objects to raise requests to:
    - create and cancel orders
    - view and close your open positions
    - view and close open trades
    - get candles for any instrument OANDA trades
    
## Installation
```commandline
pip install algotradingtuff
```

## For more information
Visit the [ONADA docs](http://developer.oanda.com/rest-live-v20/introduction/).