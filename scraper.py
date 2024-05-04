import aiohttp
import asyncio
import lxml
from selenium import webdriver
from bs4 import BeautifulSoup

URL = "https://dexscreener.com/?rankBy=pairAge&order=asc&chainIds=base&maxAge=1"

# async def fetch():
#     async with aiohttp.ClientSession() as session:
#         async with session.get(URL, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}) as response:
#             text = await response.text()
    
#     return BeautifulSoup(text, 'lxml')

# async def main():
#     soup = await fetch()
#     print(soup.prettify())

# if __name__ == "__main__":
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(main())

# dr = webdriver.Chrome()
# dr.get(URL)
# bs = BeautifulSoup(dr.page_source,"lxml")
# print(bs.prettify())

from seleniumbase import Driver

driver = Driver(uc=True)
driver.uc_open_with_reconnect(URL, 4)
# driver.sleep(3)
# # get all a tags with class ds-dex-table-row ds-dex-table-row-new
# soup = BeautifulSoup(driver.get_page_source(), 'lxml')
# rows = soup.find_all('a', class_='ds-dex-table-row ds-dex-table-row-new')
# row = rows[0]
# # get href from a tag with class="ds-dex-table-row ds-dex-table-row-new"
# href = row['href']
# print(href)
while True:
    driver.sleep(3)
    soup = BeautifulSoup(driver.get_page_source(), 'lxml')
    rows = soup.find_all('a', class_='ds-dex-table-row ds-dex-table-row-new')
    for row in rows:
        href = row['href']
        print(href)
    print("REFRESH")
    driver.refresh()
