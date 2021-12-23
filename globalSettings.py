from datetime import date

import os
import re

# linux folders
# rawQuotesPath = "/home/yao/Downloads/quotes_tar/pyahoo/quotes"
# mlDataPath = "/home/yao/Downloads/quotes_ml_data"

# windows folders
dir = 'H:/quotes_process'
tarPath = os.path.join(dir, 'tar')
tarArchivePath = os.path.join(tarPath, 'archive')
rawQuotesPath = os.path.join(tarPath, 'pyahoo/quotes')
quotesCsvPath = os.path.join(dir, 'quotes_csv')
quotesOnedayPath = os.path.join(dir, 'quotes_oneday_data')
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
    date(2021,12,24)
]

def isNoTradingDate(date1): 
    if date1 in holidays:
        return True
    if date1.weekday() == 5 or date1.weekday() == 6: # Saturday or Sunday
        return True
    return False

def findStartDateAndEndDate(path, dateRegex=r'\d{4}-\d{2}-\d{2}'):
    files = os.listdir(path)
    dates = [getDateFromFileName(f, dateRegex) for f in files]
    return min(dates), max(dates)

def getDateFromFileName(file, dateRegex=r'\d{4}-\d{2}-\d{2}'):
    match = re.search(dateRegex, file)
    if match != None:
        return match.group()
    return None