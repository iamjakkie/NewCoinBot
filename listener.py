import os
from web3 import Web3

from utils.abis import FACTORY

wss_url = os.getenv("WSS_URL")
web3 = Web3(Web3.WebsocketProvider(wss_url))


# Uniswap V2 Factory address
factory_address = '0x8909Dc15e40173Ff4699343b6eB8132c65e18eC6'

# Instantiate the factory contract
factory_contract = web3.eth.contract(address=factory_address, abi=FACTORY)

# Event listener function
def handle_event(event):
    print(f"New pair created: {event['args']['pair']}")

# Main event loop
from web3.middleware import geth_poa_middleware
web3.middleware_onion.inject(geth_poa_middleware, layer=0)

event_filter = factory_contract.events.PairCreated.create_filter(fromBlock='latest')
while True:
    for event in event_filter.get_new_entries():
        handle_event(event)
