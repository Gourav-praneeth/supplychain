import streamlit as st

# MUST be first Streamlit command
st.set_page_config(
    page_title="FoodSafe Traceability DApp",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

import requests
import pandas as pd
import json
import asyncio
import nest_asyncio
from pathlib import Path
from datetime import datetime

# Fix asyncio event loop issue for Streamlit + web3.py
try:
    nest_asyncio.apply()
except:
    pass

# Ensure event loop exists
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

from web3 import Web3

# =============================================================================
# 1. CONFIGURATION
# =============================================================================
API_URL = st.secrets.get("api", {}).get("API_URL", "http://localhost:8000")

# Load blockchain configuration from secrets
config_error = None
try:
    POLYGON_AMOY_RPC_URL = st.secrets["blockchain"]["POLYGON_AMOY_RPC_URL"]
    CONTRACT_ADDRESS = st.secrets["blockchain"]["CONTRACT_ADDRESS"]
    PINATA_API_KEY = st.secrets["ipfs"]["PINATA_API_KEY"]
    PINATA_SECRET_API_KEY = st.secrets["ipfs"]["PINATA_SECRET_API_KEY"]
except Exception as e:
    config_error = str(e)
    POLYGON_AMOY_RPC_URL = None
    CONTRACT_ADDRESS = None
    PINATA_API_KEY = None
    PINATA_SECRET_API_KEY = None

# Initialize Web3 connection
w3 = None
contract = None
contract_abi = None
web3_error = None

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
        web3_error = str(e)

# Status enum mapping (matches Solidity contract)
STATUS_ENUM = {
    "Created": 0,
    "InTransit": 1,
    "OnShelf": 2,
    "Recalled": 3
}

STATUS_COLORS = {
    "Created": "🟢",
    "InTransit": "🟡",
    "OnShelf": "🔵",
    "Recalled": "🔴"
}

# Show config errors after page config
if config_error:
    st.error(f"⚠️ Configuration error: {config_error}. Please check .streamlit/secrets.toml")
if web3_error:
    st.warning(f"⚠️ Web3 initialization warning: {web3_error}")

# =============================================================================
# 2. IPFS HELPER FUNCTIONS
# =============================================================================
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

# =============================================================================
# 3. BLOCKCHAIN HELPER FUNCTIONS
# =============================================================================
def check_user_role(address, role_name):
    """Check if an address has a specific role on-chain."""
    if not contract or not address:
        return False

    try:
        # Handle DEFAULT_ADMIN specially
        if role_name == "DEFAULT_ADMIN":
            role_hash = contract.functions.DEFAULT_ADMIN_ROLE().call()
        else:
            role_hash = getattr(contract.functions, f"{role_name}_ROLE")().call()
        has_role = contract.functions.hasRole(role_hash, Web3.to_checksum_address(address)).call()
        return has_role
    except Exception as e:
        return False

def get_role_hash(role_name):
    """Get the keccak256 hash of a role name."""
    if not contract:
        return None
    try:
        if role_name == "DEFAULT_ADMIN":
            return contract.functions.DEFAULT_ADMIN_ROLE().call()
        role_hash = getattr(contract.functions, f"{role_name}_ROLE")().call()
        return role_hash
    except Exception:
        return None

def get_lot_from_blockchain(token_id):
    """Get lot details directly from blockchain."""
    if not contract:
        return None
    try:
        lot = contract.functions.getLot(token_id).call()
        return {
            "lotId": lot[0],
            "productName": lot[1],
            "origin": lot[2],
            "currentOwner": lot[3],
            "status": ["Created", "InTransit", "OnShelf", "Recalled"][lot[4]],
            "historyCount": len(lot[5])
        }
    except Exception as e:
        return None

# =============================================================================
# 4. API HELPER FUNCTIONS
# =============================================================================
def get_all_lots():
    """Fetches the list of all food lots from the API."""
    try:
        response = requests.get(f"{API_URL}/lots", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to backend API: {e}")
        return None

def get_lot_details(token_id):
    """Fetches details for a specific lot."""
    try:
        response = requests.get(f"{API_URL}/lots/{token_id}", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None

def get_lot_history(token_id):
    """Fetches the history for a specific lot."""
    try:
        response = requests.get(f"{API_URL}/lots/{token_id}/history", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return None

def get_all_recalls():
    """Fetches all recall events from the API."""
    try:
        response = requests.get(f"{API_URL}/recalls", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None

def get_system_stats():
    """Fetches system statistics from the API."""
    try:
        response = requests.get(f"{API_URL}/stats", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None

# =============================================================================
# 5. SIDEBAR - WALLET & ROLE SELECTION
# =============================================================================
st.sidebar.title("🛡️ FoodSafe DApp")
st.sidebar.markdown("---")

# Wallet Connection Section
st.sidebar.header("👛 Wallet Connection")
user_address = st.sidebar.text_input(
    "Wallet Address:",
    placeholder="0x...",
    help="Enter your Ethereum address to interact with the blockchain"
)

private_key = None

if user_address:
    try:
        user_address = Web3.to_checksum_address(user_address)
        st.sidebar.success(f"✓ {user_address[:6]}...{user_address[-4:]}")

        # Show user's roles
        if contract:
            st.sidebar.caption("**Your Roles:**")
            roles = []
            for role_name in ["PRODUCER", "DISTRIBUTOR", "RETAILER", "REGULATOR"]:
                if check_user_role(user_address, role_name):
                    roles.append(role_name)
            
            if check_user_role(user_address, "DEFAULT_ADMIN"):
                roles.append("ADMIN")

            if roles:
                st.sidebar.write(" | ".join([f"✓ {r}" for r in roles]))
            else:
                st.sidebar.warning("No roles assigned")
    except Exception as e:
        st.sidebar.error(f"Invalid address")
        user_address = None

# Transaction signing
st.sidebar.markdown("---")
if st.sidebar.checkbox("🔐 Enable TX Signing", help="⚠️ Only for testing!"):
    private_key = st.sidebar.text_input(
        "Private Key:",
        type="password",
        help="⚠️ NEVER use real wallets!"
    )

# Dashboard selection
st.sidebar.markdown("---")
st.sidebar.header("📊 Dashboard")
role = st.sidebar.selectbox(
    "Select View:",
    ["🔍 Public Tracking", "📊 System Status", "👮 Regulator", "🌾 Producer", "🚚 Distributor", "⚙️ Admin"]
)

# =============================================================================
# 6. MAIN CONTENT - DASHBOARDS
# =============================================================================

st.title(f"{role.split()[0]} FoodSafe: {role.split()[-1]} Dashboard")

# -----------------------------------------------------------------------------
# PUBLIC TRACKING (No wallet required)
# -----------------------------------------------------------------------------
if role == "🔍 Public Tracking":
    st.header("🔍 Track Your Food")
    st.markdown("Enter a Lot ID to trace its journey from farm to shelf.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        track_lot_id = st.number_input("Enter Lot ID:", min_value=1, step=1, value=1)
        track_button = st.button("🔍 Track Lot", use_container_width=True)
    
    if track_button:
        with st.spinner("Fetching lot information..."):
            # Try API first
            lot_details = get_lot_details(track_lot_id)
            lot_history = get_lot_history(track_lot_id)
            
            # Also try blockchain directly
            blockchain_lot = get_lot_from_blockchain(track_lot_id)
            
            if blockchain_lot:
                st.success(f"✓ Found Lot #{track_lot_id}")
                
                # Display lot info
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Product", blockchain_lot['productName'])
                with col2:
                    st.metric("Origin", blockchain_lot['origin'])
                with col3:
                    status = blockchain_lot['status']
                    st.metric("Status", f"{STATUS_COLORS.get(status, '⚪')} {status}")
                
                st.markdown("---")
                
                # Show journey timeline
                st.subheader("📜 Journey Timeline")
                if lot_history:
                    for i, entry in enumerate(lot_history):
                        with st.expander(f"Step {i+1}: {entry.get('event_type', 'Event')}", expanded=(i==len(lot_history)-1)):
                            st.write(f"**Timestamp:** {entry.get('timestamp', 'N/A')}")
                            st.write(f"**By:** {entry.get('stakeholder_address', 'N/A')[:10]}...")
                            if entry.get('ipfs_hash'):
                                st.write(f"**IPFS:** [{entry['ipfs_hash'][:20]}...]({get_ipfs_gateway_url(entry['ipfs_hash'])})")
                            st.write(f"**TX:** [{entry.get('transaction_hash', 'N/A')[:20]}...](https://amoy.polygonscan.com/tx/{entry.get('transaction_hash', '')})")
                else:
                    st.info("No history available from indexer yet.")
                
                # Verification link
                st.markdown("---")
                st.markdown(f"🔗 [Verify on PolygonScan](https://amoy.polygonscan.com/address/{CONTRACT_ADDRESS})")
                
            else:
                st.error(f"❌ Lot #{track_lot_id} not found. Please check the ID.")

# -----------------------------------------------------------------------------
# SYSTEM STATUS
# -----------------------------------------------------------------------------
elif role == "📊 System Status":
    st.header("🏥 System Health")

    col1, col2 = st.columns(2)
    
    with col1:
        # Backend API Status
        st.subheader("🖥️ Backend API")
        try:
            status_res = requests.get(f"{API_URL}/blockchain/status", timeout=5)
            data = status_res.json()
            st.success("✓ API Online")
            st.json(data)
        except Exception as e:
            st.error(f"✗ API Offline: {e}")

        # IPFS Status
        st.subheader("📦 IPFS/Pinata")
        if PINATA_API_KEY and PINATA_API_KEY != "your_pinata_api_key_here":
            st.success("✓ Pinata configured")
        else:
            st.warning("⚠ Pinata not configured")
    
    with col2:
        # Blockchain Status
        st.subheader("⛓️ Blockchain")
        if w3 and w3.is_connected():
            st.success("✓ Connected to Polygon Amoy")
            st.info(f"Block: {w3.eth.block_number}")
        else:
            st.error("✗ Not connected")

        # Contract Status
        st.subheader("📄 Smart Contract")
        if contract:
            st.success(f"✓ Loaded")
            st.code(CONTRACT_ADDRESS, language=None)
            try:
                name = contract.functions.name().call()
                symbol = contract.functions.symbol().call()
                st.info(f"Token: {name} ({symbol})")
            except:
                pass
        else:
            st.error("✗ Not loaded")
    
    # System Statistics
    st.markdown("---")
    st.subheader("📈 Statistics")
    stats = get_system_stats()
    if stats:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Lots", stats.get('total_lots', 0))
        col2.metric("Recalled Lots", stats.get('recalled_lots', 0))
        col3.metric("History Entries", stats.get('total_history_entries', 0))
        col4.metric("Recall Events", stats.get('total_recall_events', 0))

# -----------------------------------------------------------------------------
# REGULATOR DASHBOARD
# -----------------------------------------------------------------------------
elif role == "👮 Regulator":
    st.header("👮 Traceability & Recall Management")

    # Tabs for different functions
    tab1, tab2, tab3 = st.tabs(["📋 All Lots", "🚨 Trigger Recall", "📜 Audit Trail"])
    
    with tab1:
        st.subheader("All Food Lots")
        lots_data = get_all_lots()
        
        if lots_data and len(lots_data) > 0:
            df = pd.DataFrame(lots_data)
            
            # Add status emoji
            if 'status' in df.columns:
                df['status_display'] = df['status'].apply(lambda x: f"{STATUS_COLORS.get(x, '⚪')} {x}")
            
            st.dataframe(df, use_container_width=True)
            st.caption(f"Total: {len(df)} lots")
        else:
            st.info("No lots registered yet.")
        
        # Show recalls
        st.markdown("---")
        st.subheader("🚨 Recent Recalls")
        recalls = get_all_recalls()
        if recalls and len(recalls) > 0:
            df_recalls = pd.DataFrame(recalls)
            st.dataframe(df_recalls, use_container_width=True)
        else:
            st.success("✓ No recalls in system")
    
    with tab2:
        st.subheader("🚨 Trigger Surgical Recall")
        
        if not contract:
            st.error("Smart contract not loaded.")
        elif not user_address:
            st.warning("⚠️ Enter wallet address in sidebar")
        elif not check_user_role(user_address, "REGULATOR"):
            st.error("❌ You need REGULATOR_ROLE")
        else:
            st.success("✓ You have REGULATOR_ROLE")
            
            with st.form("recall_form"):
                lot_id_to_recall = st.number_input("Lot ID to Recall:", min_value=1, step=1)
                recall_reason = st.text_area("Reason for Recall:", placeholder="E.g., E. coli contamination detected")
                submitted = st.form_submit_button("🚨 TRIGGER RECALL", type="primary")

                if submitted:
                    if not private_key:
                        st.error("Enable transaction signing in sidebar")
                    else:
                        try:
                            with st.spinner("Processing recall..."):
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

                                signed_txn = w3.eth.account.sign_transaction(txn, private_key)
                                tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
                                
                                st.info(f"TX sent: {tx_hash.hex()[:20]}...")
                                
                                receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

                                if receipt['status'] == 1:
                                    st.success(f"✓ Lot #{lot_id_to_recall} RECALLED!")
                                    st.markdown(f"[View on PolygonScan](https://amoy.polygonscan.com/tx/{tx_hash.hex()})")
                                    st.balloons()
                                else:
                                    st.error("Transaction failed")

                        except Exception as e:
                            st.error(f"Error: {e}")
    
    with tab3:
        st.subheader("📜 Lot Audit Trail")
        lots_data = get_all_lots()
        
        if lots_data and len(lots_data) > 0:
            lot_ids = [lot['token_id'] for lot in lots_data]
            selected_lot = st.selectbox("Select Lot:", lot_ids)
            
            if selected_lot:
                history = get_lot_history(selected_lot)
                if history:
                    st.write(f"**{len(history)} events** for Lot #{selected_lot}")
                    df_history = pd.DataFrame(history)
                    st.dataframe(df_history, use_container_width=True)
                else:
                    st.info("No history found")
        else:
            st.info("No lots to audit")

# -----------------------------------------------------------------------------
# PRODUCER DASHBOARD
# -----------------------------------------------------------------------------
elif role == "🌾 Producer":
    st.header("🌾 Register New Food Lot")

    if not contract:
        st.error("Smart contract not loaded.")
    elif not user_address:
        st.warning("⚠️ Enter wallet address in sidebar")
    elif not check_user_role(user_address, "PRODUCER"):
        st.error("❌ You need PRODUCER_ROLE to register lots")
    else:
        st.success("✓ You have PRODUCER_ROLE")

        with st.form("register_lot_form"):
            col1, col2 = st.columns(2)
            with col1:
                product_name = st.text_input("Product Name *", placeholder="Organic Romaine Lettuce")
            with col2:
                origin = st.text_input("Origin Location *", placeholder="Salinas Valley, CA")
            
            uploaded_file = st.file_uploader(
                "Upload Certificate (optional)", 
                type=["json", "pdf", "txt", "png", "jpg"],
                help="Upload organic certification, lab results, etc."
            )

            submitted = st.form_submit_button("✅ Register Lot & Mint NFT", type="primary")

            if submitted:
                if not product_name or not origin:
                    st.error("Product name and origin are required")
                elif not private_key:
                    st.error("Enable transaction signing in sidebar")
                else:
                    try:
                        with st.spinner("Registering lot..."):
                            # Step 1: IPFS
                            st.info("📦 Uploading to IPFS...")
                            if uploaded_file:
                                ipfs_hash = upload_to_ipfs(uploaded_file.read(), uploaded_file.name)
                            else:
                                metadata = {
                                    "productName": product_name,
                                    "origin": origin,
                                    "timestamp": datetime.now().isoformat(),
                                    "registeredBy": user_address
                                }
                                ipfs_hash = upload_to_ipfs(json.dumps(metadata).encode(), "metadata.json")

                            if not ipfs_hash:
                                st.error("IPFS upload failed")
                            else:
                                st.success(f"✓ IPFS: {ipfs_hash[:20]}...")

                                # Step 2: Blockchain
                                st.info("⛓️ Minting NFT on blockchain...")
                                nonce = w3.eth.get_transaction_count(user_address)
                                gas_price = w3.eth.gas_price

                                txn = contract.functions.registerLot(
                                    product_name, origin, ipfs_hash
                                ).build_transaction({
                                    'from': user_address,
                                    'nonce': nonce,
                                    'gas': 300000,
                                    'gasPrice': gas_price
                                })

                                signed_txn = w3.eth.account.sign_transaction(txn, private_key)
                                tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
                                
                                receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

                                if receipt['status'] == 1:
                                    st.success("✓ Lot registered successfully!")
                                    st.markdown(f"[View on PolygonScan](https://amoy.polygonscan.com/tx/{tx_hash.hex()})")
                                    st.balloons()
                                else:
                                    st.error("Transaction failed")

                    except Exception as e:
                        st.error(f"Error: {e}")

# -----------------------------------------------------------------------------
# DISTRIBUTOR DASHBOARD
# -----------------------------------------------------------------------------
elif role == "🚚 Distributor":
    st.header("🚚 Update Lot Status")

    if not contract:
        st.error("Smart contract not loaded.")
    elif not user_address:
        st.warning("⚠️ Enter wallet address in sidebar")
    elif not (check_user_role(user_address, "PRODUCER") or 
              check_user_role(user_address, "DISTRIBUTOR") or 
              check_user_role(user_address, "RETAILER")):
        st.error("❌ You need PRODUCER, DISTRIBUTOR, or RETAILER role")
    else:
        st.success("✓ You can update lot status")

        with st.form("update_lot_form"):
            col1, col2 = st.columns(2)
            with col1:
                lot_id = st.number_input("Lot ID *", min_value=1, step=1)
            with col2:
                new_status = st.selectbox("New Status *", ["InTransit", "OnShelf"])
            
            uploaded_file = st.file_uploader(
                "Upload Document (optional)",
                type=["json", "pdf", "txt", "csv"],
                help="Temperature log, shipping manifest, etc."
            )

            submitted = st.form_submit_button("🔄 Update Status", type="primary")

            if submitted and lot_id > 0:
                if not private_key:
                    st.error("Enable transaction signing in sidebar")
                else:
                    try:
                        with st.spinner("Updating lot..."):
                            # IPFS
                            if uploaded_file:
                                ipfs_hash = upload_to_ipfs(uploaded_file.read(), uploaded_file.name)
                            else:
                                metadata = {
                                    "lotId": lot_id,
                                    "newStatus": new_status,
                                    "updatedBy": user_address,
                                    "timestamp": datetime.now().isoformat()
                                }
                                ipfs_hash = upload_to_ipfs(json.dumps(metadata).encode(), f"update_{lot_id}.json")

                            if not ipfs_hash:
                                st.error("IPFS upload failed")
                            else:
                                # Blockchain
                                nonce = w3.eth.get_transaction_count(user_address)
                                gas_price = w3.eth.gas_price

                                txn = contract.functions.updateLot(
                                    int(lot_id), ipfs_hash, STATUS_ENUM[new_status]
                                ).build_transaction({
                                    'from': user_address,
                                    'nonce': nonce,
                                    'gas': 250000,
                                    'gasPrice': gas_price
                                })

                                signed_txn = w3.eth.account.sign_transaction(txn, private_key)
                                tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
                                
                                receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

                                if receipt['status'] == 1:
                                    st.success(f"✓ Lot #{lot_id} updated to {new_status}!")
                                    st.markdown(f"[View on PolygonScan](https://amoy.polygonscan.com/tx/{tx_hash.hex()})")
                                else:
                                    st.error("Transaction failed")

                    except Exception as e:
                        st.error(f"Error: {e}")

# -----------------------------------------------------------------------------
# ADMIN DASHBOARD
# -----------------------------------------------------------------------------
elif role == "⚙️ Admin":
    st.header("⚙️ Role Management")

    if not contract:
        st.error("Smart contract not loaded.")
    elif not user_address:
        st.warning("⚠️ Enter wallet address in sidebar")
    elif not check_user_role(user_address, "DEFAULT_ADMIN"):
        st.error("❌ You need DEFAULT_ADMIN_ROLE")
        st.info("Only the contract deployer has this role initially.")
    else:
        st.success("✓ You have ADMIN privileges")

        tab1, tab2, tab3 = st.tabs(["🔍 Check Roles", "➕ Grant Role", "➖ Revoke Role"])
        
        with tab1:
            st.subheader("Check Address Roles")
            check_addr = st.text_input("Address to check:", placeholder="0x...")
            
            if check_addr:
                try:
                    check_addr = Web3.to_checksum_address(check_addr)
                    st.write(f"**Roles for {check_addr[:10]}...:**")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        for role_name in ["PRODUCER", "DISTRIBUTOR"]:
                            has = check_user_role(check_addr, role_name)
                            st.write(f"{'✅' if has else '❌'} {role_name}")
                    with col2:
                        for role_name in ["RETAILER", "REGULATOR"]:
                            has = check_user_role(check_addr, role_name)
                            st.write(f"{'✅' if has else '❌'} {role_name}")
                except:
                    st.error("Invalid address")
        
        with tab2:
            st.subheader("Grant Role")
            with st.form("grant_form"):
                grant_role = st.selectbox("Role:", ["PRODUCER", "DISTRIBUTOR", "RETAILER", "REGULATOR"])
                grant_addr = st.text_input("Address:", placeholder="0x...")
                grant_btn = st.form_submit_button("➕ Grant Role", type="primary")
                
                if grant_btn and grant_addr:
                    if not private_key:
                        st.error("Enable transaction signing")
                    else:
                        try:
                            with st.spinner("Granting role..."):
                                grant_addr = Web3.to_checksum_address(grant_addr)
                                role_hash = get_role_hash(grant_role)
                                
                                nonce = w3.eth.get_transaction_count(user_address)
                                txn = contract.functions.grantRole(
                                    role_hash, grant_addr
                                ).build_transaction({
                                    'from': user_address,
                                    'nonce': nonce,
                                    'gas': 150000,
                                    'gasPrice': w3.eth.gas_price
                                })

                                signed_txn = w3.eth.account.sign_transaction(txn, private_key)
                                tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
                                receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

                                if receipt['status'] == 1:
                                    st.success(f"✓ {grant_role} granted!")
                                else:
                                    st.error("Failed")
                        except Exception as e:
                            st.error(f"Error: {e}")
        
        with tab3:
            st.subheader("Revoke Role")
            with st.form("revoke_form"):
                revoke_role = st.selectbox("Role:", ["PRODUCER", "DISTRIBUTOR", "RETAILER", "REGULATOR"], key="revoke_role")
                revoke_addr = st.text_input("Address:", placeholder="0x...", key="revoke_addr")
                revoke_btn = st.form_submit_button("➖ Revoke Role", type="primary")
                
                if revoke_btn and revoke_addr:
                    if not private_key:
                        st.error("Enable transaction signing")
                    else:
                        try:
                            with st.spinner("Revoking role..."):
                                revoke_addr = Web3.to_checksum_address(revoke_addr)
                                role_hash = get_role_hash(revoke_role)
                                
                                nonce = w3.eth.get_transaction_count(user_address)
                                txn = contract.functions.revokeRole(
                                    role_hash, revoke_addr
                                ).build_transaction({
                                    'from': user_address,
                                    'nonce': nonce,
                                    'gas': 150000,
                                    'gasPrice': w3.eth.gas_price
                                })

                                signed_txn = w3.eth.account.sign_transaction(txn, private_key)
                                tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
                                receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

                                if receipt['status'] == 1:
                                    st.success(f"✓ {revoke_role} revoked!")
                                else:
                                    st.error("Failed")
                        except Exception as e:
                            st.error(f"Error: {e}")

# =============================================================================
# FOOTER
# =============================================================================
st.sidebar.markdown("---")
st.sidebar.caption(f"Contract: [{CONTRACT_ADDRESS[:10]}...](https://amoy.polygonscan.com/address/{CONTRACT_ADDRESS})" if CONTRACT_ADDRESS else "No contract")
st.sidebar.caption("FoodSafe v1.0 | Polygon Amoy")
