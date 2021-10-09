from datetime import datetime, timedelta, time
from globalSettings import targetIndex, rawQuotesPath
from listSymbols import listSymbols

import os
import pandas as pd

targetColumns = ['symbol', 'currentTime', 'regularMarketPrice', 'previousClose', 'regularMarketOpen', 'regularMarketDayHigh', 'regularMarketDayLow', 'regularMarketVolume', 'regularMarketChangePercent', 'postMarketChangePercent', 'preMarketChangePercent', 'averageDailyVolume10Day', 'fiftyDayAverage', 'twoHundredDayAverage']
targetIndexColumns = ['averageDailyVolume10Day', 'currentTime', 'fiftyDayAverage', 'previousClose', 'regularMarketChangePercent', 'regularMarketDayHigh', 'regularMarketDayLow', 'regularMarketOpen', 'regularMarketPrice', 'regularMarketVolume', 'symbol', 'twoHundredDayAverage']

marketOpen = time(9, 30)
marketClose = time(16)

allSymbols = listSymbols(rawQuotesPath)
targetStock = [s for s in allSymbols if s not in targetIndex]

"""
filter symbol and columns
"""
def readMixIndex(file): 
    dailyQuotes = pd.read_csv(file)
    print(dailyQuotes['symbol'])
    sameTimeQuotes = dailyQuotes[dailyQuotes['symbol'].isin(targetIndex)]
    sameTimeQuotes['currentTime'] = pd.to_datetime(sameTimeQuotes['currentTime'])
    sameTimeQuotes = sameTimeQuotes[sameTimeQuotes.columns.intersection(targetIndexColumns)]
    return sameTimeQuotes

def readMixQuoets(file): 
    dailyQuotes = pd.read_csv(file)
    sameTimeQuotes = dailyQuotes[~dailyQuotes['symbol'].isin(targetIndex)]
    sameTimeQuotes['currentTime'] = pd.to_datetime(sameTimeQuotes['currentTime'])
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
    targetSymbol = getTargetSymbol(oneTimeQuotes)
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

def getTargetSymbol(oneTimeQuotes):
    anySymbol = oneTimeQuotes['symbol'].iloc[0]
    if anySymbol in targetIndex: # it is index symbol, return index symbol list
        return targetIndex
    else:
        return targetStock

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
        oneTimeQuotes[column] = oneTimeQuotes[column].astype('float')
    return oneTimeQuotes

def amendMissedQuotes(missedSymbol, quotes, time):
    resultQuotes = quotes[(quotes['symbol'] == missedSymbol) & (quotes['currentTime'] < time)]
    result = resultQuotes.tail(1)
    if result.empty:
        resultQuotes = quotes[(quotes['symbol'] == missedSymbol) & (quotes['currentTime'] >time)]
        result = resultQuotes.head(1)
    return result

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
    quoteDate = quotes['currentTime'][1]
    startTime = datetime.combine(quoteDate, marketOpen)
    endTime = datetime.combine(quoteDate, marketClose)
    
    quotesByTime_df = None
    while startTime <= endTime:
        quotesByTime = getQuotesByTime(quotes, startTime)
        symbols = quotesByTime['symbol'].tolist()
        if type(quotesByTime_df) == 'None':
            quotesByTime_df = quotesByTime
        else:
            quotesByTime_df = pd.concat([quotesByTime_df, quotesByTime])
        # if len(symbols) != len(targetSymbol):
        #     print("quote size not correct by time: ", startTime, len(symbols))
        #     print([symbol for symbol in targetSymbol if symbol not in symbols])
        # if startTime == datetime(2021, 5, 4, 9, 30):
        #     print(quotesByTime.head())
        #     print(quotesByTime.info(verbose=True))
        startTime = startTime + timedelta(minutes=5)
    return quotesByTime_df

"""
This is to read the csv files generated by mixQuotes.py
and align them by the time
then save it to csv
"""
def convertData(csvPath): 
    for file in os.listdir(csvPath):
        if file.startswith('stock') and file.endswith(".csv"):
            csvFile = os.path.join(csvPath, file)
            print("processing ", csvFile)
            quotes = readMixQuoets(csvFile)
            quotesByTime_df =alignMarketTimeQuotes(quotes)
            quoteDate = quotes['currentTime'][1]
            dateStr = quoteDate.strftime("%Y-%m-%d")
            quotesByTime_df.to_csv("~/Downloads/quotes_oneday_data/stock_"+ dateStr +".csv", index=False)
        if file.startswith('index') and file.endswith(".csv"):
            csvFile = os.path.join(csvPath, file)
            print("processing ", csvFile)
            quotes = readMixIndex(csvFile)
            quotesByTime_df =alignMarketTimeQuotes(quotes)
            quoteDate = quotes['currentTime'][1]
            dateStr = quoteDate.strftime("%Y-%m-%d")
            quotesByTime_df.to_csv("~/Downloads/quotes_oneday_data/index_"+ dateStr +".csv", index=False)

if __name__ == '__main__':
    csvPath = "/home/yao/Downloads/quotes_csv"
    convertData(csvPath)

    # df = pd.read_csv('~/Downloads/quotes_oneday_data/stock_20210504.csv')
    # df['currentTime'] = pd.to_datetime(df['currentTime'])
    # df.set_index("currentTime")
    # print(df.head())
    # print(df.info(verbose=True))

    