import requests
import json
from config import settings
from typing import Dict, Any


class IPFSService:
    """
    Service for uploading and retrieving data from IPFS via Pinata.
    """

    def __init__(self):
        """
        PSEUDOCODE:
        1. Store Pinata API credentials from settings
        2. Set up base URL for Pinata API
        3. Initialize headers for authentication
        """
        self.api_key = settings.PINATA_API_KEY
        self.secret_key = settings.PINATA_SECRET_API_KEY
        self.base_url = settings.PINATA_BASE_URL
        self.headers = {
            "pinata_api_key": self.api_key,
            "pinata_secret_api_key": self.secret_key
        }

    def upload_json(self, data: Dict[str, Any], filename: str = "metadata.json") -> str:
        """
        Upload JSON data to IPFS via Pinata.

        PSEUDOCODE:
        1. Convert data dictionary to JSON string
        2. Prepare request payload with pinataOptions and pinataMetadata
        3. POST to Pinata pinJSONToIPFS endpoint
        4. Extract IPFS hash (CID) from response
        5. Return the IPFS hash (e.g., "QmXxx...")
        6. Handle errors (network, authentication, rate limits)

        Returns:
            str: IPFS hash (CID) of the uploaded content
        """
        pass

    def upload_file(self, file_path: str, filename: str = None) -> str:
        """
        Upload a file to IPFS via Pinata.

        PSEUDOCODE:
        1. Open file in binary mode
        2. Prepare multipart form data
        3. POST to Pinata pinFileToIPFS endpoint
        4. Extract IPFS hash from response
        5. Return the IPFS hash
        6. Handle file not found or upload errors
        """
        pass

    def get_content(self, ipfs_hash: str) -> Dict[str, Any]:
        """
        Retrieve JSON content from IPFS using Pinata gateway.

        PSEUDOCODE:
        1. Construct IPFS gateway URL (e.g., https://gateway.pinata.cloud/ipfs/{hash})
        2. Make GET request to gateway
        3. Parse JSON response
        4. Return parsed data
        5. Handle errors (404, invalid JSON, network issues)
        """
        pass

    def get_file_url(self, ipfs_hash: str) -> str:
        """
        Get the public URL for an IPFS file via Pinata gateway.

        PSEUDOCODE:
        1. Construct and return gateway URL
        2. Format: https://gateway.pinata.cloud/ipfs/{ipfs_hash}
        """
        return f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}"

    def pin_by_hash(self, ipfs_hash: str) -> bool:
        """
        Pin an existing IPFS hash to your Pinata account.

        PSEUDOCODE:
        1. POST to Pinata pinByHash endpoint with IPFS hash
        2. Check response status
        3. Return True if successful, False otherwise
        4. Useful for preserving content discovered from events
        """
        pass

    def unpin(self, ipfs_hash: str) -> bool:
        """
        Unpin content from Pinata (remove from your pin set).

        PSEUDOCODE:
        1. DELETE request to Pinata unpin endpoint
        2. Check response status
        3. Return success/failure boolean
        4. Content remains on IPFS but no longer guaranteed by your account
        """
        pass


ipfs_service = IPFSService()
