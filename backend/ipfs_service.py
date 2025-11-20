import requests
import json
from config import settings
from typing import Dict, Any
import os


class IPFSService:
    """
    Service for uploading and retrieving data from IPFS via Pinata.
    """

    def __init__(self):
        """
        Initialize Pinata API credentials and headers.
        """
        self.api_key = settings.PINATA_API_KEY
        self.secret_key = settings.PINATA_SECRET_API_KEY
        self.base_url = settings.PINATA_BASE_URL
        self.headers = {
            "pinata_api_key": self.api_key,
            "pinata_secret_api_key": self.secret_key
        }
        self.gateway_url = "https://gateway.pinata.cloud/ipfs"

    def upload_json(self, data: Dict[str, Any], filename: str = "metadata.json") -> str:
        """
        Upload JSON data to IPFS via Pinata.
        
        Args:
            data: Dictionary of data to upload
            filename: Optional metadata filename
            
        Returns:
            str: IPFS hash (CID) of the uploaded content
        """
        url = f"{self.base_url}/pinning/pinJSONToIPFS"
        
        payload = {
            "pinataContent": data,
            "pinataMetadata": {
                "name": filename
            },
            "pinataOptions": {
                "cidVersion": 1
            }
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers={**self.headers, "Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            result = response.json()
            ipfs_hash = result.get("IpfsHash")
            
            if not ipfs_hash:
                raise ValueError("No IPFS hash returned from Pinata")
            
            print(f"Successfully uploaded JSON to IPFS: {ipfs_hash}")
            return ipfs_hash
            
        except requests.exceptions.RequestException as e:
            print(f"Error uploading JSON to IPFS: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error uploading JSON: {e}")
            raise

    def upload_file(self, file_path: str, filename: str = None) -> str:
        """
        Upload a file to IPFS via Pinata.
        
        Args:
            file_path: Path to the file to upload
            filename: Optional custom filename for metadata
            
        Returns:
            str: IPFS hash (CID) of the uploaded file
        """
        url = f"{self.base_url}/pinning/pinFileToIPFS"
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if filename is None:
            filename = os.path.basename(file_path)
        
        try:
            with open(file_path, 'rb') as file:
                files = {
                    'file': (filename, file)
                }
                
                metadata = json.dumps({
                    "name": filename
                })
                
                data = {
                    "pinataMetadata": metadata,
                    "pinataOptions": json.dumps({
                        "cidVersion": 1
                    })
                }
                
                response = requests.post(
                    url,
                    files=files,
                    data=data,
                    headers=self.headers
                )
                response.raise_for_status()
                
                result = response.json()
                ipfs_hash = result.get("IpfsHash")
                
                if not ipfs_hash:
                    raise ValueError("No IPFS hash returned from Pinata")
                
                print(f"Successfully uploaded file to IPFS: {ipfs_hash}")
                return ipfs_hash
                
        except requests.exceptions.RequestException as e:
            print(f"Error uploading file to IPFS: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error uploading file: {e}")
            raise

    def get_content(self, ipfs_hash: str) -> Dict[str, Any]:
        """
        Retrieve JSON content from IPFS using Pinata gateway.
        
        Args:
            ipfs_hash: The IPFS hash (CID) to retrieve
            
        Returns:
            Dict: Parsed JSON content from IPFS
        """
        url = f"{self.gateway_url}/{ipfs_hash}"
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Try to parse as JSON
            try:
                return response.json()
            except json.JSONDecodeError:
                # If not JSON, return as text
                return {"content": response.text}
                
        except requests.exceptions.RequestException as e:
            print(f"Error retrieving content from IPFS: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error retrieving content: {e}")
            raise

    def get_file_url(self, ipfs_hash: str) -> str:
        """
        Get the public URL for an IPFS file via Pinata gateway.
        
        Args:
            ipfs_hash: The IPFS hash (CID)
            
        Returns:
            str: Full gateway URL to access the content
        """
        return f"{self.gateway_url}/{ipfs_hash}"

    def pin_by_hash(self, ipfs_hash: str) -> bool:
        """
        Pin an existing IPFS hash to your Pinata account.
        
        Args:
            ipfs_hash: The IPFS hash (CID) to pin
            
        Returns:
            bool: True if successful, False otherwise
        """
        url = f"{self.base_url}/pinning/pinByHash"
        
        payload = {
            "hashToPin": ipfs_hash
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers={**self.headers, "Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            print(f"Successfully pinned IPFS hash: {ipfs_hash}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"Error pinning IPFS hash: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error pinning hash: {e}")
            return False

    def unpin(self, ipfs_hash: str) -> bool:
        """
        Unpin content from Pinata (remove from your pin set).
        
        Args:
            ipfs_hash: The IPFS hash (CID) to unpin
            
        Returns:
            bool: True if successful, False otherwise
        """
        url = f"{self.base_url}/pinning/unpin/{ipfs_hash}"
        
        try:
            response = requests.delete(url, headers=self.headers)
            response.raise_for_status()
            
            print(f"Successfully unpinned IPFS hash: {ipfs_hash}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"Error unpinning IPFS hash: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error unpinning hash: {e}")
            return False

    def test_connection(self) -> bool:
        """
        Test connection to Pinata API.
        
        Returns:
            bool: True if connected and authenticated, False otherwise
        """
        url = f"{self.base_url}/data/testAuthentication"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            print("Successfully authenticated with Pinata API")
            return True
        except Exception as e:
            print(f"Pinata authentication failed: {e}")
            return False


ipfs_service = IPFSService()
