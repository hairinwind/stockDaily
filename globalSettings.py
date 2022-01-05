from datetime import date, time
import os

defaultDatePattern = '%Y%m%d'

# linux folders
# rawQuotesPath = "/home/yao/Downloads/quotes_tar/pyahoo/quotes"
# mlDataPath = "/home/yao/Downloads/quotes_ml_data"

# windows folders.
dir = 'H:/quotes_process'
tarPath = os.path.join(dir, 'tar')
tarArchivePath = os.path.join(tarPath, 'archive')
rawQuotesPath = os.path.join(tarPath, 'pyahoo/quotes')
quotesCsvPath = os.path.join(dir, 'quotes_csv')
quotesOnedayPath = os.path.join(dir, 'quotes_oneday_data')
quotesDailyPath = os.path.join(dir, 'quotes_daily_data')
mlDataPath = ""

targetIndex = ['^DJI', '^GSPC', '^IXIC ', '^NYA', '^RUT', '^TNX', '^VIX', 'DX-Y.NYB', 'CL=F', 'EURUSD=X', 'CNH=F']

# https://www.nyse.com/markets/hours-calendars
holidays = [
    date(2021,1,1),
    date(2021,1,18),
    date(2021,2,15),
    date(2021,4,2),
    date(2021,5,31),
    date(2021,7,5),
    date(2021,9,6),
    date(2021,11,25),
    date(2021,12,24),
    date(2022,1,1),
    date(2022,1,17),
    date(2022,2,21),
    date(2022,4,15),
    date(2022,5,30),
    date(2022,6,20),
    date(2022,7,4),
    date(2022,9,5),
    date(2022,11,24),
    date(2022,12,26)
]

targetColumns = ['symbol', 'currentTime', 'regularMarketPrice', 'previousClose', 'regularMarketOpen', 'regularMarketDayHigh', 'regularMarketDayLow', 
                'regularMarketVolume', 'regularMarketChangePercent', 'postMarketChangePercent', 'preMarketChangePercent', 'averageDailyVolume10Day', 
                'fiftyDayAverage', 'twoHundredDayAverage']

marketOpen = time(9, 45)
marketClose = time(16, 45)

    