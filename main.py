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

startTime = datetime.now()

#define system arguments
ARGS = sys.argv

#only do this if we want to update training dataset
if 'update' in ARGS:
	#here we are going to define our data set as the top x results when looking at the utility industry under Yahoo Finance website as of 3/18/2019 at 4:21 P.M. 
	numberOfTickers = 0 #for testing purposes
	stocksFile = open('tickerSymbols.csv', 'r')
	tickersAndNamesData = stocksFile.read().split()
	tickersAndNames = []
	for pair in tickersAndNamesData:
		tickersAndNames.append(pair.split(','))
	stocksFile.close()
	stockDict = {}
	#define training data
	trainingData = pd.DataFrame()
	failedData = []
	for ticker, companyName in tickersAndNames:
		numberOfTickers += 1
		try:
			trainingData = pdr.get_data_yahoo(ticker, '2018-01-01', '2019-01-01', False, 'ticker', False, True)
		except:
			trainingData = {}
			print("Failed to acquire data for ticker {}.".format(ticker))
		if not trainingData.empty:
			print("Successfully processed ticker {}.".format(ticker))
			#get data to work with
			#store data as a class
			stock = Stock(ticker)
			for datatype in trainingData:
				for index, datapoint in enumerate(trainingData[datatype]):
					stock.addDataPoint(datatype, [trainingData.index[index].date().strftime('%Y-%m-%d'), datapoint])
			#do training with stock
			stockDict[ticker] = stock
		else:
			failedData.append(ticker)
			print("Could not process ticker {}.".format(ticker))
			#if no data has been processed then restart program. note if first 10 fail we can assume we failed to access the data
			if len(failedData) == numberOfTickers and len(failedData) >= 10:
				print("Failed to access Yahoo Finance data... restarting program in 45 seconds.")
				time.sleep(45)
				#close training file
				os.execv(sys.executable, ['python'] + sys.argv)
	#store stockDict with pickle
	trainingDataFile = open('trainingData.pickle', 'wb')
	pickle.dump(stockDict, trainingDataFile)
	trainingDataFile.close()
	#print the failed ticker names
	print("Failed to process tickers: {}.".format(failedData))	
	#purge failed data
	stocksFile = open('tickerSymbols.csv', 'w')
	for ticker, companyName in tickersAndNames:
		if ticker not in failedData:
			stocksFile.write(str(ticker) + ',' + str(companyName) + '\n')
	stocksFile.close()
else:
	print("Training data not updated.")

#if we want to train
if 'train' in ARGS:
	#get stock dictionary of classes
	trainingDataFile = open('trainingData.pickle', 'rb')
	stockDict = pickle.load(trainingDataFile)
	trainingDataFile.close()
else:
	print("Did not train the data.")

print("Run time is {}".format(datetime.now()-startTime))

#get current date
#currentDate = datetime.strftime(datetime.now(),'%Y-%m-%d')

