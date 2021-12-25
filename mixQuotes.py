"""
This is to mix all symbol quotes at the same time into one file
easy to feed data to machine learning
"""

import os
import pandas as pd
from datetime import date, timedelta
from globalSettings import rawQuotesPath, quotesCsvPath, targetIndex, findStartDateAndEndDate, isNoTradingDate
from stock_data_reader import StockDataReader

from listSymbols import listSymbols

def mixQuotes(symbolSet, startDate, endDate):
    stockSymbolSet = [symbol for symbol in symbolSet if symbol not in targetIndex]
    periodRange = pd.period_range(start=startDate, end=endDate, freq='D')
    for day in periodRange:
        date1 = date(day.year, day.month, day.day)
        if not isNoTradingDate(date1): 
            date1Str = date1.strftime('%Y%m%d')
            generateMixQuoteFiles(stockSymbolSet, date1Str, "stock")

def mixIndex(symbolSet, startDate, endDate):
    indexSymbolSet = [symbol for symbol in symbolSet if symbol in targetIndex]
    periodRange = pd.period_range(start=startDate, end=endDate, freq='D')
    for day in periodRange:
        date1 = date(day.year, day.month, day.day)
        if not isNoTradingDate(date1): 
            date1Str = date1.strftime('%Y%m%d')
            generateMixQuoteFiles(indexSymbolSet, date1Str, "index")

def generateMixQuoteFiles(symbolSet, dateStr, targetFilePrefix): 
    stockDataReader = StockDataReader()
    for symbol in symbolSet:
        fileName = symbol + "_" + dateStr + ".json"
        fullPathFileName = os.path.join(rawQuotesPath, fileName)
        if not os.path.isfile(fullPathFileName):
            print("file not exist: ", fullPathFileName)
            continue
        quotes = stockDataReader.read(fullPathFileName)
        df = pd.DataFrame(quotes)
        targetFile = os.path.join(quotesCsvPath, targetFilePrefix + "_" + dateStr+".csv")
        if os.path.isfile(targetFile): 
            df.to_csv(targetFile, index=False, header=False, mode='a')
        else:
            df.to_csv(targetFile, index=False)
    
def mix():
    startDate, endDate = findStartDateAndEndDate(rawQuotesPath)
    symbolSet = listSymbols(rawQuotesPath)

    # startDate, endDate = '20211005','20211006'
    # symbolSet = ['TECS']
    # symbolSet = listSymbols(rawQuotesPath)

    # print("symbol size: ", len(symbolSet))
    mixQuotes(symbolSet, startDate, endDate)
    mixIndex(symbolSet, startDate, endDate) 

if __name__ == '__main__':
    mix()