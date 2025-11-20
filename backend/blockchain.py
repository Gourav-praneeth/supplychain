from web3 import Web3
from config import settings
import json
import os
from typing import List, Dict, Any
from datetime import datetime

# Load ABI from the contract_abi.json file
current_dir = os.path.dirname(os.path.abspath(__file__))
abi_path = os.path.join(current_dir, 'contract_abi.json')

with open(abi_path, 'r') as f:
    FOODSAFE_ABI = json.load(f)

# Status enum mapping
STATUS_MAP = {
    0: "Created",
    1: "InTransit",
    2: "OnShelf",
    3: "Recalled"
}


class BlockchainService:
    """
    Service for interacting with the FoodSafe smart contract on Polygon Amoy.
    """

    def __init__(self):
        """
        Initialize Web3 provider and contract instance.
        """
        self.w3 = Web3(Web3.HTTPProvider(settings.POLYGON_AMOY_RPC_URL))
        self.contract_address = settings.CONTRACT_ADDRESS
        self.contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.contract_address),
            abi=FOODSAFE_ABI
        )

    def is_connected(self) -> bool:
        """
        Check if connected to blockchain network.
        """
        return self.w3.is_connected()

    def get_lot_status(self, token_id: int) -> str:
        """
        Get the current status of a lot from the smart contract.
        Returns: Status string (Created, InTransit, OnShelf, Recalled)
        """
        try:
            lot = self.contract.functions.getLot(token_id).call()
            # lot[4] is the status field in the FoodLot struct
            status_value = lot[4]
            return STATUS_MAP.get(status_value, "Unknown")
        except Exception as e:
            print(f"Error getting lot status: {e}")
            raise

    def get_lot_owner(self, token_id: int) -> str:
        """
        Get the current owner address of a lot (NFT).
        Returns: Owner's Ethereum address
        """
        try:
            owner = self.contract.functions.ownerOf(token_id).call()
            return owner
        except Exception as e:
            print(f"Error getting lot owner: {e}")
            raise

    def get_lot_history(self, token_id: int) -> List[Dict[str, Any]]:
        """
        Get the full history array for a lot from the smart contract.
        Returns: List of history entries with timestamp, ipfsHash, and status
        """
        try:
            history = self.contract.functions.getLotHistory(token_id).call()
            parsed_history = []
            for entry in history:
                parsed_entry = {
                    "timestamp": datetime.fromtimestamp(entry[0]),
                    "ipfsHash": entry[1],
                    "status": STATUS_MAP.get(entry[2], "Unknown")
                }
                parsed_history.append(parsed_entry)
            return parsed_history
        except Exception as e:
            print(f"Error getting lot history: {e}")
            raise

    def get_lot_details(self, token_id: int) -> Dict[str, Any]:
        """
        Get complete lot details including metadata.
        Returns: Dictionary with lot information
        """
        try:
            lot = self.contract.functions.getLot(token_id).call()
            return {
                "lotId": lot[0],
                "productName": lot[1],
                "origin": lot[2],
                "currentOwner": lot[3],
                "status": STATUS_MAP.get(lot[4], "Unknown"),
                "history": self._parse_history(lot[5])
            }
        except Exception as e:
            print(f"Error getting lot details: {e}")
            raise

    def _parse_history(self, history_data: list) -> List[Dict[str, Any]]:
        """Helper method to parse history data from contract."""
        parsed_history = []
        for entry in history_data:
            parsed_entry = {
                "timestamp": datetime.fromtimestamp(entry[0]),
                "ipfsHash": entry[1],
                "status": STATUS_MAP.get(entry[2], "Unknown")
            }
            parsed_history.append(parsed_entry)
        return parsed_history

    def is_recalled(self, token_id: int) -> bool:
        """
        Check if a lot is currently recalled.
        Returns: True if recalled, False otherwise
        """
        try:
            status = self.get_lot_status(token_id)
            return status == "Recalled"
        except Exception as e:
            print(f"Error checking recall status: {e}")
            return False

    def get_event_logs(self, event_name: str, from_block: int, to_block: int | str = 'latest') -> List[Dict[str, Any]]:
        """
        Fetch event logs from the blockchain.
        Args:
            event_name: Name of the event (e.g., 'Transfer', 'LotRecalled')
            from_block: Starting block number
            to_block: Ending block number or 'latest'
        Returns: List of event log dictionaries
        """
        try:
            event = getattr(self.contract.events, event_name)
            event_filter = event.create_filter(
                fromBlock=from_block,
                toBlock=to_block
            )
            logs = event_filter.get_all_entries()
            
            parsed_logs = []
            for log in logs:
                parsed_log = {
                    'event': event_name,
                    'args': dict(log['args']),
                    'blockNumber': log['blockNumber'],
                    'transactionHash': log['transactionHash'].hex(),
                    'logIndex': log['logIndex']
                }
                parsed_logs.append(parsed_log)
            
            return parsed_logs
        except AttributeError:
            print(f"Event {event_name} not found in contract")
            return []
        except Exception as e:
            print(f"Error getting event logs: {e}")
            return []

    def get_latest_block_number(self) -> int:
        """
        Get the latest block number on the chain.
        """
        return self.w3.eth.block_number

    def get_block_timestamp(self, block_number: int) -> datetime:
        """
        Get the timestamp of a specific block.
        """
        try:
            block = self.w3.eth.get_block(block_number)
            return datetime.fromtimestamp(block['timestamp'])
        except Exception as e:
            print(f"Error getting block timestamp: {e}")
            return datetime.utcnow()


blockchain_service = BlockchainService()
