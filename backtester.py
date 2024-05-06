import pandas as pd

def read_all_data():
    # TBD where all the data is stored, right now - combined.csv
    df = pd.read_csv("out/combined.csv")

def get_pair_return(pair_df, buy_after_block, sell_after_block, weth):
    first_block = pair_df[pair_df["action"]=="add"]["blockNumber"].values[0]
    last_block = pair_df[pair_df["action"]=="remove"]["blockNumber"].values[0]
    buy_block = first_block + buy_after_block
    buy_price = pair_df.iloc[(pair_df["blockNumber"] - buy_block).abs().argsort()[:1]].iloc[0]["price"]
    sell_block = last_block + sell_after_block
    sell_price = pair_df.iloc[(pair_df["blockNumber"] - sell_block).abs().argsort()[:1]].iloc[0]["price"]
    return (weth/buy_price) * sell_price