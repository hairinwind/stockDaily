"""
This is to mix all symbol quotes at the same time into one file
easy to feed data to machine learning
"""

import os
import pandas as pd
from datetime import date, timedelta
from stock_data_reader import StockDataReader

from listSymbols import listSymbols

path = "/home/yao/Downloads/quotes_json"
targetPath = "/home/yao/Downloads/quotes_csv"

# https://www.nyse.com/markets/hours-calendars
holidays = [
    date(2021,1,1),
    date(2021,1,18),
    date(2021,2,15),
    date(2021,4,2),
    date(2021,5,31),
    date(2021,7,5),
    date(2021,9,6),
    date(2021,11,25),
    date(2021,12,24)
]

def isNoTradingDate(date1): 
    if date1 in holidays:
        return True
    if date1.weekday() == 5 or date1.weekday() == 6: # Saturday or Sunday
        return True
    return False

def mixQuotes(symbolSet, startDate, endDate):
    stockSymbolSet = [symbol for symbol in symbolSet if not symbol.startswith("^")]
    periodRange = pd.period_range(start=startDate, end=endDate, freq='D')
    for day in periodRange:
        date1 = date(day.year, day.month, day.day)
        if not isNoTradingDate(date1): 
            date1Str = date1.strftime('%Y%m%d')
            generateMixQuoteFiles(stockSymbolSet, date1Str, "stock")

def mixIndex(symbolSet, startDate, endDate):
    indexSymbolSet = [symbol for symbol in symbolSet if symbol.startswith("^")]
    periodRange = pd.period_range(start=startDate, end=endDate, freq='D')
    for day in periodRange:
        date1 = date(day.year, day.month, day.day)
        if not isNoTradingDate(date1): 
            date1Str = date1.strftime('%Y%m%d')
            generateMixQuoteFiles(indexSymbolSet, date1Str, "index")

def generateMixQuoteFiles(symbolSet, dateStr, targetFilePrefix): 
    stockDataReader = StockDataReader()
    quotes_df = pd.DataFrame({'A' : []}) # empty dataframe
    for symbol in symbolSet:
        fileName = symbol + "_" + dateStr + ".json"
        fullPathFileName = os.path.join(path, fileName)
        if not os.path.isfile(fullPathFileName):
            print("file not exist: ", fullPathFileName)
            continue
        quotes = stockDataReader.read(fullPathFileName)
        if quotes_df.empty:
            quotes_df = pd.DataFrame(quotes)
        else:
            quotes_df = pd.concat([quotes_df, pd.DataFrame(quotes)])
    # print(quotes_df)
    # save quotes_df to file
    targetFile = os.path.join(targetPath, targetFilePrefix + "_" + dateStr+".csv")
    print("save file: ", targetFile)
    quotes_df.to_csv(targetFile, index=False)

if __name__ == '__main__':
    startDate = date(2021, 9, 8)
    endDate = date(2021, 9, 17)
    # endDate = date(2021, 5, 4)
    symbolSet = listSymbols(path)
    # print("symbol size: ", len(symbolSet))
    mixQuotes(symbolSet, startDate, endDate)
    mixIndex(symbolSet, startDate, endDate) 