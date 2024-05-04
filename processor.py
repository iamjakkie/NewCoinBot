import asyncio
import aiohttp
from bs4 import BeautifulSoup
import lxml
import os
from web3 import AsyncWeb3

from utils.abis import UNISWAP_PAIR, ERC20

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

async def get_token_data(address):
    contract = web3.eth.contract(address=web3.to_checksum_address(address), abi=ERC20)
    symbol = await contract.functions.symbol().call()
    supply = await contract.functions.totalSupply().call()
    return {"address": address, "symbol": symbol, "supply": int(supply)/10**18}

async def get_pair_events(address):
    

async def process_token(pair_address):
    token = await get_paired_token(pair_address["PAIR_ADDRESS"])
    pair_address.update(await get_token_data(token))

async def process_page(html):
    with open(html) as f:
        html = f.read()
    soup = BeautifulSoup(html, 'lxml')
    addresses = get_contract_addresses(soup)
    # speed this up with asyncio.gather
    for i in range(0, len(addresses), 10):
        tasks = [process_token(address) for address in addresses[i:i+10]]
        await asyncio.gather(*tasks)
        # update address with token data

        # for address, token in zip(addresses[i:i+10], tokens):
        #     address["ADDRESS"] = token
        #     address.update(await get_token_data(token))
        break
    print(addresses[:10])

asyncio.run(process_page(html))