import streamlit as st
import requests
import pandas as pd
import json
from web3 import Web3
from pathlib import Path

# 1. Configuration
API_URL = st.secrets.get("api", {}).get("API_URL", "http://localhost:8000")

# Load blockchain configuration from secrets
try:
    POLYGON_AMOY_RPC_URL = st.secrets["blockchain"]["POLYGON_AMOY_RPC_URL"]
    CONTRACT_ADDRESS = st.secrets["blockchain"]["CONTRACT_ADDRESS"]
    PINATA_API_KEY = st.secrets["ipfs"]["PINATA_API_KEY"]
    PINATA_SECRET_API_KEY = st.secrets["ipfs"]["PINATA_SECRET_API_KEY"]
except Exception as e:
    st.error(f"Configuration error: {e}. Please check .streamlit/secrets.toml")
    POLYGON_AMOY_RPC_URL = None
    CONTRACT_ADDRESS = None
    PINATA_API_KEY = None
    PINATA_SECRET_API_KEY = None

# Initialize Web3 connection
w3 = None
contract = None
if POLYGON_AMOY_RPC_URL:
    try:
        w3 = Web3(Web3.HTTPProvider(POLYGON_AMOY_RPC_URL))

        # Load contract ABI
        abi_path = Path(__file__).parent.parent / "backend" / "contract_abi.json"
        with open(abi_path, 'r') as f:
            contract_abi = json.load(f)

        if CONTRACT_ADDRESS and CONTRACT_ADDRESS != "0x0000000000000000000000000000000000000000":
            contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=contract_abi)
    except Exception as e:
        st.warning(f"Web3 initialization warning: {e}")

# Status enum mapping (matches Solidity contract)
STATUS_ENUM = {
    "Created": 0,
    "InTransit": 1,
    "OnShelf": 2,
    "Recalled": 3
}

st.set_page_config(
    page_title="FoodSafe Traceability DApp",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. IPFS Helper Functions
def upload_to_ipfs(file_content, filename):
    """Upload file to IPFS via Pinata and return the hash."""
    if not PINATA_API_KEY or PINATA_API_KEY == "your_pinata_api_key_here":
        st.warning("Pinata API keys not configured. Using simulated IPFS hash.")
        return f"Qm{'X' * 44}_simulated_{filename}"

    try:
        url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
        headers = {
            "pinata_api_key": PINATA_API_KEY,
            "pinata_secret_api_key": PINATA_SECRET_API_KEY
        }
        files = {
            'file': (filename, file_content)
        }
        response = requests.post(url, files=files, headers=headers)
        response.raise_for_status()
        ipfs_hash = response.json()["IpfsHash"]
        return ipfs_hash
    except Exception as e:
        st.error(f"IPFS upload failed: {e}")
        return None

def get_ipfs_gateway_url(ipfs_hash):
    """Return a gateway URL for viewing IPFS content."""
    return f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}"

# 3. Blockchain Helper Functions
def check_user_role(address, role_name):
    """Check if an address has a specific role on-chain."""
    if not contract or not address:
        return False

    try:
        # Get the role hash from the contract
        role_hash = getattr(contract.functions, f"{role_name}_ROLE")().call()
        has_role = contract.functions.hasRole(role_hash, Web3.to_checksum_address(address)).call()
        return has_role
    except Exception as e:
        st.error(f"Error checking role: {e}")
        return False

def get_role_hash(role_name):
    """Get the keccak256 hash of a role name."""
    if not contract:
        return None
    try:
        role_hash = getattr(contract.functions, f"{role_name}_ROLE")().call()
        return role_hash
    except Exception:
        return None

# 4. API Helper Functions (Client-side)
def get_all_lots():
    """Fetches the list of all food lots from the API."""
    try:
        response = requests.get(f"{API_URL}/lots")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to backend API: {e}")
        return None

def get_lot_history(token_id):
    """Fetches the history for a specific lot."""
    try:
        response = requests.get(f"{API_URL}/lots/{token_id}/history")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching history for lot {token_id}: {e}")
        return None

# ... (API Helper Functions) ...

