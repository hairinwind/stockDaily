from datetime import datetime, timedelta
from globalSettings import quotesOnedayPath, rawQuotesPath, quotesDailyPath, findStartDateAndEndDate, saveOrAppendCsv
from finta import TA
from listSymbols import listSymbols

import os
import pandas as pd

# def getLastDateFromDailyFile(symbol):
#     dailyFileName = getDailyFileName(symbol)
#     dailyCsvFile = os.path.join(quotesDailyPath, dailyFileName)
#     if os.path.isfile(dailyCsvFile):
#         df = pd.read_csv(dailyCsvFile)
#         df.sort_values(by=['currentTime'])
#         return df['currentTime'].values[-1]

def getDailyFileName(symbol):
    return symbol + "_daily.csv"

def addCustomIndicators(dailyQuotes):
    dailyQuotes.rename(columns={'regularMarketOpen':'Open', 'regularMarketPrice':'Close', 'regularMarketDayLow':'Low', 'regularMarketDayHigh':'High', 'regularMarketVolume':'Volume'}, inplace=True)
    dailyQuotes.reset_index(drop=True, inplace=True)
    dailyQuotes['SMA20'] = TA.SMA(dailyQuotes, 20)
    dailyQuotes['SMM20'] = TA.SMM(dailyQuotes, 20)
    dailyQuotes['RSI'] = TA.RSI(dailyQuotes)
    dailyQuotes['OBV'] = TA.OBV(dailyQuotes)
    dailyQuotes.fillna(0, inplace=True)

def generate():
    symbols = listSymbols(rawQuotesPath)
    startDate, endDate = findStartDateAndEndDate(rawQuotesPath)
    for symbol in symbols:
        # date = getLastDateFromDailyFile(symbol)
        # if date is not None:
        #     newStartDate = date + timedelta(days=1)
        # else:
        #     newStartDate = startDate
        print(f'processing {symbol}')
        periodRange = pd.period_range(start=startDate, end=endDate, freq='D')
        symbolDailyResult = []
        for day in periodRange:
            fiveMinuteDataFileName = "data_" + day.strftime('%Y%m%d') + ".csv"
            fiveMinuteDataFilePath = os.path.join(quotesOnedayPath, fiveMinuteDataFileName)
            if os.path.isfile(fiveMinuteDataFilePath):
                fiveMinutesData = pd.read_csv(fiveMinuteDataFilePath) #, dtype={'currentTime': 'datetime'}
                fiveMinutesData = fiveMinutesData[fiveMinutesData['symbol'] == symbol]
                lastData = fiveMinutesData.tail(1)
                symbolDailyResult.append(lastData)
        targetFile = os.path.join(quotesDailyPath, getDailyFileName(symbol))
        dailyQuotes = pd.concat(symbolDailyResult, sort=True)
        addCustomIndicators(dailyQuotes)
        saveOrAppendCsv(dailyQuotes, targetFile)

if __name__ == '__main__':
    generate()