import asyncio
from web3 import AsyncHTTPProvider, AsyncWeb3

#0x4752ba5DBc23f44D87826276BF6Fd6b1C372aD24
async def get_token_price():
    base_rpc_url = 'https://base-mainnet.s.chainbase.online/v1/2gTQyCsSw3rwko0lY6J9Mmd2Is2'
    web3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(base_rpc_url))

    # Check connection
    assert web3.is_connected(), "Failed to connect to the Base network"

    # Get the current gas price
    current_gas_price = await web3.eth.gas_price
    print(f"Current gas price: {web3.from_wei(current_gas_price, 'gwei')} gwei")


async def swap_eth_for_token():
    # check if eth balance is enough
    # get token price
    # calculate min amount of token to receive (1-slippage) * token price
    ...

asyncio.run(get_token_price())