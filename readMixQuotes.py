from datetime import datetime, timedelta, time
from globalSettings import isNoTradingDate, targetIndex, rawQuotesPath, quotesCsvPath, quotesOnedayPath, getDateFromFileName
from listSymbols import listSymbols

import os
import pandas as pd
import numpy as np

targetColumns = ['symbol', 'currentTime', 'regularMarketPrice', 'previousClose', 'regularMarketOpen', 'regularMarketDayHigh', 'regularMarketDayLow', 
                'regularMarketVolume', 'regularMarketChangePercent', 'postMarketChangePercent', 'preMarketChangePercent', 'averageDailyVolume10Day', 
                'fiftyDayAverage', 'twoHundredDayAverage']

marketOpen = time(9, 45)
marketClose = time(16, 45)

targetSymbol = listSymbols(rawQuotesPath)

"""
filter symbol and columns
"""
def readMixIndex(file): 
    if os.path.isfile(file): 
        dailyQuotes = pd.read_csv(file)
        # print(dailyQuotes['symbol'])
        sameTimeQuotes = dailyQuotes[dailyQuotes['symbol'].isin(targetIndex)]
        sameTimeQuotes['currentTime'] = pd.to_datetime(sameTimeQuotes['currentTime'], format="%Y-%m-%d %H:%M")
        sameTimeQuotes = sameTimeQuotes[sameTimeQuotes.columns.intersection(targetColumns)]
        sameTimeQuotes['preMarketChangePercent'] = 0
        sameTimeQuotes['postMarketChangePercent'] = 0
        return sameTimeQuotes

def readMixQuotes(file): 
    if os.path.isfile(file):
        dailyQuotes = pd.read_csv(file)
        sameTimeQuotes = dailyQuotes[~dailyQuotes['symbol'].isin(targetIndex)]
        sameTimeQuotes['currentTime'] = pd.to_datetime(sameTimeQuotes['currentTime'], format="%Y-%m-%d %H:%M")
        sameTimeQuotes = sameTimeQuotes[sameTimeQuotes.columns.intersection(targetColumns)]
        return sameTimeQuotes       

def getQuotesByTime(quotes, time):
    """
    get the quotes for specified time
    for example 9:10
    make a window from 9:08 - 9:13
    any quotes in this window is accepted
    """
    startTime = time - timedelta(minutes=2)
    endTime = time + timedelta(minutes=3)
    oneTimeQuotes = quotes[(quotes['currentTime']>=startTime) & (quotes['currentTime']<endTime)]
    #  amend missed quotes with previous quote
    oneTimeQuotes = oneTimeQuotes.drop_duplicates(subset=['symbol'])
    missedSymbol = [symbol for symbol in targetSymbol if symbol not in oneTimeQuotes['symbol'].tolist()]
    for missedSymbol in missedSymbol:
        amendedQuote = amendMissedQuotes(missedSymbol, quotes, time)
        oneTimeQuotes = oneTimeQuotes.append(amendedQuote)
    # change columns type
    oneTimeQuotes = asFloatType(oneTimeQuotes)
    # set to the same time
    oneTimeQuotes['currentTime'] = time
    oneTimeQuotes = fillNan(oneTimeQuotes)
    oneTimeQuotes.set_index('currentTime')
    return oneTimeQuotes

def fillNan(df):
    if 'preMarketChangePercent' in df:
        df['preMarketChangePercent'] = df['preMarketChangePercent'].fillna(0)
    if 'postMarketChangePercent' in df:
        df['postMarketChangePercent'] = df['postMarketChangePercent'].fillna(0)
    return df

def asFloatType(oneTimeQuotes):
    for column in oneTimeQuotes.columns.values:
        if column == 'currentTime' or column == 'symbol':
            continue
        # the command below convert the data to numeric, if error happens, fill it with 0
        oneTimeQuotes[column] = pd.to_numeric(oneTimeQuotes[column], errors='coerce').fillna(0)

    return oneTimeQuotes

def amendMissedQuotes(missedSymbol, quotes, time):
    resultQuotes = quotes[(quotes['symbol'] == missedSymbol) & (quotes['currentTime'] < time)]
    result = resultQuotes.tail(1)
    if result.empty:
        resultQuotes = quotes[(quotes['symbol'] == missedSymbol) & (quotes['currentTime'] >time)]
        result = resultQuotes.head(1)
    if result.empty:
        # don't have data in today's file, get the data from previous file
        result = getDataFromPreviousDay(missedSymbol, time)
        if result is None:
            data = [{'averageDailyVolume10Day': 0,'fiftyDayAverage': 0,'postMarketChangePercent': 0,'preMarketChangePercent': 0,
                    'previousClose': 0,'regularMarketChangePercent': 0,'regularMarketDayHigh': 0,'regularMarketDayLow': 0,'regularMarketOpen': 0,
                    'regularMarketPrice': 0,'regularMarketVolume': 0,'symbol': missedSymbol,'twoHundredDayAverage': 0, 'currentTime':time}]
            result = pd.DataFrame(data)
        result['currentTime'] = time
    return result

