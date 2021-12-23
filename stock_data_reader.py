"""
before market hour 8:00 - 9:30
market hour 9:30 - 16:00
after market hour 16:00 - 20:00
"""

import json

class StockDataReader: 

    def __init__(self):
        self.previousQuote = {}

    def read(self, file): 
        print(f'reading {file}')
        f = open(file, "r")
        lines = f.readlines()
        quotes = list(filter(None,map(self.parseLine, lines)))
        # print(len(quotes))
        return quotes
        
    def parseLine(self, line): 
        try: 
            lineJson = json.loads(line)
            if len(lineJson) == 66: # some quotes return 66 fields and miss trailingPE
                lineJson['trailingPE'] = 0
            if len(lineJson) != 67:
                print(f"{lineJson['symbol']} has {len(lineJson)} columns, which cannot be processed")
                return None
        except BaseException as err:
            print(f"cannot parse lines {line}")
            return None 
            
        quote = {}
        try:
            for key in lineJson.keys(): 
                if type(lineJson[key]) is dict and 'raw' in lineJson[key].keys(): 
                    quote[key] = lineJson[key]['raw']
                else: 
                    quote[key] = lineJson[key]
            self.previousQuote = quote
        except BaseException as err:
            print(err)
            print(line)
            print(lineJson)
            print("===")
        
        return quote

if __name__ == '__main__':
    reader = StockDataReader()
    reader.read('H:/quotes_process/tar/pyahoo/quotes/AAPL_20211005.json')