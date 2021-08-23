from datetime import datetime, timedelta, time
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

targetColumns = ['symbol', 'currentTime', 'regularMarketPrice', 'previousClose', 'regularMarketOpen', 'regularMarketDayHigh', 'regularMarketDayLow', 'regularMarketVolume', 'regularMarketChangePercent', 'postMarketChangePercent', 'preMarketChangePercent', 'averageDailyVolume10Day', 'fiftyDayAverage', 'twoHundredDayAverage']
print(len(targetColumns))
marketOpen = time(9, 30)
marketClose = time(16)

def readMixQuoets(file): 
    dailyQuotes = pd.read_csv(file)
    sameTimeQuotes = dailyQuotes[dailyQuotes['symbol'].isin(targetSymbol)]
    sameTimeQuotes['currentTime'] = pd.to_datetime(sameTimeQuotes['currentTime'])
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
    # filter columns 
    oneTimeQuotes = oneTimeQuotes[oneTimeQuotes.columns.intersection(targetColumns)]
    # change columns type
    oneTimeQuotes = asFloatType(oneTimeQuotes)
    # set to the same time
    oneTimeQuotes['currentTime'] = time
    oneTimeQuotes = fillNan(oneTimeQuotes)
    oneTimeQuotes.set_index('currentTime')
    return oneTimeQuotes

def fillNan(df):
    df['preMarketChangePercent'] = df['preMarketChangePercent'].fillna(0)
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

def readMarketTimeQuotes(quotes):
    # startTime = datetime(2021, 5, 4, 9, 30)
    # endTime = datetime(2021, 5, 4, 16)
    quoteDate = datetime(2021,5,4)
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
        if len(symbols) != len(targetSymbol):
            print("quote size not correct by time: ", startTime, len(symbols))
            print([symbol for symbol in targetSymbol if symbol not in symbols])
        if startTime == datetime(2021, 5, 4, 9, 30):
            print(quotesByTime.head())
            print(quotesByTime.info(verbose=True))
        startTime = startTime + timedelta(minutes=5)
    quotesByTime_df.to_csv("~/Downloads/test.csv", index=False)

if __name__ == '__main__':
    csvPath = "/home/yao/Downloads/quotes_csv"
    csvFile = os.path.join(csvPath, "stock_20210504.csv")
    quotes = readMixQuoets(csvFile)
    readMarketTimeQuotes(quotes)

    df = pd.read_csv('~/Downloads/test.csv')
    df['currentTime'] = pd.to_datetime(df['currentTime'])
    df.set_index("currentTime")
    print(df.head())
    print(df.info(verbose=True))

    