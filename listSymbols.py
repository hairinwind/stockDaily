from globalSettings import rawQuotesPath
import os

def listSymbols(path): 
    files = os.listdir(path)
    symbolSet = set()
    for file in files:
        symbol = file.split("_")[0]
        symbolSet.add(symbol.strip())
    return sorted(symbolSet)
        

if __name__ == "__main__":
    symbolSet = listSymbols(rawQuotesPath)
    print(symbolSet)
    print(len(symbolSet))