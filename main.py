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

#only do this if we want to train the data
if 'train' in ARGS:
	#get stock dictionary of classes
	DataFile = open('Data.pickle', 'rb')
	stockDict = pickle.load(DataFile)
	DataFile.close()
	trainDict = {stock:stockDict[stock] for stock in stockDict if stock in tickers[:5]}
	table = []

	#create a loop to buy and sell 100 stocks
	for i in range(100):
		#random buy and sell
		randomStock = random.choice(tickers[:5])
		buyStock = random.randint(30,500)
		sellStock = random.randint(buyStock+1,501)
		#get general trend for past 30 data points
		trend = ((trainDict[randomStock].getDataType('Open')[buyStock][1] - trainDict[randomStock].getDataType('Open')[buyStock-30][1]) > 0)
		#up from previous data point
		previous = ((trainDict[randomStock].getDataType('Open')[buyStock][1] - trainDict[randomStock].getDataType('Open')[buyStock-1][1]) > 0)
		#sentiment analysis
		sentiment = True #placeholder until nick finishes code for this
		#see if stock was held more than 30 days
		longHold = ((trainDict[randomStock].getDataType('Open')[sellStock][0] - trainDict[randomStock].getDataType('Open')[buyStock][0]).days > 30)

		#add features to dictionary
		features = {
			"trend" : trend,
			"previous" : previous,
			"sentiment" : sentiment,
			"longHold" : longHold
		}

		#total profit
		profit = (trainDict[randomStock].getDataType('Open')[buyStock][1] < trainDict[randomStock].getDataType('Open')[sellStock][1])
		#add buy data to table
		table.append([features, profit])


#only do this if we want to test our data
if 'test' in ARGS:
	#get stock dictionary of classes
	DataFile = open('Data.pickle', 'rb')
	stockDict = pickle.load(DataFile)
	DataFile.close()
	trainDict = {stock:stockDict[stock] for stock in stockDict if stock in tickers[5:]}