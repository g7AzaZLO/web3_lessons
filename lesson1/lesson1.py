from web3 import Web3

RPC = "https://eth.llamarpc.com"
web3 = Web3(Web3.HTTPProvider(RPC))

# Проверка подключения
if web3.is_connected():
    print("Успешно подключились к блокчейну Ethereum!")
else:
    print("Не удалось подключиться к блокчейну.")

chain_id = web3.eth.chain_id
print("ID цепочки:", chain_id)

# Получение номера последнего блока
latest_block = web3.eth.block_number
print("Номер последнего блока:", latest_block)

# Получение данных последнего блока
block_data = web3.eth.get_block(latest_block)
print("Данные последнего блока:", block_data)

# Получение и вывод хешей транзакций из последнего блока
transactions = block_data['transactions']
print("Хеши транзакций в последнем блоке:")
for tx in transactions:
    print(tx)

# Получение баланса аккаунта
account_address = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"

checksum_address = web3.to_checksum_address(account_address)
print(f"Checksum адрес аккаунта: {checksum_address}")

print(web3.eth.get_balance(checksum_address))

wei = 1
gwei = web3.from_wei(wei, 'gwei')
ether = web3.from_wei(wei, 'ether')

print(str(wei) + " " + '{:f}'.format(gwei) + " " + '{:f}'.format(ether))

balance_wei = web3.eth.get_balance(account_address)
balance_eth = web3.from_wei(balance_wei, 'ether')
print(f"Баланс аккаунта {account_address}: {balance_eth} ETH")

# Получение текущей цены газа
gas_price_wei = web3.eth.gas_price
gas_price_gwei = web3.fromWei(gas_price_wei, 'gwei')
print(f"Текущая цена газа: {gas_price_gwei} Gwei")


tx_hash = "0xe213f634db80ef1230faa0b15c1fdcfe6d2d8b834e59574de03ec272f4d3b8f2"
transaction = web3.eth.get_transaction(tx_hash)

print(transaction)

print("Отправитель:", transaction['from'])
print("Получатель:", transaction['to'])
print("Сумма:", web3.from_wei(transaction['value'], 'ether'))
print("Цена газа:", web3.from_wei(transaction['gasPrice'], 'gwei'))
print("Хеш транзакции:", transaction['hash'])
