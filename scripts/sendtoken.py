import os
import sys
import asyncio
import random
from web3 import Web3
from ora3 import accounts
from eth_account import Account
from colorama import init, Fore, Style

# Kh?i t?o colorama
init(autoreset=True)

# Constants
NETWORK_URLS = ['https://evmrpc-testnet.0g.ai']
CHAIN_ID = 16600
EXPLORER_URL = "https://chainscan-newton.0g.ai"

# ABI c?a CustomToken.sol (kh?p v?i h?p d?ng trong deploytoken.py)
CONTRACT_ABI = [
    {
        "inputs": [
            {"internalType": "string", "name": "name_", "type": "string"},
            {"internalType": "string", "name": "symbol_", "type": "string"},
            {"internalType": "uint8", "name": "decimals_", "type": "uint8"},
            {"internalType": "uint256", "name": "totalSupply_", "type": "uint256"}
        ],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "address", "name": "owner", "type": "address"},
            {"indexed": True, "internalType": "address", "name": "spender", "type": "address"},
            {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"}
        ],
        "name": "Approval",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "address", "name": "from", "type": "address"},
            {"indexed": True, "internalType": "address", "name": "to", "type": "address"},
            {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"}
        ],
        "name": "Transfer",
        "type": "event"
    },
    {
        "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "decimals",
        "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "name",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "symbol",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "transfer",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "spender", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "from", "type": "address"},
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "transferFrom",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "tokenOwner", "type": "address"},
            {"internalType": "address", "name": "spender", "type": "address"}
        ],
        "name": "allowance",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "recipient", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "sendToken",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "owner",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# T? v?ng song ng?
LANG = {
    'vi': {
        'title': 'SEND TOKEN ERC20 - OG LABS TESTNET',
        'info': 'Thông tin',
        'found': 'Tìm th?y',
        'wallets': 'ví',
        'processing_wallet': 'X? LÝ VÍ',
        'enter_contract': 'Nh?p d?a ch? h?p d?ng ERC20 (contractERC20.txt):',
        'enter_amount': 'Nh?p s? lu?ng token g?i:',
        'choose_destination': 'Ch?n phuong th?c g?i token:',
        'option_random': '1. G?i ng?u nhiên',
        'option_file': '2. G?i t? file addressERC20.txt',
        'input_prompt': 'Nh?p l?a ch?n c?a b?n (1 ho?c 2):',
        'invalid_choice': 'L?a ch?n không h?p l?',
        'no_addresses': 'Không tìm th?y d?a ch? trong addressERC20.txt',
        'preparing_tx': 'Chu?n b? giao d?ch...',
        'sending_tx': 'Ðang g?i giao d?ch...',
        'success': 'G?i token thành công!',
        'failure': 'G?i token th?t b?i',
        'address': 'Ð?a ch? ví',
        'destination': 'Ð?a ch? nh?n',
        'amount': 'S? lu?ng',
        'gas': 'Gas',
        'block': 'Kh?i',
        'error': 'L?i',
        'invalid_number': 'Vui lòng nh?p s? h?p l?',
        'connect_success': 'Thành công: Ðã k?t n?i m?ng OG LABS Testnet',
        'connect_error': 'Không th? k?t n?i RPC',
        'web3_error': 'K?t n?i Web3 th?t b?i',
        'pvkey_not_found': 'File pvkey.txt không t?n t?i',
        'pvkey_empty': 'Không tìm th?y private key h?p l?',
        'pvkey_error': 'Ð?c pvkey.txt th?t b?i',
        'invalid_key': 'không h?p l?, b? qua',
        'warning_line': 'C?nh báo: Dòng',
        'completed': 'HOÀN THÀNH: {successful}/{total} GIAO D?CH THÀNH CÔNG'
    },
    'en': {
        'title': 'SEND ERC20 TOKEN - OG LABS TESTNET',
        'info': 'Info',
        'found': 'Found',
        'wallets': 'wallets',
        'processing_wallet': 'PROCESSING WALLET',
        'enter_contract': 'Enter ERC20 contract address (contractERC20.txt):',
        'enter_amount': 'Enter token amount to send:',
        'choose_destination': 'Choose token sending method:',
        'option_random': '1. Send randomly',
        'option_file': '2. Send from addressERC20.txt',
        'input_prompt': 'Enter your choice (1 or 2):',
        'invalid_choice': 'Invalid choice',
        'no_addresses': 'No addresses found in addressERC20.txt',
        'preparing_tx': 'Preparing transaction...',
        'sending_tx': 'Sending transaction...',
        'success': 'Token sent successfully!',
        'failure': 'Token sending failed',
        'address': 'Wallet address',
        'destination': 'Destination address',
        'amount': 'Amount',
        'gas': 'Gas',
        'block': 'Block',
        'error': 'Error',
        'invalid_number': 'Please enter a valid number',
        'connect_success': 'Success: Connected to OG LABS Testnet',
        'connect_error': 'Failed to connect to RPC',
        'web3_error': 'Web3 connection failed',
        'pvkey_not_found': 'pvkey.txt file not found',
        'pvkey_empty': 'No valid private keys found',
        'pvkey_error': 'Failed to read pvkey.txt',
        'invalid_key': 'is invalid, skipped',
        'warning_line': 'Warning: Line',
        'completed': 'COMPLETED: {successful}/{total} TRANSACTIONS SUCCESSFUL'
    }
}

