from datetime import date
from finta import TA
from globalSettings import mlDataPath
from mixQuotes import isNoTradingDate
import datetime
import numpy as np
import os
import pandas as pd
import re
import pickle

csvPath = "/home/yao/Downloads/quotes_oneday_data/"

def getStockFile(indexFile):
    date = getDateFromFileName(indexFile)
    return 'stock_'+date+'.csv'

def getDateFromFileName(indexFile):
    match = re.search(r'\d{4}-\d{2}-\d{2}', indexFile)
    return match.group()

def flattenByTime(df):
    result = []
    dfGroupedByTime = df.groupby("currentTime")
    for key in dfGroupedByTime.groups.keys():
        result.append(dfGroupedByTime.get_group(key).values.flatten())
    return result

def mergeIndexWithStock(indexFlatten, stockFlatten):
    result = []
    for i in range(len(indexFlatten)):
        merged = np.concatenate((indexFlatten[i], stockFlatten[i]))
        result.append(merged)
        # if i == 0:
        #     print(indexFlatten)
        #     print(stockFlatten)
        #     print(merged)
        #     print(len(indexFlatten[0]), len(stockFlatten[0]), len(merged))
    return result

def readLearningData(csvPath, indexFile): 
    stockFile = getStockFile(indexFile)
    # print(indexFile,stockFile)
    index_df = pd.read_csv(os.path.join(csvPath, indexFile))
    stock_df = pd.read_csv(os.path.join(csvPath, stockFile))
    
    indexFlatten = flattenByTime(index_df)
    stockFlatten = flattenByTime(stock_df)
    data = mergeIndexWithStock(indexFlatten, stockFlatten)
    return data

def readLearningDataByDate(csvPath, date):
    indexFile = 'index_' + date + '.csv'
    return readLearningData(csvPath, indexFile)

"""
- this method is to read one day csv
- mix stock and index into one dateframe
- 5 minutes data to daily data
- add custom indicators 
- and save the new dataframe to csv
"""
def readAndSaveToCsv(startDate, endDate):
    periodRange = pd.period_range(start=startDate, end=endDate, freq='D')
    for index, day in enumerate(periodRange):
        date1 = date(day.year, day.month, day.day)
        if not isNoTradingDate(date1):
            print(f'process data of {day}')
            df = mergeStockAndIndexDataFrame(day)
            dailyDataFrame = getDailyDataFrame(df) 
            addCustomIndicators(dailyDataFrame)
            dailyDataFrame.to_csv(getDailyCsvFilePath(day))

def getDailyCsvFilePath(day):
    fileName = "data_" + day.strftime('%Y-%m-%d') + ".csv"
    return os.path.join(mlDataPath, fileName)

def mergeStockAndIndexDataFrame(day):
    date1 = date(day.year, day.month, day.day)
    if not isNoTradingDate(date1): 
        quoteDate = date1.strftime('%Y-%m-%d')
        indexFile = 'index_' + quoteDate + '.csv'
        stockFile = 'stock_' + quoteDate + '.csv'
        index_df = pd.read_csv(os.path.join(csvPath, indexFile))
        index_df['preMarketChangePercent'] = 0
        index_df['postMarketChangePercent'] = 0
        stock_df = pd.read_csv(os.path.join(csvPath, stockFile))
        union_df = pd.concat([stock_df, index_df], ignore_index=True)
        return union_df

def getDailyDataFrame(df):
    grouped = df.groupby("symbol")
    result = []
    for group in grouped:
        # group is a tuple, group[0] is the key, group[1] is the dataframe grouped by the symbol column
        # fetch the last record as daily record
        result.append(group[1].iloc[-1])
    dailyDataFrame = pd.concat(result, axis=1, ignore_index=True).T
    dailyDataFrame.rename(columns={'regularMarketOpen':'Open', 'regularMarketPrice':'Close', 'regularMarketDayLow':'Low', 'regularMarketDayHigh':'High', 'regularMarketVolume':'Volume'}, inplace=True)
    return dailyDataFrame

def addCustomIndicators(symbolDateFrame): 
    symbolDateFrame['SMA20'] = TA.SMA(symbolDateFrame, 20)
    symbolDateFrame['RSI'] = TA.RSI(symbolDateFrame)
    symbolDateFrame['OBV'] = TA.OBV(symbolDateFrame)
    symbolDateFrame.fillna(0, inplace=True)

# this is to save data in one dimension array
def readAndSaveData(startDate, endDate):
    periodRange = pd.period_range(start=startDate, end=endDate, freq='D')
    for day in periodRange:
        date1 = date(day.year, day.month, day.day)
        if not isNoTradingDate(date1): 
            quoteDate = date1.strftime('%Y-%m-%d')
            data = readLearningDataByDate(csvPath, quoteDate)
            save(data, quoteDate)

def readSavedData(fileDate):
    dataFile = getDataFileName(fileDate)
    with open(dataFile, 'rb') as filehandle:
        data = pickle.load(filehandle)
    return data

def save(data, fileDate):
    dataFile = getDataFileName(fileDate)
    with open(dataFile, 'wb') as filehandle:
        pickle.dump(data, filehandle)

def getDataFileName(fileDate):
    fileName = "data_{}.pickle".format(fileDate)
    csvDataFile = os.path.join(mlDataPath, fileName)
    return csvDataFile

def test1(csvPath):
    files = [f for f in os.listdir(csvPath) if f.startswith('index') and f.endswith(".csv")]
    for indexFile in sorted(files):
        data = readLearningData(csvPath, indexFile)
        print("data rows: ", len(data))
        for dataItem in data:
            print("columns in one row: ", len(dataItem))
        my_df = pd.DataFrame(data)

def test2(getDataFileName, quoteDate):
    with open(getDataFileName(quoteDate), 'rb') as filehandle:
        data1 = pickle.load(filehandle)
    for dataItem in data1:
        if (len(dataItem) != 1678):
            print(dataItem)
    print(data1[0])




if __name__ == '__main__':
    startDate, endDate = findStartDateAndEndDate()
    print(f'startDate:{startDate}, endDate:{endDate}')
    
    # readAndSaveData(startDate, endDate)
    # data = readSavedData("2021-09-08")
    # print(len(data))
    # print(len(data[0]))

    readAndSaveToCsv(startDate, endDate)