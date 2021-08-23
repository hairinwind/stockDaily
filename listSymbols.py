import os

def listSymbols(path): 
    files = os.listdir(path)
    symbolSet = set()
    for file in files:
        symbol = file.split("_")[0]
        symbolSet.add(symbol)
    return sorted(symbolSet)
        

if __name__ == "__main__":
    path = "/home/yao/Downloads/quotes_json"
    symbolSet = listSymbols(path)
    print(symbolSet)
    print(len(symbolSet))