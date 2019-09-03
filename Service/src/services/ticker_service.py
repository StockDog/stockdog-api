from flask import g
from iexfinance.stocks import Stock
from util.config import getConfig

# Past date data collection needs more work here
def collectIEXTickersPrice():
	tickerPrices = {}
	config = getConfig()
	tickerCount = getTickersCount();
	print("Total number of tickers in the system ",tickerCount )
	pageSize = 50;
	for i in range(1, int(tickerCount), pageSize):	    
		tickers = getTickerSymbols(i,pageSize)
		try:
			batchCollection = Stock(tickers, output_format='pandas',token=config["iexToken"])
			data = batchCollection.get_quote()
			for ticker in tickers:
				tickerPrices[ticker] = data[ticker]["latestPrice"];
		except Exception as e:
			g.log.error(e)
	for key,value in tickerPrices.items():
		g.cursor.execute('''INSERT INTO TickerHistory(ticker,sharePrice) VALUES(%s,%s)''',(key,value))
	g.db.commit();
	return tickerPrices

# Past date data collection needs more work here
def collectIEXTickerPrice(ticker):
	print("Collecting the ticker price from IEX : ",ticker);
	currentPrice = {}
	config = getConfig()
	tickerPrice = Stock(ticker, output_format='pandas',token=config["iexToken"])
	price = tickerPrice.get_quote()[ticker]["latestPrice"];
	g.cursor.execute('''INSERT INTO TickerHistory(ticker,sharePrice) VALUES(%s,%s)''',(ticker,price))
	currentPrice[ticker]=price;
	g.db.commit();
	return currentPrice[ticker];

#For now we are only doing for the given day after close
def getTickerPrice(ticker):
	g.cursor.execute("SELECT sharePrice from TickerHistory where ticker=%s order by dateCreated desc limit 1",(ticker))
	tickerPrice = g.cursor.fetchone();
	price = 0.0;
	if tickerPrice != None:
		price = next(iter(tickerPrice.values()))
	else:
		price = collectIEXTickerPrice(ticker);
	return price;

def getTickersCount():
	g.cursor.execute("SELECT count(*) from ticker order by symbol asc")
	tickerCount = g.cursor.fetchone();
	return next(iter(tickerCount.values()))

def getTickerSymbols(offset,size):
	ignoreSymbols = ["BLIN","EVGBC","IVENC","ZTEST","EVLMC","IVFGC","EVSTC","IVFVC",]
	tickerArray = []
	g.cursor.execute("SELECT symbol from ticker order by symbol asc limit "+str(offset)+","+str(size))
	tickers = g.cursor.fetchall()
	for ticker in tickers:
		if ticker["symbol"].strip() not in ignoreSymbols:
			tickerArray.append(ticker["symbol"])
	return tickerArray;