# 5. Main Application Logic
st.sidebar.title("👤 Role Selection")

# Wallet Connection Section
st.sidebar.header("Wallet Connection")
user_address = st.sidebar.text_input(
    "Enter your wallet address:",
    placeholder="0x...",
    help="Enter your Ethereum address to interact with the blockchain"
)

if user_address:
    try:
        user_address = Web3.to_checksum_address(user_address)
        st.sidebar.success(f"Connected: {user_address[:6]}...{user_address[-4:]}")

        # Show user's roles
        if contract:
            st.sidebar.subheader("Your Roles")
            roles = []
            for role_name in ["PRODUCER", "DISTRIBUTOR", "RETAILER", "REGULATOR"]:
                if check_user_role(user_address, role_name):
                    roles.append(role_name)

            if roles:
                for r in roles:
                    st.sidebar.info(f"✓ {r}")
            else:
                st.sidebar.warning("No roles assigned")
    except Exception as e:
        st.sidebar.error(f"Invalid address: {e}")
        user_address = None

# For signing transactions (WARNING: Only for testing!)
st.sidebar.markdown("---")
if st.sidebar.checkbox("Enable Transaction Signing (Testing Only)", help="WARNING: Never enter your private key in production!"):
    private_key = st.sidebar.text_input(
        "Private Key (for testing only):",
        type="password",
        help="⚠️ DANGER: Only use test wallets!"
    )
else:
    private_key = None

st.sidebar.markdown("---")
role = st.sidebar.selectbox(
    "Select Dashboard View:",
    ["System Status", "Regulator", "Producer", "Distributor", "Admin"]
)

st.title(f"🛡️ FoodSafe: {role} Dashboard")

# --- Content based on Role ---

if role == "System Status":
    st.header("System Health")

    # Backend API Status
    st.subheader("Backend API")
    try:
        status_res = requests.get(f"{API_URL}/blockchain/status")
        st.json(status_res.json())
        st.success("✓ FastAPI backend is responding")
    except Exception as e:
        st.error(f"✗ Cannot connect to FastAPI backend: {e}")

    # Web3 Connection Status
    st.subheader("Blockchain Connection")
    if w3:
        try:
            is_connected = w3.is_connected()
            if is_connected:
                st.success(f"✓ Connected to Polygon Amoy")
                latest_block = w3.eth.block_number
                st.info(f"Latest block: {latest_block}")
            else:
                st.error("✗ Web3 provider not connected")
        except Exception as e:
            st.error(f"✗ Web3 connection error: {e}")
    else:
        st.warning("⚠ Web3 not initialized (check RPC URL in secrets.toml)")

    # Smart Contract Status
    st.subheader("Smart Contract")
    if contract:
        st.success(f"✓ Contract loaded at: {CONTRACT_ADDRESS}")
        try:
            # Try reading contract name
            token_name = contract.functions.name().call()
            token_symbol = contract.functions.symbol().call()
            st.info(f"Token: {token_name} ({token_symbol})")
        except Exception as e:
            st.error(f"Error reading contract: {e}")
    else:
        st.error("✗ Contract not loaded (check CONTRACT_ADDRESS in secrets.toml)")

    # IPFS Status
    st.subheader("IPFS/Pinata")
    if PINATA_API_KEY and PINATA_API_KEY != "your_pinata_api_key_here":
        st.success("✓ Pinata API keys configured")
    else:
        st.warning("⚠ Pinata API keys not configured")

