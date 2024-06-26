import numpy as np
import os
import pandas as pd
import requests

BASE_API_KEY = os.getenv("BASE_API_KEY")

def read_all_data():
    # TBD where all the data is stored, right now - combined.csv
    return pd.read_csv("out/combined.csv")

def get_current_block():
    url = f"https://api.basescan.org/api?module=proxy&action=eth_blockNumber&apikey={BASE_API_KEY}"
    res = requests.get(url)
    return int(res.json()["result"], 16)

def get_pair_return(pair_df, buy_after_block, sell_after_block, weth, latest_block):
    if len(pair_df) < 2:
        return 0
    first_block = pair_df[pair_df["action"]=="add"]["blockNumber"].values[0]
    try:
        last_block = int(pair_df[pair_df["action"]=="remove"]["blockNumber"].values[0])
    except:
        last_block = latest_block
    pair_df = pair_df[(pair_df["blockNumber"] < last_block) & (pair_df["blockNumber"] > first_block)]
    # last_block = min(int(pair_df[pair_df["action"]=="remove"]["blockNumber"].values[0]), latest_block)
    buy_block = first_block + buy_after_block
    buy_price = pair_df.iloc[(pair_df["blockNumber"] - buy_block).abs().argsort()[:1]].iloc[0]["price"]
    sell_block = first_block + sell_after_block
    # print(f"Sell block: {sell_block}, Last block: {last_block}")
    if sell_block >= last_block:
        return 0
    # wrongly used iloc here, should use the last trade BEFORE remove
    sell_price = pair_df.iloc[(pair_df["blockNumber"] - sell_block).abs().argsort()[:1]].iloc[0]["price"]
    # print(f"Buy price: {buy_price}, Sell price: {sell_price}, bought: {weth/buy_price}, sold: {(weth/buy_price) * sell_price}")
    return (weth/buy_price) * sell_price

def simulate(data, total_investment, buy_after_block, sell_after_block, latest_block, sell_safety_blocks=None, unique_tokens=None):
    if not unique_tokens:
        unique_tokens = data["address"].unique()
    total_pairs = len(unique_tokens)
    split = total_investment / total_pairs
    returns = []
    max_return = 0
    max_token = None
    for token in unique_tokens:
        pair_df = data[data["address"]==token]
        weth = split
        buy_after_block = buy_after_block
        sell_after_block = sell_after_block
        if sell_safety_blocks:
            weth = weth/2
            pair_return_safety = get_pair_return(pair_df, buy_after_block, sell_safety_blocks, weth, latest_block)
        else:
            pair_return_safety = 0
        pair_return_final = get_pair_return(pair_df, buy_after_block, sell_after_block, weth, latest_block)
        pair_return = pair_return_safety + pair_return_final
        if pair_return > max_return:
            max_return = pair_return
            max_token = token
        returns.append(pair_return)
    print(f"Max return: {max_return} for token: {max_token}")
    return sum(returns)

def main():
    data = read_all_data()
    latest_block = get_current_block()
    print(latest_block)
    total_investment = 0.07 # always in weth

    #print(get_pair_return(data[data["token"]=="PUPS"], 20, 270, 0.003, latest_block))
    

    # find optimal buy_after_block and sell_after_block

    # basic test - grid search, single entry single exit -- ca. earliest entry, leave around 1000 blocks
    max_return = 0
    best_buy_after_block = 0
    best_sell_after_block = 0
    # for buy_after_block in range(70, 100, 10):
    #     for sell_after_block in range(500, 1100, 10):
    #         return_ = simulate(data, total_investment, buy_after_block, sell_after_block, latest_block)
    #         print(f"buy_after_block: {buy_after_block}, sell_after_block: {sell_after_block}, return: {return_}")
    #         if return_ > max_return:
    #             max_return = return_
    #             best_buy_after_block = buy_after_block
    #             best_sell_after_block = sell_after_block

    best_lp = 0.0
    # simulate different initial LP pool sizes
    add_per_token = data.groupby('address').first().reset_index()
    add_per_token["weth_lp"] = np.where(add_per_token["base"] < add_per_token["quote"], add_per_token["base"], add_per_token["quote"])
    # range 0 to 3, step 0.1
    buy_after_block = 30
    sell_after_block = 1060
    for weth in [0.0, 1.0, 2.0, 3.0]:
        tokens = add_per_token[add_per_token["weth_lp"] >= weth]["address"].tolist()
        return_ = simulate(data, total_investment, buy_after_block, sell_after_block, latest_block, unique_tokens=tokens)
        print(f"lp: {weth}, buy_after_block: {buy_after_block}, sell_after_block: {sell_after_block}, return: {return_}")
        if return_ > max_return:
            max_return = return_
            best_lp = weth
            best_buy_after_block = buy_after_block
            best_sell_after_block = sell_after_block
    print(f"Best return: {max_return}, best_lp: {best_lp}, no of tokens: {len(tokens)}, buy_after_block: {best_buy_after_block}, sell_after_block: {best_sell_after_block}, total gain: {max_return - total_investment}")
            # for sell_safety_blocks in range(0, 300, 10):
            #     return_ = simulate(data, total_investment, buy_after_block, sell_after_block, latest_block, sell_safety_blocks)
            #     print(f"buy_after_block: {buy_after_block}, sell_after_block: {sell_after_block}, return: {return_}, safety: {sell_safety_blocks}")
            #     if return_ > max_return:
            #         max_return = return_
            #         best_buy_after_block = buy_after_block
            #         best_sell_after_block = sell_after_block
    
    print(f"Best return: {max_return}, buy_after_block: {best_buy_after_block}, sell_after_block: {best_sell_after_block}, total gain: {max_return - total_investment}")

if __name__ == "__main__":
    main()