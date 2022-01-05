"""
This is to mix all symbol quotes in one month into one file
easy to feed data to machine learning
"""

import os
import pandas as pd
from datetime import date, datetime, timedelta
from globalSettings import rawQuotesPath, quotesCsvPath, targetIndex, targetColumns, marketOpen, marketClose
from stock_data_reader import StockDataReader
from utils import getMonthlyPeriod, formatDate, findStartDateAndEndDate, isNoTradingDate, saveOrAppendCsv

from listSymbols import listSymbols

def mixQuotes(symbolSet, startDate, endDate):
    stockSymbolSet = [symbol for symbol in symbolSet if symbol not in targetIndex]
    periodRange = pd.period_range(start=startDate, end=endDate, freq='D')
    result = []
    for day in periodRange:
        date1 = date(day.year, day.month, day.day)
        if not isNoTradingDate(date1): 
            date1Str = date1.strftime('%Y%m%d')
            df = readQuotes(stockSymbolSet, date1Str, "stock")
            result.append(df)
    return pd.concat(result)

def mixIndex(symbolSet, startDate, endDate):
    indexSymbolSet = [symbol for symbol in symbolSet if symbol in targetIndex]
    periodRange = pd.period_range(start=startDate, end=endDate, freq='D')
    result = []
    for day in periodRange:
        date1 = date(day.year, day.month, day.day)
        if not isNoTradingDate(date1): 
            date1Str = date1.strftime('%Y%m%d')
            df = readQuotes(indexSymbolSet, date1Str, "index")
            result.append(df)
    return pd.concat(result)

def timeFilter(row):
    currentTime = datetime.strptime(row['currentTime'], "%Y-%m-%d %H:%M")
    return currentTime.time() >= marketOpen and currentTime.time() <= marketClose

def toClose5Minute(date):
    minute = date.minute
    newMinute = round(minute / 5) * 5
    if newMinute == 60:
        newTime = date.replace(hour=date.hour+1, minute=0)
    else: 
        newTime = date.replace(minute=newMinute)
    return newTime

def readQuotes(symbolSet, dateStr, targetFilePrefix): 
    stockDataReader = StockDataReader()
    result = []
    for symbol in symbolSet:
        fileName = symbol + "_" + dateStr + ".json"
        fullPathFileName = os.path.join(rawQuotesPath, fileName)
        if not os.path.isfile(fullPathFileName):
            print("file not exist: ", fullPathFileName)
            continue
        quotes = stockDataReader.read(fullPathFileName)
        df = pd.DataFrame(quotes)
        
        # filter columns
        df = df[df.columns.intersection(targetColumns)]
        # filter by time: before market and after market
        df = df[df.apply(timeFilter, axis=1)]
        
        # add columns for index quotes
        if targetFilePrefix == 'index': 
            df['preMarketChangePercent'] = 0
            df['postMarketChangePercent'] = 0

        result.append(df)
    return pd.concat(result)

def amendMissedQuotes(df, symbolSet):
    startDate = df['currentTime'].min()
    endDate = df['currentTime'].max()
    periods = pd.date_range(startDate, endDate, freq='D')
    for period in periods:
        if isNoTradingDate(period):
            continue
        currentTime = datetime.combine(period, marketOpen)
        endTime = datetime.combine(period, marketClose)
        while currentTime <= endTime:
            df1 = df[df['currentTime'] == currentTime]
            missedSymbols = [symbol for symbol in symbolSet if symbol not in df1['symbol'].tolist()]
            if missedSymbols:
                print(currentTime, missedSymbols)
            for missedSymbol in missedSymbols:
                quote = findQuoteToAmend(missedSymbol, currentTime, df).copy()
                print(f"quote not found for {missedSymbol} @ {currentTime}, use this quote to replace {quote.iloc[0]['symbol']} {quote.iloc[0]['currentTime']} {quote.iloc[0]['regularMarketPrice']}")
                quote['currentTime'] = currentTime
                df = df.append(quote, ignore_index = True)
            currentTime = currentTime + timedelta(minutes=5)
    return df
        
def findQuoteToAmend(missedSymbol, currentTime, df):
    # find previous
    previousQuote = df[(df['symbol'] == missedSymbol) & (df['currentTime'] < currentTime)].tail(1)
    if previousQuote is not None and len(previousQuote) > 0:
        return previousQuote
    # find after
    nextQuote = df[(df['symbol'] == missedSymbol) & (df['currentTime'] >  currentTime)].head(1)
    if nextQuote is not None and len(nextQuote) > 0:
        return nextQuote
    # cannot find return 0 Cat’s Pride Unscented Multi-Cat Clumping Litte
    data = [{'averageDailyVolume10Day': 0,'fiftyDayAverage': 0,'postMarketChangePercent': 0,'preMarketChangePercent': 0,
                    'previousClose': 0,'regularMarketChangePercent': 0,'regularMarketDayHigh': 0,'regularMarketDayLow': 0,'regularMarketOpen': 0,
                    'regularMarketPrice': 0,'regularMarketVolume': 0,'symbol': missedSymbol,'twoHundredDayAverage': 0, 'currentTime':currentTime}]
    return pd.DataFrame(data)

def isPeriodProcessed(period):
    """
    check if the period already in csv
    """
    startDate = period[0]
    fileNameText = datetime.strftime(startDate, "%Y%m")
    csvFile = os.path.join(quotesCsvPath, f"{fileNameText}.text")
    if not os.path.isfile(csvFile):
        return False
    df = pd.read_csv(csvFile)
    currentTime = datetime.combine(startDate, marketOpen)
    df1 = df[df['currentTime'] >= currentTime]
    return len(df1) > 0

def removeFilesProcessed(): 
    for file in os.listdir(rawQuotesPath):
        os.remove(os.path.join(rawQuotesPath, file))

def mix():
    startDate, endDate = findStartDateAndEndDate(rawQuotesPath)
    symbolSet = listSymbols(rawQuotesPath)

    # more than one month between startDate, endDate
    periods = getMonthlyPeriod(startDate, endDate)
    for period in periods:
        startDate = formatDate(period[0])
        endDate = formatDate(period[1])
        stock_df = mixQuotes(symbolSet, startDate, endDate)
        index_df = mixIndex(symbolSet, startDate, endDate)
        df = pd.concat([stock_df, index_df])
        # algin time
        df['currentTime'] = pd.to_datetime(df['currentTime'], format="%Y-%m-%d %H:%M")
        df['currentTime'] = df['currentTime'].apply(toClose5Minute)
        print(f"before amend {len(df)}")
        periodText = datetime.strftime(period[0], '%Y%m')
        targetFile = os.path.join(quotesCsvPath, f"{periodText}.csv")
        if os.path.isfile(targetFile):
            # read the current csv file and merge with new df
            csv_df = pd.read_csv(targetFile)
            csv_df['currentTime'] = pd.to_datetime(csv_df['currentTime'], format="%Y-%m-%d %H:%M")
            df = csv_df.append(df)
        df.drop_duplicates(subset=['symbol', 'currentTime'], keep='last', inplace=True)
        assert len(df) % (122 *85) == 0
        df.to_csv(targetFile, index=False)
    removeFilesProcessed()

if __name__ == '__main__':
    # mix()
    removeFilesProcessed()
