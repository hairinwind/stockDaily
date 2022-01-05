from datetime import datetime
from globalSettings import holidays

import os
import pandas as pd
import re

"""
input 20210831, 20211102
returns [
    (20210831, 20210831),
    (20210901, 20210930),
    (20211001, 20211031),
    (20211101, 20211102)
]
"""
def getMonthlyPeriod(startDate, endDate):
    result = []
    periodRange = pd.period_range(start=startDate, end=endDate, freq='M')
    for period in periodRange:
        result.append(getPeriodIntersection(period, startDate, endDate))
    return result

"""
returns the intersection of the period and the startDate - endDate
for example, period is 2021-08, startDate is 20210815, endDate is 20210910
it shall return (2021-08-15, 2021-08-31)
"""
def getPeriodIntersection(period, startDate, endDate):
    startDate = parseDate(startDate)
    endDate = parseDate(endDate)
    periodStartDate = period.start_time.to_pydatetime()
    periodEndDate = period.end_time.to_pydatetime()
    return (max(periodStartDate, startDate), min(periodEndDate, endDate))

def parseDate(dateText, pattern='%Y%m%d'):
    if type(dateText) == str:
        return datetime.strptime(dateText, pattern)
    else:
        return dateText

def formatDate(date, pattern='%Y%m%d'):
    return datetime.strftime(date, pattern)        

def isNoTradingDate(date1): 
    if date1 in holidays:
        return True
    if date1.weekday() == 5 or date1.weekday() == 6: # Saturday or Sunday
        return True
    return False

def findStartDateAndEndDate(path, dateRegex=r'\d{8}'):
    files = os.listdir(path)
    dates = [getDateFromFileName(f, dateRegex) for f in files]
    return min(dates), max(dates)

def getDateFromFileName(file, dateRegex=r'\d{8}'):
    match = re.search(dateRegex, file)
    if match != None:
        return match.group()
    return None

def saveOrAppendCsv(df, csvFile):
    if os.path.isfile(csvFile):
        df.to_csv(csvFile, mode='a', header=False, index=False)
    else:
        df.to_csv(csvFile, index=False)