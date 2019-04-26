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
			data = pdr.get_data_yahoo(ticker, '2017-01-01', '2019-01-01', False, 'ticker', False, True)
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
		#sentiment analysis
		sentiment = (random.randint(0,100) - random.randint(0,100)) #placeholder until nick finishes code for this
		maxDiff = (trainDict[randomStock].getDataType('Open')[buyStock][1] - trainDict[randomStock].getDataType('High')[buyStock][1])
		minDiff = (trainDict[randomStock].getDataType('Open')[buyStock][1] - trainDict[randomStock].getDataType('Low')[buyStock][1])
		maxMin = (trainDict[randomStock].getDataType('Low')[buyStock][1] - trainDict[randomStock].getDataType('High')[buyStock][1])
		#total profit
		profit = (trainDict[randomStock].getDataType('Open')[sellStock][1] - trainDict[randomStock].getDataType('Open')[buyStock][1])

		#add features to dictionary
		features = {
			"trend" : trend,
			"previous" : previous,
			"sentiment" : sentiment,
			"maxDiff" : maxDiff,
			"minDiff" : minDiff,
			"maxMin" : maxMin,
			"profit" : profit
		}
		
		table.append(features)
	#add buy data to table
	TestFile = open('Test.pickle', 'wb')
	pickle.dump(table, TestFile)
	TestFile.close()

	print("Training Done")

#only do this if we want to test our data
if 'test' in ARGS:
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

	#test each stock to see if we want to buy it
	for ticker in tickers[5:]:
		#get current state we want to look at
		inDate = datetime.today()-timedelta(3)
		#gather relevant variables
		try:
			currentPrice = pdr.get_data_yahoo(ticker, inDate.strftime('%Y-%m-%d'), inDate.strftime('%Y-%m-%d'), False, 'ticker', False, True)
		except:
			print("Data Unavailable: Try Different Date")
			sys.exit()
		deltaChange = 0
		while(1):
			try:
				previousPrice = pdr.get_data_yahoo(ticker, (inDate-timedelta(1+deltaChange)).strftime('%Y-%m-%d'), (inDate-timedelta(1+deltaChange)).strftime('%Y-%m-%d'), False, 'ticker', False, True)["Open"][0] 
				break
			except:
				deltaChange += 1
				print("Possible Loading Failure: If continues restart program...")
		deltaChange = 0
		while(1):
			try:	
				trendPrice = pdr.get_data_yahoo(ticker, (inDate-timedelta(30+deltaChange)).strftime('%Y-%m-%d'), (inDate-timedelta(30+deltaChange)).strftime('%Y-%m-%d'), False, 'ticker', False, True)["Open"][0] 
				break
			except:
				deltaChange += 1
				print("Possible Loading Failure: If continues restart program...")
		#get general trend for past 30 data points
		trend = (currentPrice['Open'][0] - trendPrice)
		#up from previous data point
		previous = (currentPrice['Open'][0] - previousPrice)
		#sentiment analysis
		sentiment = (random.randint(0,100) - random.randint(1,100)) #placeholder until nick finishes code for this
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
			diffSentiment = sentiment - entry['sentiment']
			diffMaxDiff = maxDiff - entry['maxDiff']
			diffMinDiff = minDiff - entry['minDiff']
			diffMaxMin = maxMin - entry['maxMin']
			difference = (abs(diffTrend) + abs(diffPrevious) + abs(diffSentiment) + abs(diffMaxDiff) + abs(diffMinDiff) + abs(diffMaxMin))/500
			if difference < diffChecker:
				diffChecker = difference
				mostSimilarEntry = entry
		print(diffChecker, mostSimilarEntry)

	print('Testing Done')