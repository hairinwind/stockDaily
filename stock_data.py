import numbers

class StockData: 
    
    def getLearningData(self, quote):
        volume = quote['volume'] if quote['volume'] else quote['regularMarketVolume']
        navPrice = quote['navPrice'] if isinstance(quote['navPrice'], numbers.Number) else 0
        # dayLow regularMarketDayLow
        # dayHigh regularMarketDayHigh
        result = [0] * 22
        result[0] = quote['previousClose'] # 0 - previousClose 
        result[1] = quote['regularMarketOpen'] # 1 - open
        result[2] = round(quote['regularMarketPrice'] - quote['twoHundredDayAverage'], 2) #2 diff twoHundredDayAverage
        result[3] = round(quote['regularMarketDayHigh'], 2) #3 high
        result[4] = round(quote['regularMarketPrice'] - navPrice, 2) #4 diff navPrice
        result[5] = round(volume/quote['averageVolume10days']*100) #5 diff averageVolume10days
        result[6] = quote['yield'] #6 yield
        result[7] = round(quote['regularMarketDayLow'], 2) #7 low
        result[8] = round(volume/quote['averageVolume']*100) #8 diff averageVolume
        result[9] = quote['ask'] #9 ask
        result[10] = quote['askSize'] #10 askSize
        result[11] = round(quote['regularMarketPrice'] - quote['fiftyTwoWeekHigh'], 2) #11 diff fiftyTwoWeekHigh
        result[12] = round(quote['regularMarketPrice'] - quote['fiftyTwoWeekLow'], 2) #12 diff fiftyTwoWeekLow
        result[13] = quote['regularMarketChange'] #13 regularMarketChange
        result[14] = quote['regularMarketChangePercent'] #14 regularMarketChangePercent
        result[15] = quote['regularMarketTime'] #15 regularMarketTime
        result[16] = quote['preMarketChangePercent'] #16 preMarketChangePercent
        result[17] = quote['preMarketPrice'] #17 preMarketPrice
        result[18] = quote['preMarketChange'] #18 preMarketChange
        result[19] = round(quote['regularMarketPrice'] - quote['preMarketChange'], 2) #19 diff  preMarketPrice
        result[20] = quote['regularMarketPrice'] # 20 price
        result[21] = volume #21 volume
        return result

    def getPrice(self, data): 
        return data[20]