
## untar.py
untar the files collected

## listSymbols.py
list all symbols by the file names  
for example, file name is AAPL_20210503.json, the code returns AAPL

## mixQuotes.py
each quote file in quotes_json contains the 5 minutes data for one specific symbol, e.g. AAPL  
The mixQUotes.py is to mix all quotes data into one file and save it to quotes_csv/. e.g. /home/yao/Downloads/quotes_csv/stock_20210504.csv

## readMixQUotes
- mix stock and index into one data file 
- only keep useful columns
- column sequence in csv 
- sort by currentTime, symbol before saving to csv (TODO)

## generateDailyDataFrom5Minutes
- generate daily data from 5 minutes data (last record of each day)
- add custom indicators
- put back the custom indicator to each record in 5 minutes csv (TODO)

## readLearningData
- create numpy array as learning data, this is the observation in machine learning
- 