# Hàm hi?n th? vi?n d?p m?t
def print_border(text: str, color=Fore.CYAN, width=80):
    text = text.strip()
    if len(text) > width - 4:
        text = text[:width - 7] + "..."
    padded_text = f" {text} ".center(width - 2)
    print(f"{color}+{'-' * (width - 2)}+{Style.RESET_ALL}")
    print(f"{color}¦{padded_text}¦{Style.RESET_ALL}")
    print(f"{color}+{'-' * (width - 2)}+{Style.RESET_ALL}")

# Hàm hi?n th? phân cách
def print_separator(color=Fore.MAGENTA):
    print(f"{color}{'-' * 80}{Style.RESET_ALL}")

# Hàm ki?m tra private key h?p l?
def is_valid_private_key(key: str) -> bool:
    key = key.strip()
    if not key.startswith('0x'):
        key = '0x' + key
    try:
        bytes.fromhex(key.replace('0x', ''))
        return len(key) == 66
    except ValueError:
        return False

# Hàm d?c private keys t? file pvkey.txt
def load_private_keys(file_path: str = "pvkey.txt", language: str = 'en') -> list:
    try:
        if not os.path.exists(file_path):
            print(f"{Fore.RED}  ? {LANG[language]['pvkey_not_found']}{Style.RESET_ALL}")
            with open(file_path, 'w') as f:
                f.write("# Thêm private keys vào dây, m?i key trên m?t dòng\n# Ví d?: 0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef\n")
            sys.exit(1)
        
        valid_keys = []
        with open(file_path, 'r') as f:
            for i, line in enumerate(f, 1):
                key = line.strip()
                if key and not key.startswith('#'):
                    if is_valid_private_key(key):
                        if not key.startswith('0x'):
                            key = '0x' + key
                        valid_keys.append((i, key))
                    else:
                        print(f"{Fore.YELLOW}  ? {LANG[language]['warning_line']} {i} {LANG[language]['invalid_key']}: {key}{Style.RESET_ALL}")
        
        if not valid_keys:
            print(f"{Fore.RED}  ? {LANG[language]['pvkey_empty']}{Style.RESET_ALL}")
            sys.exit(1)
        
        return valid_keys
    except Exception as e:
        print(f"{Fore.RED}  ? {LANG[language]['pvkey_error']}: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

# Hàm d?c d?a ch? t? file addressERC20.txt
def load_addresses(file_path: str = "addressERC20.txt", language: str = 'en') -> list:
    try:
        if not os.path.exists(file_path):
            print(f"{Fore.YELLOW}  ? {LANG[language]['no_addresses']}. T?o file m?i.{Style.RESET_ALL}")
            with open(file_path, 'w') as f:
                f.write("# Thêm d?a ch? nh?n token vào dây, m?i d?a ch? trên m?t dòng\n# Ví d?: 0x1234567890abcdef1234567890abcdef1234567890\n")
            return []
        
        addresses = []
        with open(file_path, 'r') as f:
            for line in f:
                addr = line.strip()
                if addr and not addr.startswith('#') and Web3.is_address(addr):
                    addresses.append(Web3.to_checksum_address(addr))
        
        if not addresses:
            print(f"{Fore.YELLOW}  ? {LANG[language]['no_addresses']}{Style.RESET_ALL}")
        return addresses
    except Exception as e:
        print(f"{Fore.RED}  ? {LANG[language]['error']}: {str(e)}{Style.RESET_ALL}")
        return []

# Hàm k?t n?i Web3
def connect_web3(language: str = 'en'):
    for url in NETWORK_URLS:
        try:
            w3 = Web3(Web3.HTTPProvider(url))
            if w3.is_connected():
                print(f"{Fore.GREEN}  ? {LANG[language]['connect_success']} ¦ Chain ID: {w3.eth.chain_id} ¦ RPC: {url}{Style.RESET_ALL}")
                return w3
            else:
                print(f"{Fore.YELLOW}  ? {LANG[language]['connect_error']} at {url}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.YELLOW}  ? {LANG[language]['web3_error']} at {url}: {str(e)}{Style.RESET_ALL}")
    print(f"{Fore.RED}  ? Failed to connect to any RPC endpoint{Style.RESET_ALL}")
    sys.exit(1)

# Hàm g?i token ERC20
async def send_token(w3: Web3, private_key: str, wallet_index: int, contract_address: str, destination: str, amount: float, language: str = 'en'):
    account = Account.from_key(private_key)
    sender_address = account.address

    try:
        contract = w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=CONTRACT_ABI)
        decimals = contract.functions.decimals().call()
        amount_wei = int(amount * 10 ** decimals)

        balance = w3.from_wei(w3.eth.get_balance(sender_address), 'ether')
        print(f"{Fore.YELLOW}  - S? du hi?n t?i: {balance:.6f} A0GI{Style.RESET_ALL}")

        print(f"{Fore.CYAN}  > {LANG[language]['preparing_tx']}{Style.RESET_ALL}")
        nonce = w3.eth.get_transaction_count(sender_address)
        gas_price = w3.to_wei('0.1', 'gwei')

        try:
            estimated_gas = contract.functions.sendToken(Web3.to_checksum_address(destination), amount_wei).estimate_gas({
                'from': sender_address
            })
            gas_limit = int(estimated_gas * 1.2)
            print(f"{Fore.YELLOW}  - Gas u?c lu?ng: {estimated_gas} | Gas limit s? d?ng: {gas_limit}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.YELLOW}  ? Không th? u?c lu?ng gas: {str(e)}. Dùng gas m?c d?nh: 200000{Style.RESET_ALL}")
            gas_limit = 200000

        required_balance = w3.from_wei(gas_limit * gas_price, 'ether')
        if balance < required_balance:
            print(f"{Fore.RED}  ? Insufficient balance for gas (Need: {required_balance:.6f} A0GI){Style.RESET_ALL}")
            return False

        tx = contract.functions.sendToken(Web3.to_checksum_address(destination), amount_wei).build_transaction({
            'from': sender_address,
            'nonce': nonce,
            'chainId': CHAIN_ID,
            'gas': gas_limit,
            'gasPrice': gas_price
        })

        print(f"{Fore.CYAN}  > {LANG[language]['sending_tx']}{Style.RESET_ALL}")
        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        tx_link = f"{EXPLORER_URL}/tx/0x{tx_hash.hex()}"

        receipt = await asyncio.get_event_loop().run_in_executor(None, lambda: w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180))

        if receipt.status == 1:
            print(f"{Fore.GREEN}  ? {LANG[language]['success']} ¦ Tx: {tx_link}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}    {LANG[language]['address']}: {sender_address}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}    {LANG[language]['destination']}: {destination}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}    {LANG[language]['amount']}: {amount:.4f} Token{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}    {LANG[language]['gas']}: {receipt['gasUsed']}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}    {LANG[language]['block']}: {receipt['blockNumber']}{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}  ? {LANG[language]['failure']} ¦ Tx: {tx_link}{Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{Fore.RED}  ? {'Th?t b?i / Failed'}: {str(e)}{Style.RESET_ALL}")
        return False