# ... (After System Status check) ...
elif role == "Regulator":
    st.header("Traceability & Recall Management")

    lots_data = get_all_lots()

    if lots_data:
        df = pd.DataFrame(lots_data)
        st.subheader(f"All {len(df)} Food Lots")
        st.dataframe(df, use_container_width=True)

        # Recall Tool
        st.subheader("Trigger Surgical Recall")

        if not contract:
            st.error("Smart contract not loaded. Check configuration.")
        elif not user_address:
            st.warning("Please enter your wallet address in the sidebar to trigger recalls.")
        elif not check_user_role(user_address, "REGULATOR"):
            st.error("Your address does not have REGULATOR_ROLE. Cannot trigger recalls.")
        else:
            with st.form("recall_form"):
                lot_id_to_recall = st.number_input("Lot ID to Recall (Token ID)", min_value=1, step=1, key="recall_lot_id")
                submitted = st.form_submit_button("🚨 TRIGGER RECALL (Smart Contract TX)")

                if submitted:
                    if not private_key:
                        st.error("Please enable transaction signing in the sidebar and enter your private key.")
                    else:
                        try:
                            st.info(f"Preparing recall transaction for Lot #{lot_id_to_recall}...")

                            # Build transaction
                            nonce = w3.eth.get_transaction_count(user_address)
                            gas_price = w3.eth.gas_price

                            txn = contract.functions.triggerRecall(
                                int(lot_id_to_recall)
                            ).build_transaction({
                                'from': user_address,
                                'nonce': nonce,
                                'gas': 200000,
                                'gasPrice': gas_price
                            })

                            # Sign transaction
                            signed_txn = w3.eth.account.sign_transaction(txn, private_key)

                            # Send transaction
                            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
                            st.success(f"✓ Transaction sent! Hash: {tx_hash.hex()}")
                            st.info("Waiting for confirmation...")

                            # Wait for receipt
                            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

                            if receipt['status'] == 1:
                                st.success(f"✓ Recall for Lot #{lot_id_to_recall} confirmed on blockchain!")
                                st.info("The indexer will detect the LotRecalled event and update the database shortly.")
                                st.markdown(f"[View on PolygonScan](https://amoy.polygonscan.com/tx/{tx_hash.hex()})")
                            else:
                                st.error("Transaction failed. Check PolygonScan for details.")

                        except Exception as e:
                            st.error(f"Transaction failed: {e}")

        # Audit Trail Viewer
        st.subheader("Lot Audit Trail Viewer")
        selected_lot_id = st.selectbox("Select Lot ID for History:", df['token_id'].unique() if not df.empty else [1])
        if selected_lot_id:
            history = get_lot_history(selected_lot_id)
            if history:
                df_history = pd.DataFrame(history)
                # Display history ordered by timestamp
                st.dataframe(df_history.sort_values(by='timestamp'), use_container_width=True)
            else:
                st.info("No history found for this lot.")


# ... (After Regulator dashboard) ...
elif role == "Producer":
    st.header("Register New Food Lot")

    if not contract:
        st.error("Smart contract not loaded. Check configuration.")
    elif not user_address:
        st.warning("Please enter your wallet address in the sidebar to register lots.")
    elif not check_user_role(user_address, "PRODUCER"):
        st.error("Your address does not have PRODUCER_ROLE. Cannot register lots.")
    else:
        st.info("You have PRODUCER_ROLE. You can register new food lots.")

        with st.form("register_lot_form"):
            product_name = st.text_input("Product Name (e.g., 'Organic Lettuce Lot 42')")
            origin = st.text_input("Origin Location")
            uploaded_file = st.file_uploader("Upload Initial Metadata/Certificate (IPFS)", type=["json", "pdf", "txt"])

            submitted = st.form_submit_button("✅ Register Lot & Mint NFT")

            if submitted and product_name and origin:
                if not private_key:
                    st.error("Please enable transaction signing in the sidebar and enter your private key.")
                else:
                    try:
                        # Step 1: Upload to IPFS
                        st.info("Step 1: Uploading to IPFS...")
                        if uploaded_file:
                            file_content = uploaded_file.read()
                            ipfs_hash = upload_to_ipfs(file_content, uploaded_file.name)
                        else:
                            # Create a JSON metadata file
                            import json
                            from datetime import datetime
                            metadata = {
                                "productName": product_name,
                                "origin": origin,
                                "timestamp": datetime.now().isoformat(),
                                "registeredBy": user_address
                            }
                            metadata_json = json.dumps(metadata, indent=2)
                            ipfs_hash = upload_to_ipfs(metadata_json.encode(), "metadata.json")

                        if not ipfs_hash:
                            st.error("IPFS upload failed. Cannot proceed.")
                        else:
                            st.success(f"✓ IPFS Hash: {ipfs_hash}")
                            st.markdown(f"[View on IPFS]({get_ipfs_gateway_url(ipfs_hash)})")

                            # Step 2: Register on blockchain
                            st.info("Step 2: Registering lot on blockchain...")

                            nonce = w3.eth.get_transaction_count(user_address)
                            gas_price = w3.eth.gas_price

                            txn = contract.functions.registerLot(
                                product_name,
                                origin,
                                ipfs_hash
                            ).build_transaction({
                                'from': user_address,
                                'nonce': nonce,
                                'gas': 300000,
                                'gasPrice': gas_price
                            })

                            # Sign and send
                            signed_txn = w3.eth.account.sign_transaction(txn, private_key)
                            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

                            st.success(f"✓ Transaction sent! Hash: {tx_hash.hex()}")
                            st.info("Waiting for confirmation...")

                            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

                            if receipt['status'] == 1:
                                st.success("✓ New Lot NFT minted successfully!")
                                st.info("The indexer will detect the LotRegistered event and update the database.")
                                st.markdown(f"[View on PolygonScan](https://amoy.polygonscan.com/tx/{tx_hash.hex()})")
                                st.balloons()
                            else:
                                st.error("Transaction failed. Check PolygonScan for details.")

                    except Exception as e:
                        st.error(f"Registration failed: {e}")

