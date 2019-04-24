#let's define a class to store our different stocks in as well as operational functions
class Stock():
	#initialization of a stock
	def __init__(self, ticker):
		self.ticker = ticker
		#define dictionary to store data
		self.data = {}

	#define function to return stock ticker
	def getTicker(self):
		return self.ticker

	#define function to add datapoints
	def addDataPoint(self, datatype, datapoint):
		if datatype not in self.data:
			self.data[datatype] = []
		try:	
			self.data[datatype].append(datapoint)
		except:
			print("Failed to add value {} to stock {}.".format(datapoint, self.ticker))

	#define function to get stock data
	def getData(self):
		return self.data

	#define funtion to get datapoint from a certain datatype
	def getDataType(self, datatype):
		try:
			return self.data[datatype]
		except:
			print("Could not retrieve data for data type {} under ticker {}.".format(datatype, self.ticker))




	