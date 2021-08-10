from datetime import datetime, timedelta
import os
import pandas as pd

filterSymbol = ['AINV', 'BRID', 'BRZU', 'CFBK', 'CHAD', 'CHAU', 'CL=F', 'CLAR', 'CURE', 'CWEB', 'DFEN', 'DMRC', 'DPK', 'DRIP', 'DZK', 'EDC', 'EDZ', 'ERIE', 'EURL', 'EURUSD=X', 'FRPT', 'GASL', 'GC=F', 'GLOB', 'GUSH', 'GWGH', 'HFFG', 'INDL', 'INS', 'JAGX', 'JDST', 'JYNT', 'KNOW', 'LABD', 'LBJ', 'LFVN', 'LRN', 'MIDU', 'MIDZ', 'MSON', 'NAIL', 'NOA', 'NSSC', 'NSTG', 'PAR', 'PAYS', 'PDVW', 'PILL', 'PNRG', 'QQQE', 'RETL', 'RFL', 'RUSL', 'SHSP','SPUU', 'TMV', 'TPB', 'TPOR', 'TYD', 'TYO',  'UBOT', 'UTSL', 'WDRW', 'WK', ]
#  'CLAR', 'CURE', 'DFEN', 'DMRC', ,'YANG'

# to watch 
# VGK
# gold
# ^TNX 10 年期长期利率 和 bond 票面价值成反比
# use KO to replace coke

targetSymbol = ['AAPL', 'BAC', 'C', 'COKE', 'CORE', 'DAC', 'DPST', 'DRN', 'DUSL', 'DUST', 'ERX', 'ERY', 'FAS', 'FAZ', 'MSFT', 'SOXL', 'SOXS',  'SPXL', 'SPXS', 'TECL', 'TECS', 'TNA', 'TSLA']

targetColumns = []

def readMixQuoets(file): 
    dailyQuotes = pd.read_csv(file)
    sameTimeQuotes = dailyQuotes[dailyQuotes['symbol'].isin(targetSymbol)]
    sameTimeQuotes['currentTime'] = pd.to_datetime(sameTimeQuotes['currentTime'])
    return sameTimeQuotes       

def getQUotesByTime(quotes, time):
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
    return oneTimeQuotes

def amendMissedQuotes(missedSymbol, quotes, time):
    resultQuotes = quotes[(quotes['symbol'] == missedSymbol) & (quotes['currentTime'] < time)]
    result = resultQuotes.tail(1)
    if result.empty:
        resultQuotes = quotes[(quotes['symbol'] == missedSymbol) & (quotes['currentTime'] >time)]
        result = resultQuotes.head(1)
    return result

def printSymbol(sameTimeQuotes):
    """ 
    This is a help function
    filter the symbol not qualified 
    if the symbol assets or marketCap is too small 
    or daily volume is too small, it is not qualified
    """
    for index, row in sameTimeQuotes.iterrows():
        capOrAsset = 0
        averageDailyVolume10Day = 0
        if row['marketCap'] != '{}':
            capOrAsset = int(float(row['marketCap']))
        if row['totalAssets'] != '{}':
            capOrAsset = int(float(row['totalAssets']))
        if row['averageDailyVolume10Day'] != '{}' :
            averageDailyVolume10Day = int(float(row['averageDailyVolume10Day']))
        if capOrAsset >= 1000000000 and averageDailyVolume10Day >= 1000000: 
            print(row['symbol'], capOrAsset)

if __name__ == '__main__':
    csvPath = "/home/yao/Downloads/quotes_csv"
    csvFile = os.path.join(csvPath, "stock_20210504.csv")
    quotes = readMixQuoets(csvFile)

    startTime = datetime(2021, 5, 4, 9, 30)
    endTime = datetime(2021, 5, 4, 16)
    while startTime <= endTime:
        quotesByTime = getQUotesByTime(quotes, startTime)
        
        symbols = quotesByTime['symbol'].tolist()
        if len(symbols) != len(targetSymbol):
            print("quote size not correct by time: ", startTime, len(symbols))
            print([symbol for symbol in targetSymbol if symbol not in symbols])

        if startTime == datetime(2021, 5, 4, 9, 30):
            print(quotesByTime)
        
        startTime = startTime + timedelta(minutes=5)

    