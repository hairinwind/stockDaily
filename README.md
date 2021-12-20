
## untar.py
untar the files collected

## listSymbols.py
list all symbols by the file names  
for example, file name is AAPL_20210503.json, the code returns AAPL

## mixQuotes.py
each quote file in quotes_json contains the 5 minutes data for one specific symbol, e.g. AAPL  
The mixQUotes.py is to mix all quotes data into one file and save it to quotes_csv/. e.g. /home/yao/Downloads/quotes_csv/stock_20210504.csv

## readMixQUotes
把所有同一时间的数据，收集起来，放在dataframe的 一个 row，然后可以作为 AI 的训练数据。

## generateDailyDataFrom5Minutes
