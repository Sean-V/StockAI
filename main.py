'''
Sean Vanderbach
Nicholas Palmer
5/1/2019
AI Practicum: StockAI
'''


#import random to get random trades
import random
#import usability of graphs
import matplotlib.pyplot as plt
#import out custom stock class
from dataClass import Stock
#import pickle to convert dictionaries to strings
import pickle
#import system functions
import sys
import os
#import pandas for data frame usage
import pandas as pd
#import numpy cuz numpy
import numpy as np
#import time to implement waits
import time
#import stock data 
import fix_yahoo_finance as yf
#import padas datareader
from pandas_datareader import data as pdr
#import so we can get current data and time
from datetime import datetime, timedelta
import fileinput 
#implement data reader into yahoo finace
yf.pdr_override()

#define system arguments
ARGS = sys.argv

#define stocks
tickers = ["ATVI","LMT","NKE","NFLX","AMZN","AAL","AAPL","INTC","NVDA","NOC"]

#only do this if we want to update training dataset
if 'update' in ARGS:
	data = pd.DataFrame()
	stock = None
	stockDict = {}
	for ticker in tickers:
		#attempt to grab data from yahoo finance
		try:
			data = pdr.get_data_yahoo(ticker, '2016-01-01', '2019-01-01', False, 'ticker', False, True)
		except:
			data = {}
			print("Failed to acquire data for ticker {}.".format(ticker))
		if not data.empty:
			print("Successfully processed ticker {}.".format(ticker))
			#get data to work with
			#store data as a class
			del stock
			stock = Stock(ticker)
			for datatype in data:
				for index, datapoint in enumerate(data[datatype]):
					stock.addDataPoint(datatype, [data.index[index].date(), datapoint])
			#do training with stock
			stockDict[ticker] = stock
		
	#store stockDict with pickle
	DataFile = open('Data.pickle', 'wb')
	pickle.dump(stockDict, DataFile)
	DataFile.close()

	print("Update Done")

#only do this if we want to train the data
if 'train' in ARGS:
	#get stock dictionary of classes
	DataFile = open('Data.pickle', 'rb')
	stockDict = pickle.load(DataFile)
	DataFile.close()
	trainDict = {stock:stockDict[stock] for stock in stockDict if stock in tickers[:5]}
	table = []

	#create a loop to buy and sell 100 stocks
	for i in range(1000000):
		#random buy and sell
		randomStock = random.choice(tickers[:5])
		buyStock = random.randint(30,500)
		sellStock = random.randint(buyStock+1,501)
		#get general trend for past 30 data points
		trend = (trainDict[randomStock].getDataType('Open')[buyStock][1] - trainDict[randomStock].getDataType('Open')[buyStock-30][1]) 
		#up from previous data point
		previous = (trainDict[randomStock].getDataType('Open')[buyStock][1] - trainDict[randomStock].getDataType('Open')[buyStock-1][1]) 
		maxDiff = (trainDict[randomStock].getDataType('Open')[buyStock][1] - trainDict[randomStock].getDataType('High')[buyStock][1])
		minDiff = (trainDict[randomStock].getDataType('Open')[buyStock][1] - trainDict[randomStock].getDataType('Low')[buyStock][1])
		maxMin = (trainDict[randomStock].getDataType('Low')[buyStock][1] - trainDict[randomStock].getDataType('High')[buyStock][1])
		weight = 0
		#total profit
		profit = (trainDict[randomStock].getDataType('Open')[sellStock][1] - trainDict[randomStock].getDataType('Open')[buyStock][1])

		#add features to dictionary
		features = {
			"trend" : trend,
			"previous" : previous,
			"maxDiff" : maxDiff,
			"minDiff" : minDiff,
			"maxMin" : maxMin,
			"profit" : profit,
			"weight" : weight
		}
		
		table.append(features)
	#add buy data to table
	TestFile = open('Test.pickle', 'wb')
	pickle.dump(table, TestFile)
	TestFile.close()

	print("Training Done")

