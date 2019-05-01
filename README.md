# StockAI

## Running Code

In order to run the code, go into the directory where main.py is located and run "python main.py <arguments>" in the terminal. Note the code is capable of handling multiple arguments at once.

There are multiple arguments that are supported: 

update - this argument will grab stock data for the given list of stocks.

train - this argument will generate a table of randomly bought and sold stocks to compare our test data to. This process does not take long itself.

buys - this argument will make the code buy a list of stocks within a pre-determined time period. Whether or not the code buys stocks is based on the training data so running the 'train' argument again could change the output of 'buys'. NOTE: THIS PROCESS WILL TAKE ABOUT 2 HOURS!!!

sells - this argument will sell the stocks bought by the most recent 'buys' command based on pre-determined criteria. NOTE: THIS PROCESS TAKES ABOUT 2 HOURS!!!

results - this argument will print the graphs we included in our writeup.

##	Assignment Specific Notes

For each step of our code, we pickled the output data so that later steps could be run on the same data in significantly less time. Included with the assignment are copies of our last used pickle files. This will allow for the viewing of the results very quickly. However, if going through the whole process is desired, the process will take about 4 hours. The easiest way to accomplish this is with the command 'python main.py update train buys sells results'.
