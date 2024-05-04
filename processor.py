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

html = "./files/DEX Screener.html"

provider = AsyncWeb3.AsyncHTTPProvider(PROVIDER_LINK)
web3 = AsyncWeb3(provider)

LATEST_BLOCK = 0


def get_contract_addresses(soup: BeautifulSoup):
    rows = soup.find_all("a", class_="ds-dex-table-row ds-dex-table-row-new")
    return [{"PAIR_ADDRESS": row["href"].split("/")[-1]} for row in rows]


async def get_paired_token(address):
    if not address:
        return
    contract = web3.eth.contract(
        address=web3.to_checksum_address(address), abi=UNISWAP_PAIR
    )
    token_0 = await contract.functions.token0().call()
    token_1 = await contract.functions.token1().call()
    token_data = {}
    if token_0 == "0x4200000000000000000000000000000000000006":
        token_data = await get_token_data(token_1)
    else:
        token_data = await get_token_data(token_0)
    # liquidity_data = await get_liquidity_events(address)
    # print(liquidity_data)
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


async def get_liquidity_events(address):
    # rewrite using jsonrpc
    payload = get_json_payload(
        "eth_getLogs",
        fromBlock=LATEST_BLOCK,
        toBlock="latest",
        address=address,
        topics=["0xdccd412f0b1252819cb1fd330b93224ca42612892bb3f4f789976e6d81936496", "0x4c209b5fc8ad50758f13e2e1088ba56a560dff690a1c6fef26394f4c03821c4f"],
    )
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_getLogs",
        "params": [
            {
                "fromBlock": "0xd5eb21",
                "toBlock": "latest",
                "address": address,
                "topics": [
                    "0xdccd412f0b1252819cb1fd330b93224ca42612892bb3f4f789976e6d81936496"
                ],
            }
        ],
    }

    print(payload)
    print(PROVIDER_LINK)

    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.developer.coinbase.com/rpc/v1/base/wd7CKNfSnWyjmYdCaxBUCe8BUM_onk9C",
            json=payload,
            headers=headers,
        ) as response:
            data = await response.json()
            return data


async def get_pair_events(contract):
    # get sync and liquidity events
    ...


async def process_token(pair_address):
    token = await get_paired_token(pair_address["PAIR_ADDRESS"])
    if token:
        pair_address.update(await get_token_data(token))


async def process_page(html):
    synced_block_ts = time.time()
    LATEST_BLOCK = await get_latest_block()
    print(LATEST_BLOCK)
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
