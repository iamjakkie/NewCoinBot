import asyncio
import aiohttp
from bs4 import BeautifulSoup
import lxml
import os
import random
import time
from web3 import AsyncWeb3

from utils.abis import UNISWAP_PAIR, ERC20
from utils.payload import get_json_payload

PROVIDER_LINK = os.getenv("PROVIDER_LINK")
BASE_API_KEY = os.getenv("BASE_API_KEY")

html = "./files/DEX Screener.html"

provider = AsyncWeb3.AsyncHTTPProvider(PROVIDER_LINK)
web3 = AsyncWeb3(provider)

LATEST_BLOCK = 0
HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}


def get_contract_addresses(soup: BeautifulSoup):
    rows = soup.find_all("a", class_="ds-dex-table-row ds-dex-table-row-new")
    return [{"PAIR_ADDRESS": row["href"].split("/")[-1]} for row in rows]

async def get_contract_creation_block(address):
    url = "".join(f"""https://api.basescan.org/api
        ?module=account
        &action=txlistinternal
        &address={address}
        &startblock=0
        &endblock=latest
        &page=1
        &offset=10
        &sort=asc
        &apikey={BASE_API_KEY}""".split())
    print(url)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            return int(data["result"][0]["blockNumber"])

async def get_paired_token(address):
    if not address:
        return
    contract = web3.eth.contract(
        address=web3.to_checksum_address(address), abi=UNISWAP_PAIR
    )
    created_at = await get_contract_creation_block(address)
    print(created_at)
    token_0 = await contract.functions.token0().call()
    token_1 = await contract.functions.token1().call()
    token_data = {}
    if token_0 == "0x4200000000000000000000000000000000000006":
        token_data = await get_token_data(token_1)
    else:
        token_data = await get_token_data(token_0)
    # liquidity_data = await get_liquidity_events(address, created_at)
    sync_data = await get_sync_events(address, created_at)
    print(sync_data[0])
    print(sync_data[-2])
    # sync_data = await get_sync_events(contract)


async def get_token_data(address):
    if not address:
        return
    contract = web3.eth.contract(address=web3.to_checksum_address(address), abi=ERC20)
    symbol = await contract.functions.symbol().call()
    supply = await contract.functions.totalSupply().call()
    return {"address": address, "symbol": symbol, "supply": int(supply) / 10**18}


async def get_latest_block():
    block = await web3.eth.get_block("latest")
    return block["number"]

async def get_sync_events(address, created_at):
    global LATEST_BLOCK
    current_block = created_at
    events = []
    while current_block < LATEST_BLOCK:
        payload = get_json_payload(
            "eth_getLogs",
            fromBlock=hex(current_block),
            toBlock=hex(current_block + 500),
            address=address,
            topics=["0x1c411e9a96e071241c2f21f7726b17ae89e3cab4c78be50e062b03a9fffbbad1"],
        )
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.developer.coinbase.com/rpc/v1/base/wd7CKNfSnWyjmYdCaxBUCe8BUM_onk9C",
                json=payload,
                headers=HEADERS,
            ) as response:
                data = await response.json()

        if data:
            res = data["result"]
            for event in res:
                amounts = event["data"]
                amount_0 = int(amounts[:66], 16)/10**18
                amount_1 = int(amounts[66:], 16)/10**18
                normalised_event = {
                    "blockNumber": int(event["blockNumber"], 16),
                    "transactionHash": event["transactionHash"],
                    "action": "trade",
                    "base": amount_0,
                    "quote": amount_1
                }
                events.append(normalised_event)
        current_block += 500
    return events

async def get_liquidity_events(address, created_at):
    global LATEST_BLOCK
    current_block = created_at
    events = []
    while current_block < LATEST_BLOCK:
        payload = get_json_payload(
            "eth_getLogs",
            fromBlock=hex(current_block),
            toBlock=hex(current_block + 500),
            address=address,
            topics=[["0xdccd412f0b1252819cb1fd330b93224ca42612892bb3f4f789976e6d81936496", "0x4c209b5fc8ad50758f13e2e1088ba56a560dff690a1c6fef26394f4c03821c4f"]],
        )
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.developer.coinbase.com/rpc/v1/base/wd7CKNfSnWyjmYdCaxBUCe8BUM_onk9C",
                json=payload,
                headers=HEADERS,
            ) as response:
                data = await response.json()
        if data:
            res = data["result"]
            for event in res:
                #"0x0000000000000000000000000000000000000000000000000e3a2e32d4cae5010000000000000000000000000000000000000009dc85af359ea417c37727aa0c" translates to amount0 : 1025182661033518337 amount1 : 781301779326326925118560250380, code this logic
                amounts = event["data"]
                amount_0 = int(amounts[:66], 16)/10**18
                amount_1 = int(amounts[66:], 16)/10**18
                normalised_event = {
                    "blockNumber": int(event["blockNumber"], 16),
                    "transactionHash": event["transactionHash"],
                    "action": "add" if event["topics"][0] == "0x4c209b5fc8ad50758f13e2e1088ba56a560dff690a1c6fef26394f4c03821c4f" else "remove",
                    "base": amount_0,
                    "quote": amount_1
                }
                events.append(normalised_event)
        current_block += 500
    return events

async def get_pair_events(contract):
    # get sync and liquidity events
    ...

async def save_to_db(data):
    # save to sqlite
    ...

async def save_to_redis(pair_address):
    ...

async def check_pair(pair_address):
    # check if pair exists in redis
    ...

async def process_token(pair_address):
    # check if this pair was not processed before
    if await check_pair(pair_address):
        return
    token = await get_paired_token(pair_address["PAIR_ADDRESS"])
    if token:
        pair_address.update(await get_token_data(token))


async def process_page(html):
    synced_block_ts = time.time()
    global LATEST_BLOCK
    LATEST_BLOCK = await get_latest_block()
    with open(html) as f:
        html = f.read()
    soup = BeautifulSoup(html, "lxml")
    addresses = get_contract_addresses(soup)
    # speed this up with asyncio.gather
    for i in range(0, len(addresses), 2):
        tasks = [process_token(address) for address in addresses[i : i + 2]]
        await asyncio.gather(*tasks)
        # update address with token data

        # for address, token in zip(addresses[i:i+10], tokens):
        #     address["ADDRESS"] = token
        #     address.update(await get_token_data(token))
        break
    # print(addresses[:10])


asyncio.run(process_page(html))
