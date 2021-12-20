import pandas as pd

csvFile = '/home/yao/Downloads/quotes_oneday_data/stock_2021-10-01.csv'

df = pd.read_csv(csvFile)
print(df.head(15))
apple_df = df[df['symbol']=='AAPL']
print(apple_df.head(15))
print(apple_df.dtypes)
print(apple_df['regularMarketOpen'].value_counts())
print(apple_df.iloc[-1])