#only do this if we want to test our data with buys
if 'buys' in ARGS:
	#get stock dictionary of classes
	DataFile = open('Data.pickle', 'rb')
	stockDict = pickle.load(DataFile)
	DataFile.close()
	#get testing data
	testDict = {stock:stockDict[stock] for stock in stockDict if stock in tickers[5:]}
	#get table to compare states with
	TestFile = open('Test.pickle', 'rb')
	table = list(pickle.load(TestFile))
	TestFile.close()
	
	#initialize resource pool
	currentMoney = 100000
	currentStocks = []
	goodBuys = 0
	goodBuyList = []

	#run through a year of data
	for day in range(0,365):
		print("progress: " + str(day+1) + "/365")
		print("good buys: " + str(goodBuys))
		#test each stock to see if we want to buy it
		for ticker in tickers[5:]:
			#get current state we want to look at
			inDate = datetime(2016, 1, 1)-timedelta(365-day)
			#gather relevant variables
			try:
				currentPrice = pdr.get_data_yahoo(ticker, inDate.strftime('%Y-%m-%d'), inDate.strftime('%Y-%m-%d'), False, 'ticker', False, True)
				if len(currentPrice) == 0:
					continue
			except:
				#skip to next iteration
				continue
			deltaChange = 0
			while(1):
				try:
					previousPrice = pdr.get_data_yahoo(ticker, (inDate-timedelta(1+deltaChange)).strftime('%Y-%m-%d'), (inDate-timedelta(1+deltaChange)).strftime('%Y-%m-%d'), False, 'ticker', False, True)["Open"][0] 
					break
				except:
					deltaChange += 1
					if deltaChange > 5:
						previousPrice = None
						break
			deltaChange = 0
			while(1):
				try:	
					trendPrice = pdr.get_data_yahoo(ticker, (inDate-timedelta(30+deltaChange)).strftime('%Y-%m-%d'), (inDate-timedelta(30+deltaChange)).strftime('%Y-%m-%d'), False, 'ticker', False, True)["Open"][0] 
					break
				except:
					deltaChange += 1
					if deltaChange > 5:
						trendPrice = None
						break
			#check if good data
			if trendPrice == None or previousPrice == None:
				continue
			#get general trend for past 30 data points
			trend = (currentPrice['Open'][0] - trendPrice)
			#up from previous data point
			previous = (currentPrice['Open'][0] - previousPrice)
			maxDiff = (currentPrice['Open'][0] - currentPrice['High'][0])
			minDiff = (currentPrice['Open'][0] - currentPrice['Low'][0])
			maxMin =  (currentPrice['Low'][0] - currentPrice['High'][0])

			#now let us find closest match between test data and our trained model
			mostSimilarEntry = None
			diffChecker = float('inf')
			differences = []
			for entry in table:
				#list differences
				diffTrend = trend - entry['trend']
				diffPrevious = previous - entry['previous']
				diffMaxDiff = maxDiff - entry['maxDiff']
				diffMinDiff = minDiff - entry['minDiff']
				diffMaxMin = maxMin - entry['maxMin']
				difference = (abs(diffTrend) + abs(diffPrevious) + abs(diffMaxDiff) + abs(diffMinDiff) + abs(diffMaxMin) + entry['weight'])/500
				if difference < diffChecker:
					diffChecker = difference
					mostSimilarEntry = entry
			if (diffChecker < 0.005 and mostSimilarEntry['profit'] > 75) or (diffChecker < 0.01 and mostSimilarEntry['profit'] > 300):
				goodBuys += 1
				#store good buy
				goodBuyList.append([ticker, currentPrice, mostSimilarEntry])
			print(diffChecker, mostSimilarEntry)

	#pickle good buys
	buyFile = open('buys.pickle', 'wb')
	pickle.dump(goodBuyList, buyFile)
	buyFile.close()
	print("Good Buys: " + str(goodBuys))

	print('Buying Done')

