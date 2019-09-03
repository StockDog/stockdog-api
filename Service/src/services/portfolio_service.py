from flask import g
from util.config import getConfig
from .ticker_service import getTickerPrice
from decimal import *

# Past date portfolio history cals needs more work here
def calculatePortfolioHistories():	
	config = getConfig()
	portfolioCount = getPortfolioCount();
	print("Total number of portfolios in the system ",portfolioCount )	
	pageSize = 1;
	for i in range(0, int(portfolioCount),pageSize):	    
		portfolioWithItems = getPortfolioWithItems(i,pageSize)
		try:
			calculatePortfolioHistory(portfolioWithItems);
		except Exception as e:
			g.log.error(e)
	return portfolioCount

def calculatePortfolioHistory(portfolioWithItems):
	portfolioItems = portfolioWithItems["portfolioItems"];
	portfolioId = portfolioWithItems["portfolio"]["id"]
	value = portfolioWithItems["portfolio"]["buyPower"];
	for portfolioItem in portfolioItems:
		shareCount = portfolioItem["shareCount"];
		ticker = portfolioItem["ticker"];
		price = getTickerPrice(ticker)
		currentValue = shareCount * price;
		value = value + Decimal(currentValue);

	g.cursor.execute('''INSERT INTO PortfolioHistory(portfolioId,datetime,value) VALUES(%s,NOW(),%s)''',(portfolioId,value))
	g.db.commit();
	return None;


def getPortfolioCount():
	g.cursor.execute("SELECT count(*) from Portfolio")
	portfolioCount = g.cursor.fetchone();
	return next(iter(portfolioCount.values()))

def getPortfolioWithItems(offset,size):	
	portfolioWithItems = {};
	g.cursor.execute("SELECT * from Portfolio order by id limit "+str(offset)+","+str(size))
	portfolio = g.cursor.fetchone()	
	g.cursor.execute("SELECT * from PortfolioItem where portfolioId=%s",(portfolio["id"]))
	portfolioItems = g.cursor.fetchall()
	portfolioWithItems["portfolio"] = portfolio;
	portfolioWithItems["portfolioItems"] = portfolioItems;
	return portfolioWithItems;