elif role == "Distributor":
    st.header("Update Lot Custody and Status")

    if not contract:
        st.error("Smart contract not loaded. Check configuration.")
    elif not user_address:
        st.warning("Please enter your wallet address in the sidebar to update lots.")
    elif not (check_user_role(user_address, "DISTRIBUTOR") or check_user_role(user_address, "RETAILER")):
        st.error("Your address does not have DISTRIBUTOR_ROLE or RETAILER_ROLE. Cannot update lots.")
    else:
        st.info("You can update lot status and custody.")

        with st.form("update_lot_form"):
            lot_id = st.number_input("Lot ID to Update", min_value=1, step=1)
            new_status = st.selectbox(
                "New Status:",
                ["InTransit", "OnShelf"]
            )
            uploaded_file = st.file_uploader(
                "Upload Status Update Document (e.g., Temperature Log)",
                type=["json", "pdf", "txt", "csv"],
                help="Optional: Upload a document to IPFS"
            )
            manual_ipfs_hash = st.text_input(
                "Or enter existing IPFS Hash:",
                help="Leave blank to auto-generate or upload a file"
            )

            submitted = st.form_submit_button("🔄 Update Lot Status")

            if submitted and lot_id > 0:
                if not private_key:
                    st.error("Please enable transaction signing in the sidebar and enter your private key.")
                else:
                    try:
                        # Step 1: Handle IPFS upload
                        ipfs_hash = manual_ipfs_hash
                        if uploaded_file:
                            st.info("Step 1: Uploading to IPFS...")
                            file_content = uploaded_file.read()
                            ipfs_hash = upload_to_ipfs(file_content, uploaded_file.name)
                            st.success(f"✓ IPFS Hash: {ipfs_hash}")
                        elif not ipfs_hash:
                            # Create default metadata
                            from datetime import datetime
                            metadata = {
                                "lotId": lot_id,
                                "newStatus": new_status,
                                "updatedBy": user_address,
                                "timestamp": datetime.now().isoformat()
                            }
                            metadata_json = json.dumps(metadata, indent=2)
                            ipfs_hash = upload_to_ipfs(metadata_json.encode(), f"update_lot_{lot_id}.json")
                            st.success(f"✓ Generated IPFS Hash: {ipfs_hash}")

                        if not ipfs_hash:
                            st.error("IPFS hash required. Cannot proceed.")
                        else:
                            # Step 2: Update on blockchain
                            st.info(f"Step 2: Updating Lot #{lot_id} to status **{new_status}**...")

                            nonce = w3.eth.get_transaction_count(user_address)
                            gas_price = w3.eth.gas_price

                            txn = contract.functions.updateLot(
                                int(lot_id),
                                ipfs_hash,
                                STATUS_ENUM[new_status]
                            ).build_transaction({
                                'from': user_address,
                                'nonce': nonce,
                                'gas': 250000,
                                'gasPrice': gas_price
                            })

                            signed_txn = w3.eth.account.sign_transaction(txn, private_key)
                            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

                            st.success(f"✓ Transaction sent! Hash: {tx_hash.hex()}")
                            st.info("Waiting for confirmation...")

                            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

                            if receipt['status'] == 1:
                                st.success(f"✓ Lot #{lot_id} updated successfully!")
                                st.info("The indexer will detect the LotStatusUpdated event and update the database.")
                                st.markdown(f"[View on PolygonScan](https://amoy.polygonscan.com/tx/{tx_hash.hex()})")
                            else:
                                st.error("Transaction failed. Check PolygonScan for details.")

                    except Exception as e:
                        st.error(f"Update failed: {e}")

