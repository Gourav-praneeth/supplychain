import streamlit as st
import requests
import pandas as pd

# 1. Configuration
API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="FoodSafe Traceability DApp",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. API Helper Functions (Client-side)
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

# 3. Main Application Logic
st.sidebar.title("👤 Role Selection")
role = st.sidebar.selectbox(
    "Select your Stakeholder Role:",
    ["Regulator", "Distributor", "Producer", "System Status"]
)

st.title(f"🛡️ FoodSafe: {role} Dashboard")

# --- Content based on Role ---

if role == "System Status":
    st.header("System Health")
    try:
        status_res = requests.get(f"{API_URL}/blockchain/status")
        st.json(status_res.json())
        st.success("FastAPI and Blockchain Service are responding.")
    except Exception:
        st.error("Cannot connect to FastAPI or Blockchain service. Ensure both are running.")

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
        with st.form("recall_form"):
            lot_id_to_recall = st.number_input("Lot ID to Recall (Token ID)", min_value=1, step=1, key="recall_lot_id")
            submitted = st.form_submit_button("🚨 TRIGGER RECALL (Smart Contract TX)")

            if submitted:
                st.warning(f"Simulating Smart Contract transaction for lot **#{lot_id_to_recall}**...")
                st.info("The indexer (running in another terminal) will detect the LotRecalled event and update the database.")
                
                st.success(f"Recall for Lot #{lot_id_to_recall} successfully submitted to the Polygon Amoy Testnet.")

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
    st.warning("This requires a **MetaMask** transaction using an address with `PRODUCER_ROLE`.")

    with st.form("register_lot_form"):
        product_name = st.text_input("Product Name (e.g., 'Organic Lettuce Lot 42')")
        origin = st.text_input("Origin Location")
        # In a real app, Producer uploads a file (manifest/certificate)
        uploaded_file = st.file_uploader("Upload Initial Metadata/Certificate (IPFS)", type=["json", "pdf"])

        submitted = st.form_submit_button("✅ Register Lot & Mint NFT")

        if submitted and product_name and origin and uploaded_file:
            st.info("Simulating IPFS upload...")
            st.write("---")
            
            st.info(f"1. IPFS Hash created: **Qm... (simulated)**")
            st.info("2. Triggering **`registerLot`** Smart Contract TX via MetaMask.")
            st.success("New Lot NFT minted. Check Regulator dashboard shortly.")

elif role == "Distributor":
    st.header("Update Lot Custody and Status")
    st.warning("This requires a **MetaMask** transaction using an address with `DISTRIBUTOR_ROLE`.")
    
    with st.form("update_lot_form"):
        lot_id = st.number_input("Lot ID to Update", min_value=1, step=1)
        new_status = st.selectbox(
            "New Status:",
            ["InTransit", "OnShelf"]
        )
        new_ipfs_hash = st.text_input("New IPFS Hash (e.g., Temperature Log)")

        submitted = st.form_submit_button("🔄 Update Lot Status")
        if submitted and lot_id > 0:
            st.info(f"Triggering **`updateLot`** Smart Contract TX for Lot #{lot_id} to status **{new_status}**.")
            st.success("Lot status update submitted.")