def getDataFromPreviousDay(symbol, time):
    previousTradingDay = getPreviousTradingDay(time)
    dateStr = previousTradingDay.strftime('%Y%m%d')
    previousDataFile = getTargetFile(dateStr)
    if os.path.isfile(previousDataFile):
        df = pd.read_csv(previousDataFile)
        return df.loc[df['symbol']==symbol].tail(1)
    else: 
        return None

def getPreviousTradingDay(date):
    previousDay = date - timedelta(days=1)
    if not isNoTradingDate(previousDay):
        return previousDay
    previousDay = date - timedelta(days=1)
    if not isNoTradingDate(previousDay):
        return previousDay
    previousDay = date - timedelta(days=1)
    if not isNoTradingDate(previousDay):
        return previousDay
    previousDay = date - timedelta(days=1)
    return previousDay
    

# def printSymbol(sameTimeQuotes):
#     """ 
#     This is a help function
#     filter the symbol not qualified 
#     if the symbol assets or marketCap is too small 
#     or daily volume is too small, it is not qualified
#     """
#     for index, row in sameTimeQuotes.iterrows():
#         capOrAsset = 0
#         averageDailyVolume10Day = 0
#         if row['marketCap'] != '{}':
#             capOrAsset = int(float(row['marketCap']))
#         if row['totalAssets'] != '{}':
#             capOrAsset = int(float(row['totalAssets']))
#         if row['averageDailyVolume10Day'] != '{}' :
#             averageDailyVolume10Day = int(float(row['averageDailyVolume10Day']))
#         if capOrAsset >= 1000000000 and averageDailyVolume10Day >= 1000000: 
#             print(row['symbol'], capOrAsset)

def alignMarketTimeQuotes(quotes):
    quoteDate = toDateTime(quotes['currentTime'].values[0])
    startTime = datetime.combine(quoteDate, marketOpen)
    endTime = datetime.combine(quoteDate, marketClose)
    
    quoteResult = []
    while startTime <= endTime:
        quotesByTime = getQuotesByTime(quotes, startTime)
        # symbols = quotesByTime['symbol'].tolist()
        # if type(quotesByTime_df) == 'None':
        #     quotesByTime_df = quotesByTime
        # else:
        #     quotesByTime_df = pd.concat([quotesByTime_df, quotesByTime], sort=True)
        quoteResult.append(quotesByTime)
        if len(quotesByTime.columns) != 14 :
            print(quotesByTime)
        startTime = startTime + timedelta(minutes=5)
    return pd.concat(quoteResult, sort=True)

def toDateTime(dt64):
    unix_epoch = np.datetime64(0, 's')
    one_second = np.timedelta64(1, 's')
    seconds_since_epoch = (dt64 - unix_epoch) / one_second
    return datetime.utcfromtimestamp(seconds_since_epoch)

"""
This is to read the csv files generated by mixQuotes.py
and align them by the time
then save it to csv
"""
def convertData(csvPath): 
    fileDates = set()
    for file in os.listdir(csvPath):
        date = getDateFromFileName(file, dateRegex=r'\d{8}')
        if date != None:
            fileDates.add(date)
    
    for date in sorted(fileDates):
        print(f'processing {date}')
        indexFile = 'index_' + date + '.csv'
        indexQuotes = readMixIndex(os.path.join(csvPath, indexFile))
        stockFile = 'stock_' + date + '.csv'
        stockQuotes = readMixQuotes(os.path.join(csvPath, stockFile))
        # mix index with stock
        quotes = pd.concat([stockQuotes, indexQuotes], sort=True)
        assert len(quotes.columns) == 14
        # align time
        quotesByTime_df = alignMarketTimeQuotes(quotes)
        assert len(quotesByTime_df.columns) == 14
        
        targetFile = getTargetFile(date)
        print(len(quotesByTime_df))
        print(f'save to file {targetFile}')
        quotesByTime_df = quotesByTime_df.sort_values(by=['currentTime', 'symbol'])
        quotesByTime_df.to_csv(targetFile, index=False, header=True, columns=targetColumns)

def getTargetFile(date):
    return os.path.join(quotesOnedayPath, "data_"+ date +".csv")

if __name__ == '__main__':
    convertData(quotesCsvPath)

    