# Admin Dashboard for Role Management
elif role == "Admin":
    st.header("Role Management (Admin)")

    if not contract:
        st.error("Smart contract not loaded. Check configuration.")
    elif not user_address:
        st.warning("Please enter your wallet address in the sidebar.")
    elif not check_user_role(user_address, "DEFAULT_ADMIN"):
        st.error("Your address does not have DEFAULT_ADMIN_ROLE. Cannot manage roles.")
        st.info("Only the contract deployer or addresses with DEFAULT_ADMIN_ROLE can grant/revoke roles.")
    else:
        st.success("You have DEFAULT_ADMIN_ROLE. You can manage all roles.")

        # Display role hashes
        st.subheader("Role Information")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Role Hashes:**")
            for role_name in ["PRODUCER", "DISTRIBUTOR", "RETAILER", "REGULATOR"]:
                role_hash = get_role_hash(role_name)
                if role_hash:
                    st.code(f"{role_name}_ROLE: {role_hash.hex()}")

        with col2:
            st.markdown("**Check Address Roles:**")
            check_addr = st.text_input("Enter address to check:", key="check_roles_addr")
            if check_addr:
                try:
                    check_addr = Web3.to_checksum_address(check_addr)
                    for role_name in ["PRODUCER", "DISTRIBUTOR", "RETAILER", "REGULATOR"]:
                        has_role = check_user_role(check_addr, role_name)
                        st.write(f"{'✓' if has_role else '✗'} {role_name}_ROLE")
                except Exception as e:
                    st.error(f"Invalid address: {e}")

        st.markdown("---")

        # Grant Role Form
        st.subheader("Grant Role")
        with st.form("grant_role_form"):
            role_to_grant = st.selectbox("Select Role:", ["PRODUCER", "DISTRIBUTOR", "RETAILER", "REGULATOR"])
            address_to_grant = st.text_input("Address to grant role:")
            grant_submitted = st.form_submit_button("Grant Role")

            if grant_submitted and address_to_grant:
                if not private_key:
                    st.error("Please enable transaction signing in the sidebar and enter your private key.")
                else:
                    try:
                        address_to_grant = Web3.to_checksum_address(address_to_grant)

                        # Get role hash
                        role_hash = get_role_hash(role_to_grant)

                        st.info(f"Granting {role_to_grant}_ROLE to {address_to_grant}...")

                        nonce = w3.eth.get_transaction_count(user_address)
                        gas_price = w3.eth.gas_price

                        txn = contract.functions.grantRole(
                            role_hash,
                            address_to_grant
                        ).build_transaction({
                            'from': user_address,
                            'nonce': nonce,
                            'gas': 150000,
                            'gasPrice': gas_price
                        })

                        signed_txn = w3.eth.account.sign_transaction(txn, private_key)
                        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

                        st.success(f"✓ Transaction sent! Hash: {tx_hash.hex()}")

                        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

                        if receipt['status'] == 1:
                            st.success(f"✓ {role_to_grant}_ROLE granted to {address_to_grant}!")
                            st.markdown(f"[View on PolygonScan](https://amoy.polygonscan.com/tx/{tx_hash.hex()})")
                        else:
                            st.error("Transaction failed.")

                    except Exception as e:
                        st.error(f"Grant failed: {e}")