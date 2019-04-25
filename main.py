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
		trend = ((trainDict[randomStock].getDataType('Open')[buyStock][1] - trainDict[randomStock].getDataType('Open')[buyStock-30][1]) > 0)
		#up from previous data point
		previous = ((trainDict[randomStock].getDataType('Open')[buyStock][1] - trainDict[randomStock].getDataType('Open')[buyStock-1][1]) > 0)
		#sentiment analysis
		sentiment = random.choice([True, False]) #placeholder until nick finishes code for this

		#add features to dictionary
		features = {
			"trend" : trend,
			"previous" : previous,
			"sentiment" : sentiment
		}

		#total profit
		profit = (trainDict[randomStock].getDataType('Open')[buyStock][1] < trainDict[randomStock].getDataType('Open')[sellStock][1])
		
		table.append([features, profit])
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
		#get current state
		inDate = datetime.today()
		currentPrice = pdr.get_data_yahoo(ticker, inDate, inDate.today(), False, 'ticker', False, True)["Open"][0]
		yesterdayPrice = pdr.get_data_yahoo(ticker, (inDate.today()-timedelta(1)).strftime('%Y-%m-%d'), (inDate.today()-timedelta(1)).strftime('%Y-%m-%d'), False, 'ticker', False, True)["Open"][0] 
		trendPrice = pdr.get_data_yahoo(ticker, (inDate.today()-timedelta(30)).strftime('%Y-%m-%d'), (inDate.today()-timedelta(30)).strftime('%Y-%m-%d'), False, 'ticker', False, True)["Open"][0] 
		#get general trend for past 30 data points
		trend = ((currentPrice - trendPrice) > 0)
		#up from previous data point
		previous = (currentPrice - yesterdayPrice > 0)
		#sentiment analysis
		sentiment = random.choice([True, False]) #placeholder until nick finishes code for this
		#add features to dictionary
		features = {
			"trend" : trend,
			"previous" : previous,
			"sentiment" : sentiment
		}
		#count hits
		positive = table.count([features, True])/len(table)
		negative = table.count([features, False])/len(table)
		print(ticker, positive, negative)

	print('Testing Done')