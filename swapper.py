import asyncio
import os
import time
from web3 import AsyncHTTPProvider, AsyncWeb3
from utils.abis import ROUTER

base_rpc_url = 'https://base-mainnet.s.chainbase.online/v1/2gTQyCsSw3rwko0lY6J9Mmd2Is2'
web3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(base_rpc_url))

# Uniswap V2 Router address and ABI
router_address = web3.to_checksum_address('0x4752ba5DBc23f44D87826276BF6Fd6b1C372aD24')

# Instantiate the router contract
router_contract = web3.eth.contract(address=router_address, abi=ROUTER)

# Account details
private_key = os.getenv('PRIVATE_KEY')
account_address = web3.eth.account.from_key(private_key).address
print(account_address)

#0x4752ba5DBc23f44D87826276BF6Fd6b1C372aD24
async def get_token_price():
    
    # Check connection
    assert web3.is_connected(), "Failed to connect to the Base network"

    # Get the current gas price
    current_gas_price = await web3.eth.gas_price
    print(f"Current gas price: {web3.from_wei(current_gas_price, 'gwei')} gwei")



async def swap_weth_for_token(token_out, amount_in_weth, slippage_tolerance, max_fee_per_gas_gwei=None, max_priority_fee_per_gas_gwei=None):
    # check if eth balance is enough
    # get token price
    # calculate min amount of token to receive (1-slippage) * token price


    # max_fee_per_gas = web3.to_wei(max_fee_per_gas_gwei, 'gwei')
    # max_priority_fee_per_gas = web3.to_wei(max_priority_fee_per_gas_gwei, 'gwei')

    # build transaction
    path = [web3.to_checksum_address('0x4200000000000000000000000000000000000006'), token_out]
    amounts_out = await router_contract.functions.getAmountsOut(amount_in_weth, path).call() 
    amount_out_min = amounts_out[-1] * (1 - slippage_tolerance)
    print(f"Calculated min amount of token to receive: {amount_out_min}")

    deadline = int(time.time()) + 5 # 5 seconds

    # build transaction
    tx = await router_contract.functions.swapExactTokensForTokens(
        amount_in_weth,
        amount_out_min,
        path,
        account_address,
        deadline
    ).buildTransaction({
        'chainId': 8453,
        # 'maxFeePerGas': max_fee_per_gas,
        # 'maxPriorityFeePerGas': max_priority_fee_per_gas,
        'nonce': await web3.eth.get_transaction_count(account_address)
    })

    estimated_gas_limit = await web3.eth.estimate_gas(tx)
    tx['gas'] = estimated_gas_limit
    print(f"Estimated gas limit: {estimated_gas_limit}")

    # sign transaction
    signed_tx = await web3.eth.account.sign_transaction(tx, private_key)

    # send transaction
    tx_hash = await web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(f"Transaction sent: {tx_hash.hex()}")

    # wait for transaction to be mined
    receipt = None
    while receipt is None:
        receipt = await web3.eth.get_transaction_receipt(tx_hash)
        await asyncio.sleep(1)

    print(f"Transaction mined in block: {receipt['blockNumber']}")


async def main():
    token = web3.to_checksum_address('0xA085ADe01f960dca1b1121cE5f7dC8867af19a8E')
    amount_weth = web3.to_wei(0.001, 'ether')
    slippage = 0.05

    await swap_weth_for_token(token, amount_weth, slippage)

asyncio.run(main())