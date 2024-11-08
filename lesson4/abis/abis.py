import os

current_dir = os.path.dirname(__file__)
file_path_erc20_abi = os.path.join(current_dir, "ERC20ABI.json")
file_path_crosscurve_abi = os.path.join(current_dir, "CROSSCURVEABI.json")

# Открываем файл
with open(file_path_erc20_abi, "r") as file:
    ERC20_ABI = file.read()

with open(file_path_crosscurve_abi, "r") as file:
    CROSSCURVE_ABI = file.read()