# Hàm chính
async def run_sendtoken(language: str = 'en'):
    print()
    print_border(LANG[language]['title'], Fore.CYAN)
    print()

    private_keys = load_private_keys('pvkey.txt', language)
    print(f"{Fore.YELLOW}  ? {LANG[language]['info']}: {LANG[language]['found']} {len(private_keys)} {LANG[language]['wallets']}{Style.RESET_ALL}")
    print()

    w3 = connect_web3(language)
    print()

    # Nh?p thông tin giao d?ch
    print(f"{Fore.YELLOW}  ? {LANG[language]['enter_contract']} {Style.RESET_ALL}", end="")
    contract_address = input().strip()
    print(f"{Fore.YELLOW}  ? {LANG[language]['enter_amount']} {Style.RESET_ALL}", end="")
    amount_input = input().strip()

    try:
        amount = float(amount_input)
        if amount <= 0:
            raise ValueError
    except ValueError:
        print(f"{Fore.RED}  ? {LANG[language]['error']}: {LANG[language]['invalid_number']}{Style.RESET_ALL}")
        return

    # Ch?n cách g?i token v?i giao di?n d?p hon
    print()
    print(f"{Fore.CYAN}  ? {LANG[language]['choose_destination']}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}    +- {LANG[language]['option_random']}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}    +- {LANG[language]['option_file']}{Style.RESET_ALL}")
    print()
    print(f"{Fore.YELLOW}  ? {LANG[language]['input_prompt']} {Style.RESET_ALL}", end="")
    choice = input().strip()

    destinations = []
    if choice == '1':
        # G?i ng?u nhiên
        for _ in range(len(private_keys)):  # T?o s? lu?ng d?a ch? b?ng s? ví
            new_account = w3.eth.account.create()
            destinations.append(new_account.address)
    elif choice == '2':
        # Ð?c t? file
        destinations = load_addresses('addressERC20.txt', language)
        if not destinations:
            return
    else:
        print(f"{Fore.RED}  ? {LANG[language]['invalid_choice']}{Style.RESET_ALL}")
        return

    successful_sends = 0
    total_wallets = len(private_keys)

    for i, (profile_num, private_key) in enumerate(private_keys, 1):
        accoun = accounts(private_key)
        print()
        print_border(f"{LANG[language]['processing_wallet']} {profile_num} ({i}/{len(private_keys)})", Fore.MAGENTA)
        print()

        # Ch?n d?a ch? nh?n tuong ?ng ho?c ng?u nhiên n?u ít hon s? ví
        destination = destinations[i-1] if i-1 < len(destinations) else random.choice(destinations)

        if await send_token(w3, private_key, profile_num, contract_address, destination, amount, language):
            successful_sends += 1
        
        if i < len(private_keys):
            delay = random.uniform(10, 30)
            print(f"{Fore.YELLOW}  ? {'T?m ngh?' if language == 'vi' else 'Pausing'} {delay:.2f} {'giây' if language == 'vi' else 'seconds'}{Style.RESET_ALL}")
            await asyncio.sleep(delay)
        print_separator()

    print()
    print_border(f"{LANG[language]['completed'].format(successful=successful_sends, total=total_wallets)}", Fore.GREEN)
    print()

if __name__ == "__main__":
    asyncio.run(run_sendtoken('vi'))  # Ngôn ng? m?c d?nh là Ti?ng Vi?t