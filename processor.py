import asyncio
import aiohttp
from bs4 import BeautifulSoup
import lxml
import os
from web3 import Web3

PROVIDER_LINK = os.getenv("PROVIDER_LINK")

html = "./files/DEX Screener.html"

provider = Web3.AsyncHTTPProvider(PROVIDER_LINK)

def get_contract_addresses(soup:BeautifulSoup):
    rows = soup.find_all('a', class_='ds-dex-table-row ds-dex-table-row-new')
    return [row['href'].split("/")[-1] for row in rows]

async def get_paired_tokens(address):
    pass

def process_page(html):
    with open(html) as f:
        html = f.read()
    soup = BeautifulSoup(html, 'lxml')
    print(get_contract_addresses(soup))

process_page(html)