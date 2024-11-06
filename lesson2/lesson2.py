from eth_account import Account
from web3 import Web3
import json


def generate_account(nums: int):
    accounts = []
    for i in range(nums):
        Account.enable_unaudited_hdwallet_features()
        account, mnemonic = Account.create_with_mnemonic()
        accounts.append([account.address, mnemonic, "0x" + account.key.hex()])
    return accounts


pub_key = "0x65BA4CCCaeBF4e79862771808B04666A94De8DB5"
priv_key = "0xfc7d5bea5520a720a9aa2abc455790f01457556a6c35eb819417a9944c01f39f"
ERC20_ABI = json.load(open('ERC20ABI.json'))
contract_addres_rivalz = "0xF0a66d18b46D4D5dd9947914ab3B2DDbdC19C2C0"

# RPC = "https://polygon.llamarpc.com"
RPC = "https://rivalz2.rpc.caldera.xyz/http"
web3 = Web3(Web3.HTTPProvider(RPC))

if web3.is_connected():
    print("Connected")
else:
    print("Not connected")


def get_balance(address: str) -> float:
    balance_wei = web3.eth.get_balance(address)
    balance_eth = web3.from_wei(balance_wei, 'ether')
    return balance_eth


print(get_balance(pub_key))


def get_nonce(address: str) -> int:
    nonce = web3.eth.get_transaction_count(address)
    return nonce

def send_native(to_address: str, amount: float) -> str | None:
    print(f"Sending {amount} POL to {to_address}")
    value = web3.to_wei(amount, 'ether')
    nonce = get_nonce(pub_key)
    tx = {
        'to': to_address,
        'value': value,
        'gasPrice': web3.eth.gas_price,
        'nonce': nonce,
        'chainId': 137
    }
    tx['gas'] = web3.eth.estimate_gas(tx)
    singed_transaction = web3.eth.account.sign_transaction(tx, private_key=priv_key)
    tx_hash = web3.eth.send_raw_transaction(singed_transaction.raw_transaction)
    return "0x"+tx_hash.hex()

def get_balance_erc20(contract_address: str, address: str) -> float:
    contract = web3.eth.contract(address=contract_address, abi=ERC20_ABI)
    balance_wei = contract.functions.balanceOf(address).call()
    decimals = contract.functions.decimals().call()
    balance_ether = balance_wei / (10 ** decimals)
    return balance_ether

#print(get_balance_erc20("0x3C69d114664d48357d820Dbdd121a8071eAc99bf", pub_key))

def send_erc20_tokens(contract_address: str, to_address: str, amount: float) -> str | None:
    contract = web3.eth.contract(address=contract_address, abi=ERC20_ABI)
    decimals = contract.functions.decimals().call()
    amount_in_wei = amount * (10 ** decimals)
    nonce = get_nonce(pub_key)
    tx = contract.functions.transfer(to_address,amount_in_wei).build_transaction({
        'from': pub_key,
        'gasPrice': web3.eth.gas_price,
        'nonce': nonce,
        'chainId': 137
    })
    tx['gas'] = web3.eth.estimate_gas(tx)
    singed_transaction = web3.eth.account.sign_transaction(tx, private_key=priv_key)
    tx_hash = web3.eth.send_raw_transaction(singed_transaction.raw_transaction)
    return "0x"+tx_hash.hex()

#print(send_erc20_tokens("0x3C69d114664d48357d820Dbdd121a8071eAc99bf", "0xb69d7F30Ba4CDBcbd6656b4fe3E079e0954D59B3", 1))

METHOD = "0x4e71d92d"

def claim_rivalz():
    nonce = get_nonce(pub_key)
    tx = {
        "to": contract_addres_rivalz,
        "value": 0,
        "nonce": nonce,
        "data": METHOD,
        "chainId": 6966,
        "gasPrice": web3.eth.gas_price,
        "gas": 300000
    }
    singed_transaction = web3.eth.account.sign_transaction(tx, private_key=priv_key)
    tx_hash = web3.eth.send_raw_transaction(singed_transaction.raw_transaction)
    return "0x"+tx_hash.hex()

print(claim_rivalz())
print(claim_rivalz())
print(claim_rivalz())
print(claim_rivalz())
