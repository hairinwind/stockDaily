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
        f = open(file, "r")
        lines = f.readlines()
        quotes = list(map(self.parseLine, lines))
        # print(len(quotes))
        # print(json.dumps(quotes[0], indent=4))
        return quotes
        
    def parseLine(self, line): 
        try: 
            lineJson = json.loads(line)
            # print(lineJson)
            quote = {}
            for key in lineJson.keys(): 
                if type(lineJson[key]) is dict and 'raw' in lineJson[key].keys(): 
                    quote[key] = lineJson[key]['raw']
                else: 
                    quote[key] = lineJson[key]
            self.previousQuote = quote
        except:
            quote = self.previousQuote
            # print("cannot parse line to json ", line, " is dict", isinstance(lineJson, dict)) 
        return quote

