from datetime import date
from globalSettings import mlDataPath
from mixQuotes import isNoTradingDate
import datetime
import numpy as np
import os
import pandas as pd
import re
import pickle

csvPath = "/home/yao/Downloads/quotes_oneday_data"

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
    startDate = date(2021, 9, 8)
    endDate = date(2021, 10, 1)
    readAndSaveData(startDate, endDate)

    data = readSavedData("2021-09-08")
    print(len(data))
    print(len(data[0]))
