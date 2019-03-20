#run this code to clean up data gathered from yahoo finance downloader
import pandas as pd 

stocks = pd.read_csv('tickerSymbols.csv')
tickers = list(stocks['Ticker'].values)
stocksFile = open('tickerSymbols.csv', 'w')
for ticker in tickers:
	stocksFile.write(str(ticker) + '\n')
stocksFile.close()