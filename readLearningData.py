import numpy as np
import os
import pandas as pd
import re

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

if __name__ == '__main__':
    csvPath = "/home/yao/Downloads/quotes_oneday_data"


    files = [f for f in os.listdir(csvPath) if f.startswith('index') and f.endswith(".csv")]
    for indexFile in sorted(files):
        stockFile = getStockFile(indexFile)
        print(indexFile,stockFile)
        index_df = pd.read_csv(os.path.join(csvPath, indexFile))
        stock_df = pd.read_csv(os.path.join(csvPath, stockFile))
        
        indexFlatten = flattenByTime(index_df)
        stockFlatten = flattenByTime(stock_df)
        data = mergeIndexWithStock(indexFlatten, stockFlatten)
        print(len(data))
        print("data0:", data[0])
        print("data1", data[1])

        my_df = pd.DataFrame(data)
        my_df.to_csv("data.csv")
        