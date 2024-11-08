import time
import requests
from web3 import Web3
from lesson4.classes.chain import Chain, chains
from lesson4.classes.client import Client
from lesson4.modules.crosscurve.config import ROUTER, USDT_ARB, USDT_OP
from lesson4.abis.abis import CROSSCURVE_ABI


def get_route(chain_in: Chain, token_address_in: str, chain_out: Chain, token_address_out: str, amount_in: float,
              slippage: float) -> dict | None:
    """
    Получение пути свапа по api

    :param chain_in: Чейн из которого будем свапать
    :param token_address_in:  Токен который будем свапать
    :param chain_out: Чейн в который будем свапать
    :param token_address_out: Токен в который будем свапать
    :param amount_in: Количество токенов для свапа
    :param slippage: Проскальзывание в процентах
    :return: Словарь с путем свапа или None если путь не найден
    """
    try:
        decimals_in = chain_in.get_decimals(token_address_in)
        amount_in_scaled = str(int(amount_in * (10 ** decimals_in)))

        url = "https://api.crosscurve.fi/routing/scan"
        params = {
            "params": {
                "chainIdOut": chain_out.id,
                "tokenOut": token_address_out,
                "chainIdIn": chain_in.id,
                "amountIn": amount_in_scaled,
                "tokenIn": token_address_in
            },
            "slippage": slippage
        }

        response = requests.post(url, json=params)
        if response.status_code == 200:
            data = response.json()
            return data[0]
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error occurred while getting swap route: {e}")
        return None


def get_estimate(route: dict) -> dict | None:
    """
    Получение оценки свапа по полученному пути

    :param route: Полученный путь свапа
    :return: Словарь с оценкой свапа или None если оценка не найдена
    """
    try:
        url = 'https://api.crosscurve.fi/estimate'
        headers = {
            "Content-Type": "application/json",
        }
        response = requests.post(url, headers=headers, json=route)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error occurred while estimating swap: {e}")
        return None


def create_swap_transaction(address: str, route: dict, estimate: dict) -> dict | None:
    """
    Создание транзакции свапа

    :param address: Адрес отправителя, получателя
    :param route: Полученный путь свапа
    :param estimate: Оценка свапа
    :return: Словарь с транзакцией свапа или None если транзакция не создана
    """
    try:
        url = 'https://api.crosscurve.fi/tx/create'
        headers = {
            "Content-Type": "application/json",
        }
        tx_create_params = {
            'from': address,
            'recipient': address,
            'routing': route,
            'estimate': estimate,
        }
        response = requests.post(url, headers=headers, json=tx_create_params)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error occurred while creating swap transaction: {e}")
        return None


def send_swap_transaction(client: Client, raw_tx: dict, estimate: dict) -> str | None:
    """
    Отправка созданной транзакции свапа

    :param client: Объект класса Клиент
    :param raw_tx: Транзакция
    :param estimate: Оценка свапа
    :return: Хеш транзакции или None если транзакция не отправлена
    """
    router = client.connection.eth.contract(address=Web3.to_checksum_address(raw_tx["to"]), abi=CROSSCURVE_ABI)
    args = [
        list(raw_tx['args'][0]),
        list(raw_tx['args'][1]),
        [
            int(raw_tx['args'][2]['executionPrice']),
            int(raw_tx['args'][2]['deadline']),
            int(raw_tx['args'][2]['v']),
            Web3.to_bytes(hexstr=raw_tx['args'][2]['r']),
            Web3.to_bytes(hexstr=raw_tx['args'][2]['s'])
        ]
    ]
    value = int(raw_tx['value']) + int(estimate['executionPrice'])
    transaction = router.functions.start(*args).build_transaction({
        'from': client.public_key,
        'value': value,
        'gas': client.connection.eth.estimate_gas({
            'to': Web3.to_checksum_address(ROUTER),
            'from': client.public_key,
            'data': router.encode_abi("start", args=args),
            'value': value
        }),
        'gasPrice': client.connection.eth.gas_price,
        'nonce': client.get_nonce()
    })
    hash = client.send_transaction(transaction)
    return hash


client = Client("0xb0e4ad648105cae70ee29ff21c2ffc7e457a12afd8949ad8e188f8e404687905", chains["arbitrum"].rpc)
route = get_route(chains["arbitrum"], USDT_ARB, chains["optimism"], USDT_OP, 5, 0.1)
print(route)
print("--------------")
estimate = get_estimate(route)
print(estimate)
print("--------------")
transaction = create_swap_transaction(client.public_key, route, estimate)
print(transaction)
print("--------------")
print(client.get_allowance(USDT_ARB, ROUTER))
time.sleep(10)
send_hash = send_swap_transaction(client, transaction, estimate)
print(send_hash)
