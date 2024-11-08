import time
from web3 import Web3
from lesson4.abis.abis import ERC20_ABI


class Client:
    def __init__(self, private_key: str, rpc: str):
        """"
        :param private_key: Приватный ключ в 16 ричном формате
        :param rpc: URL RPC-сервера
        :raises ConnectionError: Если не удалось подключиться к RPC-серверу
        """
        self.private_key = private_key
        self.rpc = rpc
        self.connection = Web3(Web3.HTTPProvider(rpc))
        if not self.connection.is_connected():
            raise ConnectionError("Failed to connect to the RPC")
        self.account = self.connection.eth.account.from_key(self.private_key)
        self.public_key = self.account.address
        self.chain_id = self.connection.eth.chain_id

    def __del__(self) -> None:
        """
        Сообщает, что клиент был удален.
        """
        print(f"Client with public key {self.public_key} was deleted")

    def __str__(self) -> str:
        """
        Возвращает строковое представление клиента.
        """
        return (
            f"Client(\n"
            f" public_key={self.public_key},\n"
            f" private_key={self.private_key}\n"
            f" rpc = {self.rpc}\n"
            f" chain_id = {self.chain_id}\n"
            f")"
        )

    def get_nonce(self, address: str = None) -> int | None:
        """
        Получает nonce аккаунта

        :param address: адрес для проверки nonce. Если не указан, берется аккаунт текущего клиента
        :return: nonce аккаунта
        """
        if address is None:
            address = self.public_key
        try:
            return self.connection.eth.get_transaction_count(Web3.to_checksum_address(address))
        except Exception as e:
            print(f"Error occurred while getting nonce for address {address}: {e}")
            return None

    def get_native_balance(self, address: str = None) -> float | None:
        """
        Получает баланс аккаунта в нативной монете

        :param address: адрес для проверки баланса. Если не указан, берется аккаунт текущего клиента
        :return: Баланс аккаунта в единице измерения ether
        """
        if address is None:
            address = self.public_key
        try:
            balance_wei = self.connection.eth.get_balance(Web3.to_checksum_address(address))
            balance_eth = self.connection.from_wei(balance_wei, 'ether')
            return balance_eth
        except Exception as e:
            print(f"Error occurred while getting native balance for address {address}: {e}")
            return None

    def send_transaction(self, transaction: dict) -> str | None:
        """
        Подписывает и отправляет транзакцию в сеть, возвращая её хеш.

        :param transaction: Словарь с данными транзакции.
        :return: Хеш отправленной транзакции или ничего
        """
        try:
            signed_transaction = self.account.sign_transaction(transaction)
            tx_hash = self.connection.eth.send_raw_transaction(signed_transaction.raw_transaction)
            return "0x" + tx_hash.hex()
        except Exception as e:
            print(f"Error occurred while sending transaction: {e}")
            return None

    def send_native(self, to_address: str, amount: float) -> str | None:
        """
        Отправляет нативные средства на кошелек ""to_address" в количестве "amount"

        :param to_address: Адрес получателя
        :param amount: Количество отправляемых нативных средств
        :return: Хеш транзакции или ничего
        """
        try:
            value = self.connection.to_wei(amount, 'ether')
            nonce = self.get_nonce()
            tx = {
                'nonce': nonce,
                'to': Web3.to_checksum_address(to_address),
                'value': value,
                'chainId': self.chain_id,
                'gasPrice': self.connection.eth.gas_price,
            }
            tx['gas'] = self.connection.eth.estimate_gas(tx)
            return self.send_transaction(tx)
        except Exception as e:
            print(f"Error occurred while preparing transaction: {e}")

    def get_erc20_balance(self, erc20_address: str, account_address: str = None) -> float | None:
        """
        Получает баланс ERC20-токена для указанного аккаунта

        :param erc20_address: Адрес ERC20-токена
        :param account_address: Адрес для проверки баланса. Если не указан, берется аккаунт текущего клиента
        :return: Баланс ERC20-токена для указанного аккаунта
        """
        if account_address is None:
            account_address = self.public_key
        contract = self.connection.eth.contract(address=Web3.to_checksum_address(erc20_address), abi=ERC20_ABI)
        balance_wei = contract.functions.balanceOf(account_address).call()
        decimals = contract.functions.decimals().call()
        balance_ether = balance_wei / (10 ** decimals)
        return balance_ether

    def send_erc20_tokens(self, erc20_address: str, to_address: str, amount: float) -> str | None:
        """
        Отправляет ERC20-токены на указанный адрес

        :param erc20_address: Адрес ERC20-токена
        :param to_address: Адрес получателя
        :param amount: Количество отправляемых ERC20-токенов
        :return: Хеш транзакции или ничего
        """
        try:
            contract = self.connection.eth.contract(address=Web3.to_checksum_address(erc20_address), abi=ERC20_ABI)
            decimals = contract.functions.decimals().call()
            scaled_amount = int(amount * (10 ** decimals))
            nonce = self.get_nonce()
            estimate_gas = contract.functions.transfer(
                Web3.to_checksum_address(to_address), scaled_amount).estimate_gas({'from': self.public_key})
            gas_price = self.connection.eth.gas_price
            transaction = contract.functions.transfer(
                Web3.to_checksum_address(to_address),  scaled_amount).build_transaction(
                {
                    'from': self.public_key,
                    'gas': estimate_gas,
                    'gasPrice': gas_price,
                    'nonce': nonce,
                    'chainId': self.chain_id,
                }
            )
            tx_hash = self.send_transaction(transaction)
            return tx_hash
        except Exception as e:
            print(f"Error occurred while sending ERC20 tokens: {e}")
            return None

    def approve(self, token_address: str, spender_address: str, amount: float) -> str | None:
        """
        Применить approve для ERC20-токена

        :param token_address: Адрес ERC20-токена
        :param spender_address: Адрес смарт контракта которому можно тратить токены
        :param amount: Количество ERC20-токенов которые можно списать
        :return: Хеш транзакции или ничего
        """
        try:
            contract = self.connection.eth.contract(address=Web3.to_checksum_address(token_address), abi=ERC20_ABI)
            decimals = contract.functions.decimals().call()
            scaled_amount = int(amount * (10 ** decimals))
            nonce = self.get_nonce()
            estimate_gas = contract.functions.transfer(
                Web3.to_checksum_address(spender_address), scaled_amount).estimate_gas({'from': self.public_key})
            gas_price = self.connection.eth.gas_price
            transaction = contract.functions.approve(
                Web3.to_checksum_address(spender_address), scaled_amount).build_transaction(
                {
                    'from': self.public_key,
                    'nonce': nonce,
                    'gas': estimate_gas,
                    'gasPrice': gas_price,
                    'chainId': self.chain_id,
                })
            tx_hash = self.send_transaction(transaction)
            return tx_hash
        except Exception as e:
            print(f"Error occurred while approving ERC20 tokens: {e}")
            return None

    def permit_approve(self, token_address: str, spender_address: str):
        """
        Применить permit approve для ERC20-токена

        :param token_address: Адрес ERC20-токена
        :param spender_address: Адрес смарт контракта которому можно тратить токены
        :return: Хеш транзакции или ничего
        """
        try:
            contract = self.connection.eth.contract(address=token_address, abi=ERC20_ABI)
            scaled_amount = 2 ** 256 - 1
            nonce = self.get_nonce()
            estimate_gas = contract.functions.transfer(
                Web3.to_checksum_address(spender_address), scaled_amount).estimate_gas({'from': self.public_key})
            gas_price = self.connection.eth.gas_price
            transaction = contract.functions.approve(
                Web3.to_checksum_address(spender_address), scaled_amount).build_transaction(
                {
                    'from': self.public_key,
                    'nonce': nonce,
                    'gas': estimate_gas,
                    'gasPrice': gas_price,
                    'chainId': self.chain_id,
                })
            tx_hash = self.send_transaction(transaction)
            return tx_hash
        except Exception as e:
            print(f"Error occurred while approving ERC20 tokens: {e}")
            return None

    def get_allowance(self, token_address: str, spender_address: str) -> float | None:
        """
        Получить лимит approve ERC20-токена для определенного контракта

        :param token_address: Адрес ERC20-токена
        :param spender_address: Адрес смарт контракта которому можно тратить токены
        :return: Остаток approve или None
        """
        try:
            contract = self.connection.eth.contract(address=Web3.to_checksum_address(token_address), abi=ERC20_ABI)
            allowance = contract.functions.allowance(self.public_key, Web3.to_checksum_address(spender_address)).call()
            decimals = contract.functions.decimals().call()
            return allowance / (10 ** decimals)
        except Exception as e:
            print(f"Error occurred while getting allowance: {e}")
            return None
