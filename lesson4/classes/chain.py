from web3 import Web3

from lesson4.abis.abis import ERC20_ABI


class Chain:
    def __init__(self, name: str, chain_id: int, rpc: str, native_token: str, alternative_rpc: list[str]):
        self.name = name
        self.id = chain_id
        self.rpc = rpc
        self.native_token = native_token
        self.alternative_rpc = alternative_rpc  # Массив альтернативных RPC-серверов, если первый недоступен
        self.current_rpc_index = 0

    def set_rpc_url(self, url: str) -> bool:
        self.rpc = url
        return True

    def switch_to_alternative_rpc(self) -> bool:
        if self.current_rpc_index < len(self.alternative_rpc):
            self.rpc = self.alternative_rpc[self.current_rpc_index]
            self.current_rpc_index += 1
            return True
        else:
            print("No more alternative RPCs available for this chain")
            return False

    def get_decimals(self, token_address: str) -> int:
        connection = Web3(Web3.HTTPProvider(self.rpc))
        contract = connection.eth.contract(address=Web3.to_checksum_address(token_address), abi=ERC20_ABI)
        decimals = contract.functions.decimals().call()
        return decimals

chains = {
    "ethereum": Chain(
        "ethereum",
        1,
        "https://ethereum-rpc.publicnode.com",
        "ETH",
        ["https://eth.llamarpc.com", "https://rpc.payload.de", "https://1rpc.io/eth"]),
    "arbitrum": Chain(
        'arbitrum',
        42161,
        "https://arbitrum.llamarpc.com",
        "ETH",
        ["https://arbitrum.drpc.org", "https://1rpc.io/arb", "https://arb-pokt.nodies.app",
         "https://arbitrum.meowrpc.com"]),
    "optimism": Chain(
        'optimism',
        10,
        "https://optimism-rpc.publicnode.com",
        "ETH",
        ["https://1rpc.io/op", "https://optimism.llamarpc.com", "https://optimism.drpc.org"]),
}