#only do this if we want to test our data with sells
if 'sells' in ARGS:
	buyFile = open('buys.pickle', 'rb')
	goodBuysList = pickle.load(buyFile)
	buyFile = buyFile.close()
	sells = {}
	print("Buys to parse: " + str(len(goodBuysList)))
	#for each day we look at
	for day in range(1, 730):
		#get closing data of stock in question
		for index, [ticker, buyData, similarFeatures] in enumerate(goodBuysList):
			#look two years out from each buy
			sellDate = (buyData['Open'].index[0] + timedelta(day))

			#lets create a 4 point system
			'''
			based on profit
			difference between high and open
			difference between high and close
			general trend (increasing is good decreasing is bad)
			'''

			#get current data for what we say is the current day
			try:
				currentData = pdr.get_data_yahoo(ticker, sellDate.strftime('%Y-%m-%d'), sellDate.strftime('%Y-%m-%d'), False, 'ticker', False, True)
			except:
				continue
			#get point 1: based on profit 
			if (currentData['Open'][0] - buyData['Open'][0]) > (0.5 * similarFeatures['profit']):
				pointOne = 1
			else:
				pointOne = 0

			#get point 2: difference between high and open
			OHDiff = currentData['High'][0] - currentData['Open'][0]
			if(OHDiff < 0.50):
				pointTwo = 1
			else:
				pointTwo = 0
				
			#get point 3: difference between high and close
			CHDiff = currentData['High'][0] - currentData['Close'][0]
			if (CHDiff/currentData['High'][0]) < 0.1:
				pointThree = 0
			else:
				pointThree = 1

			#get point 4: general trend (increasing is good decreasing is bad)
			deltaChange = 0
			try:
				previousPrice = pdr.get_data_yahoo(ticker, (sellDate-timedelta(5+deltaChange)).strftime('%Y-%m-%d'), (sellDate-timedelta(5+deltaChange)).strftime('%Y-%m-%d'), False, 'ticker', False, True)
			except:
				while(1):
					try:
						previousPrice = pdr.get_data_yahoo(ticker, (sellDate-timedelta(5+deltaChange)).strftime('%Y-%m-%d'), (sellDate-timedelta(5+deltaChange)).strftime('%Y-%m-%d'), False, 'ticker', False, True)
						break
					except:
						deltaChange += 1
			trend = (currentData['Open'][0] - previousPrice['Open'][0]) 
			if trend < 0:
				pointFour = 1
			else:
				pointFour = 0

			#check if sum of variables is > 2
			pointSum =  pointTwo + pointThree + pointFour
			if (pointSum >= 2 and (currentData['Open'][0] - buyData['Open'][0]) > (0.1 * similarFeatures['profit'])) or pointOne == 1:
				#data in sells includes ticker, buy price, buy date, sell price, sell date, profit, and if it was worth buying
				#this data includes actual sold data and best sold data for 2 year time period
				worthBuy = (currentData['Open'][0] - buyData['Open'][0]) > 5
				if (ticker, buyData['Open'].index[0].strftime('%Y-%m-%d')) not in sells:
					sells[(ticker, buyData['Open'].index[0].strftime('%Y-%m-%d'))] = []
					sells[(ticker, buyData['Open'].index[0].strftime('%Y-%m-%d'))].append([ticker, buyData['Open'][0], buyData['Open'].index[0].strftime('%Y-%m-%d'), currentData['Open'][0], currentData['Open'].index[0].strftime('%Y-%m-%d'), currentData['Open'][0] - buyData['Open'][0], worthBuy])
					sells[(ticker, buyData['Open'].index[0].strftime('%Y-%m-%d'))].append([ticker, buyData['Open'][0], buyData['Open'].index[0].strftime('%Y-%m-%d'), currentData['Open'][0], currentData['Open'].index[0].strftime('%Y-%m-%d'), currentData['Open'][0] - buyData['Open'][0], worthBuy])
				else:
					if sells[(ticker, buyData['Open'].index[0].strftime('%Y-%m-%d'))][1][5] < (currentData['Open'][0] - buyData['Open'][0]):
						sells[(ticker, buyData['Open'].index[0].strftime('%Y-%m-%d'))][1] = [ticker, buyData['Open'][0], buyData['Open'].index[0].strftime('%Y-%m-%d'), currentData['Open'][0], currentData['Open'].index[0].strftime('%Y-%m-%d'), currentData['Open'][0] - buyData['Open'][0], worthBuy]

	#pickle sells
	sellFile = open('sells.pickle', 'wb')
	pickle.dump([sells, goodBuysList], sellFile)
	sellFile.close()
	
