#run this code to clean up data gathered from yahoo finance downloader
#THIS FUNCTION TAKES THE INPUT OF THE CSV PRODUCED BY THE YAHOO FINANCE DOWNLOADER
#Files arleady cleaned cannot be passed back into this function

import pandas as pd 

def cleanData(filename):
	stocks = pd.read_csv(filename)
	tickers = list(stocks['Ticker'].values)
	companyNames = list(stocks['Name'].values)
	stocksFile = open(filename, 'w')
	for index in range(len(stocks)):
		try:
			stocksFile.write(str(tickers[index]) + ',' + str(companyNames[index]) + '\n')
		except:
			pass
	stocksFile.close()

cleanData('generic.csv')