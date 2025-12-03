# FoodSafe Project Setup Instructions

Complete guide to setting up and running the FoodSafe blockchain food traceability system.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Getting Contract Deployment Information](#getting-contract-deployment-information)
3. [Backend Setup](#backend-setup)
4. [Frontend Setup](#frontend-setup)
5. [Running the System](#running-the-system)
6. [Assigning Roles](#assigning-roles)
7. [Testing the System](#testing-the-system)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting, ensure you have:

- [ ] **Node.js** (v18+) installed
- [ ] **Python** (v3.9+) installed
- [ ] **PostgreSQL** (v12+) installed and running
- [ ] **Alchemy Account** with Polygon Amoy RPC URL
- [ ] **Pinata Account** with API keys
- [ ] **MetaMask Wallet** with test MATIC tokens
- [ ] **Contract Already Deployed** to Polygon Amoy

### Get Test MATIC
Visit https://faucet.polygon.technology/ to get free testnet MATIC for Polygon Amoy.

---

## Getting Contract Deployment Information

**IMPORTANT:** The smart contract is already deployed. You need to obtain the following information from your teammate who deployed it:

### Required Information:
1. **CONTRACT_ADDRESS** - The deployed contract address (e.g., `0xAbC123...`)
2. **DEPLOYER_ADDRESS** - Address that deployed the contract (has DEFAULT_ADMIN_ROLE)
3. **REGULATOR_ADDRESS** - Address assigned REGULATOR_ROLE during deployment
4. **Deployment Block Number** - For indexer to start scanning from
5. **Deployment Transaction Hash** - To verify on PolygonScan

### How to Get This Information:

Ask your teammate to provide:
```bash
# From their deployment output or from PolygonScan
Contract Address: 0x...
Deployer Address: 0x...
Deployment Block: 12345678
Deployment TX: 0x...
```

Verify the contract on PolygonScan:
```
https://amoy.polygonscan.com/address/CONTRACT_ADDRESS
```

---

## Backend Setup

### Step 1: Navigate to Backend Directory
```bash
cd /Users/maburande/ASU/supplychain/backend
```

### Step 2: Create Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Setup PostgreSQL Database
```bash
# Check PostgreSQL is running
pg_isready

# Create database
createdb foodsafe_db

# If you need to set a password for postgres user:
psql postgres
# Then in psql: ALTER USER postgres WITH PASSWORD 'your_password';
```

### Step 5: Configure Environment Variables

Edit `/Users/maburande/ASU/supplychain/backend/.env` with actual values:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/foodsafe_db

# Blockchain Configuration
POLYGON_AMOY_RPC_URL=https://polygon-amoy.g.alchemy.com/v2/YOUR_ALCHEMY_API_KEY
CONTRACT_ADDRESS=YOUR_DEPLOYED_CONTRACT_ADDRESS

# IPFS Configuration
PINATA_API_KEY=your_pinata_api_key
PINATA_SECRET_API_KEY=your_pinata_secret_api_key
```

**Where to get these values:**
- **POLYGON_AMOY_RPC_URL**: Sign up at https://www.alchemy.com/, create a Polygon Amoy app, copy the HTTPS URL
- **CONTRACT_ADDRESS**: Get from teammate (see section above)
- **Pinata Keys**: Sign up at https://pinata.cloud/, go to API Keys section

### Step 6: Initialize Database
```bash
python -c "from database import init_db; init_db()"
```

You should see:
```
✅ Database initialized successfully
```

### Step 7: Verify Setup
```bash
python test_setup.py
```

All checks should pass:
```
✅ Database connection: OK
✅ Blockchain connection: OK
✅ Contract ABI loaded: OK
✅ Contract accessible: OK
```

---

## Frontend Setup

### Step 1: Navigate to Frontend Directory
```bash
cd /Users/maburande/ASU/supplychain/frontend
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Secrets

Edit `/Users/maburande/ASU/supplychain/frontend/.streamlit/secrets.toml` with actual values:

```toml
[blockchain]
POLYGON_AMOY_RPC_URL = "https://polygon-amoy.g.alchemy.com/v2/YOUR_ALCHEMY_API_KEY"
CONTRACT_ADDRESS = "YOUR_DEPLOYED_CONTRACT_ADDRESS"

[api]
API_URL = "http://localhost:8000"

[ipfs]
PINATA_API_KEY = "your_pinata_api_key"
PINATA_SECRET_API_KEY = "your_pinata_secret_api_key"
```

**Use the same values as backend .env**

---

## Running the System

You need **3 terminal windows** open:

### Terminal 1: Event Indexer
```bash
cd /Users/maburande/ASU/supplychain/backend
source venv/bin/activate
python indexer.py
```

You should see:
```
🔗 Connected to Polygon Amoy Testnet
📄 Contract: 0xYourContractAddress
🔍 Starting event indexer...
⏳ Polling for events every 5 seconds...
```

**Keep this running!** It listens for blockchain events and updates the database.

### Terminal 2: FastAPI Backend
```bash
cd /Users/maburande/ASU/supplychain/backend
source venv/bin/activate
uvicorn main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

Verify at: http://localhost:8000/docs

### Terminal 3: Streamlit Frontend
```bash
cd /Users/maburande/ASU/supplychain/frontend
streamlit run streamlit_app.py
```

You should see:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

Open http://localhost:8501 in your browser.

---

## Assigning Roles

### Option 1: Using Streamlit Admin Dashboard

1. Open Streamlit at http://localhost:8501
2. In sidebar, enter **DEPLOYER_ADDRESS** (the address that deployed the contract)
3. Enable "Transaction Signing" checkbox
4. Enter the deployer's **private key** (⚠️ ONLY USE TEST WALLETS!)
5. Select **Admin** from dashboard dropdown
6. Use the "Grant Role" form to assign roles to addresses

### Option 2: Using Hardhat Script (Recommended for Multiple Addresses)

1. Edit `/Users/maburande/ASU/supplychain/smart-contract/scripts/assign-roles.js`
2. Replace placeholder addresses with actual test addresses:
   ```javascript
   const TEST_ADDRESSES = {
     producers: [
       "0xYourProducerAddress1",
       "0xYourProducerAddress2",
     ],
     distributors: [
       "0xYourDistributorAddress1",
     ],
     // ... etc
   };
   ```

3. Set environment variable:
   ```bash
   export CONTRACT_ADDRESS=0xYourDeployedContractAddress
   ```

4. Run the script:
   ```bash
   cd /Users/maburande/ASU/supplychain/smart-contract
   npx hardhat run scripts/assign-roles.js --network amoy
   ```

**Note:** The script must be run by an address with DEFAULT_ADMIN_ROLE (usually the deployer).

---

## Testing the System

### End-to-End Test Flow

#### 1. Check System Status
- In Streamlit, select **System Status** dashboard
- Verify all services are green (✓):
  - Backend API responding
  - Blockchain connected
  - Contract loaded
  - Pinata configured

#### 2. Register a New Lot (Producer)
- Select **Producer** dashboard
- Enter producer's wallet address in sidebar
- Enable transaction signing, enter private key
- Fill in the form:
  - Product Name: "Organic Lettuce Lot 001"
  - Origin: "California Farm"
  - Upload a test file (or leave blank for auto-generated metadata)
- Click "Register Lot & Mint NFT"
- Wait for transaction confirmation
- Note the transaction hash and IPFS hash

#### 3. Verify Event Indexing
- Check **Terminal 1 (indexer)**
- You should see:
  ```
  ✅ New event: LotRegistered
     Lot ID: 1
     Product: Organic Lettuce Lot 001
  ```

#### 4. View Lot in Regulator Dashboard
- Select **Regulator** dashboard
- Verify the new lot appears in the table
- Click "Select Lot ID for History"
- View the audit trail (should show 1 entry: Created)

#### 5. Update Lot Status (Distributor)
- Select **Distributor** dashboard
- Enter distributor's wallet address
- Enable transaction signing
- Update Lot ID 1 to "InTransit"
- Optionally upload a temperature log
- Submit transaction

#### 6. Verify Update
- Check **Regulator** dashboard again
- Lot should show status "InTransit"
- History should show 2 entries: Created → InTransit

#### 7. Trigger Recall (Regulator)
- Select **Regulator** dashboard
- Enter regulator's wallet address
- In "Trigger Surgical Recall" form, enter Lot ID 1
- Submit recall transaction
- Verify lot status changes to "Recalled"

#### 8. Check API Endpoints
Visit http://localhost:8000/docs and test:
- `GET /lots` - Should return all lots
- `GET /lots/1` - Should return lot details
- `GET /lots/1/history` - Should return full history
- `GET /blockchain/status` - Should show connected status

---

## Troubleshooting

### Backend Issues

#### Database Connection Error
```
Error: could not connect to server
```
**Solution:**
1. Check PostgreSQL is running: `pg_isready`
2. Verify DATABASE_URL in `.env`
3. Ensure database exists: `psql -l | grep foodsafe_db`

#### Contract ABI Error
```
Error loading contract ABI
```
**Solution:**
1. Verify `contract_abi.json` exists in backend directory
2. Check file is valid JSON: `python -m json.tool contract_abi.json`

#### Blockchain Connection Error
```
Error: Could not connect to Polygon Amoy
```
**Solution:**
1. Verify POLYGON_AMOY_RPC_URL is correct in `.env`
2. Check Alchemy dashboard for rate limits
3. Test RPC URL: `curl -X POST YOUR_RPC_URL -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'`

### Frontend Issues

#### Web3 Not Initialized
```
⚠ Web3 not initialized
```
**Solution:**
1. Check `secrets.toml` has correct POLYGON_AMOY_RPC_URL
2. Restart Streamlit after editing secrets
3. Verify RPC URL is not rate-limited

#### Contract Not Loaded
```
✗ Contract not loaded
```
**Solution:**
1. Verify CONTRACT_ADDRESS in `secrets.toml`
2. Ensure address is checksummed (mixed case)
3. Verify contract exists on PolygonScan

#### Transaction Failed
```
Transaction failed: execution reverted
```
**Solution:**
1. Check user has required role (use Admin dashboard)
2. Verify sufficient MATIC balance for gas
3. Check transaction on PolygonScan for specific error
4. Ensure lot ID exists (for update/recall operations)

### Indexer Issues

#### No Events Being Captured
**Solution:**
1. Check indexer is running in Terminal 1
2. Verify CONTRACT_ADDRESS in backend `.env`
3. Check the `last_indexed_block` in database:
   ```sql
   psql foodsafe_db
   SELECT * FROM indexer_state;
   ```
4. Manually reset indexer if needed (will re-scan from deployment block)

#### Duplicate Events
**Solution:**
1. Stop indexer
2. Clear duplicates:
   ```sql
   DELETE FROM lot_history WHERE id NOT IN (
     SELECT MIN(id) FROM lot_history GROUP BY tx_hash, event_type
   );
   ```
3. Restart indexer

---

## Getting Deployment Information from Teammate

Use this template to request info:

```
Hi [Teammate],

I need the following information about the deployed FoodTraceability contract:

1. Contract Address: 0x...
2. Deployer Address (has admin role): 0x...
3. Regulator Address (if assigned): 0x...
4. Deployment Block Number: ...
5. Deployment Transaction Hash: 0x...
6. Network: Polygon Amoy Testnet

Also, can you provide:
- The actual role hashes (PRODUCER_ROLE, DISTRIBUTOR_ROLE, etc.)
- Any addresses that already have roles assigned

Thanks!
```

---

## Next Steps

Once everything is set up:

1. **Assign Roles** - Use Admin dashboard or Hardhat script to assign roles to test addresses
2. **Test Complete Flow** - Follow the end-to-end test above
3. **Monitor Logs** - Keep all 3 terminals visible to watch event flow
4. **Verify on PolygonScan** - Check all transactions on https://amoy.polygonscan.com/

---

## Quick Reference Commands

### Start All Services
```bash
# Terminal 1
cd backend && source venv/bin/activate && python indexer.py

# Terminal 2
cd backend && source venv/bin/activate && uvicorn main:app --reload

# Terminal 3
cd frontend && streamlit run streamlit_app.py
```

### Check Status
```bash
# Database
psql foodsafe_db -c "SELECT COUNT(*) FROM food_lots;"

# Backend API
curl http://localhost:8000/blockchain/status

# Get all lots
curl http://localhost:8000/lots
```

### View Logs
```bash
# PostgreSQL logs (macOS)
tail -f /usr/local/var/log/postgresql@14.log

# Python errors (if services crash, check terminal output)
```

---

## Support

If you encounter issues:
1. Check the **Troubleshooting** section above
2. Review terminal logs for error messages
3. Verify all configuration values are correct
4. Check PolygonScan for transaction details
5. Ensure all prerequisites are met

---

**Last Updated:** 2025-12-02
**Version:** 1.0
