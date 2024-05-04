import asyncio
import aiohttp
from bs4 import BeautifulSoup
import lxml
import os
from web3 import AsyncWeb3

from utils.abis import UNISWAP_PAIR

PROVIDER_LINK = os.getenv("PROVIDER_LINK")

html = "./files/DEX Screener.html"

provider = AsyncWeb3.AsyncHTTPProvider(PROVIDER_LINK)
web3 = AsyncWeb3(provider)


def get_contract_addresses(soup:BeautifulSoup):
    rows = soup.find_all('a', class_='ds-dex-table-row ds-dex-table-row-new')
    return [{"PAIR_ADDRESS": row['href'].split("/")[-1]} for row in rows]

async def get_paired_token(address):
    contract = web3.eth.contract(address=web3.to_checksum_address(address), abi=UNISWAP_PAIR)
    token_0 =  await contract.functions.token0().call()    
    token_1 =  await contract.functions.token1().call()
    if token_0 == "0x4200000000000000000000000000000000000006":
        return token_1 
    return token_0

async def get_token_data(address)

async def process_page(html):
    with open(html) as f:
        html = f.read()
    soup = BeautifulSoup(html, 'lxml')
    addresses = get_contract_addresses(soup)
    # speed this up with asyncio.gather
    for i in range(0, len(addresses), 10):
        tasks = [get_paired_token(address["PAIR_ADDRESS"]) for address in addresses[i:i+10]]
        tokens = await asyncio.gather(*tasks)
        for address, token in zip(addresses[i:i+10], tokens):
            address["ADDRESS"] = token
        break
    print(addresses)

asyncio.run(process_page(html))