if 'results' in ARGS:
	sellFile = open('sells.pickle', 'rb')
	sellList, buyList = pickle.load(sellFile)
	sellFile = sellFile.close()	

	#get profit date
	buys = [x for x in range(len(sellList))]
	boughtProfits = []
	maxProfits = []
	for entry in sellList:
		boughtProfits.append(sellList[entry][0][5])
		maxProfits.append(sellList[entry][1][5])

	#plot profits
	fig, ax = plt.subplots()
	ax.set_title("Actual Buy/Sell vs Ideal Buy/Sell")
	ax.set_xlabel("Sell Number")
	ax.set_ylabel("Profit")
	ax.plot(buys, maxProfits, color = 'red', label = 'Ideal Buy/Sell Profit')
	ax.plot(buys, boughtProfits, color = 'blue', label = 'Actual Buy/Sell Profit')
	ax.legend()
	
	#get date data
	boughtDates = []
	maxDates = []
	for entry in sellList:
		boughtSellDate = datetime.strptime(sellList[entry][0][4], "%Y-%m-%d")
		boughtBuyDate = datetime.strptime(sellList[entry][0][2], "%Y-%m-%d")
		boughtDates.append((boughtSellDate - boughtBuyDate).days)
		SoldSellDate = datetime.strptime(sellList[entry][1][4], "%Y-%m-%d")
		SoldBuyDate = datetime.strptime(sellList[entry][1][2], "%Y-%m-%d")
		maxDates.append((SoldSellDate - SoldBuyDate).days)

	#plot timespan differences
	fig2, ax2 = plt.subplots()
	ax2.set_title("Actual Timespan vs Ideal Timespan")
	ax2.set_xlabel("Sell Number")
	ax2.set_ylabel("Difference in Buy and Sell Date")
	ax2.plot(buys, maxDates, color = 'red', label = 'Ideal Timespan')
	ax2.plot(buys, boughtDates, color = 'blue', label = 'Actual Timespan')
	ax2.legend()
	plt.show()

	#get data for ticker profits
	#get data for total shares bought and sold of each ticker
	tickerProfitActual = {}
	tickerProfitMax = {}
	bought = {}
	sold = {}
	#set default ticker profit
	for ticker in tickers[5:]:
		tickerProfitActual[ticker] = 0
		tickerProfitMax[ticker] = 0
		bought[ticker] = 0
		sold[ticker] = 0

	#get total profit per ticker
	#get total shares bought and sold per ticker
	for buy in buyList:
		bought[buy[0]] += 1
		keyMatch = (buy[0], buy[1].index[0].strftime('%Y-%m-%d'))
		if keyMatch in sellList:
			sold[keyMatch[0]] += 1
			tickerProfitActual[keyMatch[0]] += sellList[keyMatch][0][5]
			tickerProfitMax[keyMatch[0]] += sellList[keyMatch][1][5]
		else:
			tickerProfitActual[keyMatch[0]] -= buy[1]['Open'][0]
			tickerProfitMax[keyMatch[0]] -= buy[1]['Open'][0]

	#get graph for ticker profits
	fig3, ax3 = plt.subplots()
	ax3.set_title("Actual Ticker Profit vs Ideal Ticker Profit")
	ax3.set_xlabel("Ticker")
	ax3.set_ylabel("Total Ticker Profit")
	ax3.bar([i+0.1 for i in range(5)], tickerProfitMax.values(), width = 0.2, color = 'red', label = 'Ideal Ticker Profits')
	ax3.bar([i-0.1 for i in range(5)], tickerProfitActual.values(), width = 0.2, color = 'blue', label = 'Actual Ticker Profits')
	ax3.set_xticklabels([''] + list(tickerProfitActual.keys()))
	ax3.axhline(y=0, color = 'black')
	ax3.legend()
	plt.show()

	#get graph for ticker profits
	fig4, ax4 = plt.subplots()
	ax4.set_title("Shares Bought vs Sold per Ticker")
	ax4.set_xlabel("Ticker")
	ax4.set_ylabel("Total Shares Bought and Sold")
	ax4.bar([i+0.1 for i in range(5)], sold.values(), width = 0.2, color = 'red', label = 'Shares Sold')
	ax4.bar([i-0.1 for i in range(5)], bought.values(), width = 0.2, color = 'blue', label = 'Shares Bought')
	ax4.set_xticklabels([''] + list(tickerProfitActual.keys()))
	ax4.axhline(y=0, color = 'black')
	ax4.legend()
	plt.show()