# FoodSafe: Blockchain Food Safety and Recall System

## Description

**FoodSafe** addresses critical flaws in traditional food supply chains. When contamination (like _E. coli_ or _Salmonella_) occurs, tracing the source can take **days or weeks**, leading to dangerous _blanket recalls_ that waste safe food and damage consumer trust.

**FoodSafe** is a **blockchain-based traceability system** enabling **surgical recalls**. By maintaining an **immutable, lot-level ledger** of a food product's journey from farm to shelf, the system allows regulators to trace contamination sources in seconds — and recall **only the affected batches**.

### System Benefits

- **Complete Traceability:** Full visibility from producer to retailer
- **Real-Time Transparency:** Instant access for authorized stakeholders
- **Rapid Recalls:** Smart contracts instantly flag and notify stakeholders of recalled batches
- **Immutable Records:** Ensures data integrity and compliance with food safety regulations

---

## Architecture

FoodSafe uses a **three-tier architecture** to ensure scalability, performance, and user experience:

### Layer 1: Smart Contracts (Blockchain)

- **FoodTraceability.sol** — ERC-721 contract on **Polygon Amoy Testnet**
- Each food lot is a unique NFT (tokenId)
- Four status states: `Created`, `InTransit`, `OnShelf`, `Recalled`
- Role-based access control (PRODUCER, DISTRIBUTOR, RETAILER, REGULATOR)
- Emits events: `LotRegistered`, `LotStatusUpdated`, `LotRecalled`, `Transfer`
- Stores minimal on-chain data; history entries reference IPFS hashes

### Layer 2: Backend (API & Indexer)

- **FastAPI** REST API serves lot data to frontend
- **Event Indexer** listens to blockchain events and stores them in PostgreSQL
- **Web3.py** integration for real-time blockchain queries
- **Pinata** service handles IPFS file uploads/retrieval
- Database models: `Lot`, `HistoryEntry`, `RecallEvent`

### Layer 3: Frontend (DApp) - Coming Soon

- **React/Next.js** web application
- **MetaMask** integration for wallet connectivity
- **Wagmi/RainbowKit** for Web3 interactions
- Role-based dashboards for producers, distributors, and regulators

### Data Flow

1. **Producer** registers lot via MetaMask → FoodSafe contract mints NFT
2. **Indexer** detects event → stores in PostgreSQL
3. **API** serves indexed data to frontend
4. **Distributor** updates lot status → emits event → indexer updates DB
5. **Regulator** triggers recall → contract marks lot as recalled → notifications sent

---

## Technology Stack

### Smart Contracts

- **Solidity** `^0.8.20` — Smart contract language
- **Hardhat** — Development, testing, and deployment framework
- **OpenZeppelin Contracts** — ERC-721, AccessControl implementations
- **Polygon Amoy Testnet** — Layer 2 scaling solution

### Backend

- **Python** `3.9+` — Backend programming language
- **FastAPI** — High-performance REST API framework
- **Web3.py** — Ethereum blockchain interaction
- **SQLAlchemy** — ORM for database operations
- **PostgreSQL** — Relational database for event indexing
- **Pinata** — IPFS pinning service for off-chain storage

### Frontend (Coming Soon)

- **React** with **Next.js** — Web framework
- **Wagmi** / **RainbowKit** — Blockchain interaction
- **MetaMask** — Wallet connectivity

---

## Project Structure

```
supplychain/
├── backend/                   # Python FastAPI Backend ✅ COMPLETE
│   ├── blockchain.py          # Web3 integration with smart contract
│   ├── config.py              # Environment configuration
│   ├── database.py            # SQLAlchemy models (Lot, HistoryEntry, RecallEvent)
│   ├── indexer.py             # Event listener/indexer service
│   ├── ipfs_service.py        # Pinata IPFS integration
│   ├── main.py                # FastAPI REST API application
│   ├── contract_abi.json      # Smart contract ABI
│   ├── test_setup.py          # Automated setup verification
│   ├── requirements.txt       # Python dependencies
│   └── .env.example           # Environment variables template
├── smart-contracts/           # Hardhat project (to be initialized)
│   └── FoodTraceability.sol   # Main smart contract
├── frontend/                  # React Next.js frontend (to be implemented)
├── artifacts/                 # Compiled contract artifacts
├── PROJECT_STATUS.md          # Current implementation status
└── README.md                  # This file
```

---

## Quick Start

### Prerequisites

- **Node.js** ≥ 18
- **Python** ≥ 3.9
- **PostgreSQL** database
- **MetaMask** browser extension
- **Pinata** account for IPFS ([Sign up here](https://pinata.cloud))
- **Polygon Amoy** RPC URL from [Alchemy](https://www.alchemy.com/) or [Infura](https://infura.io/)

### 1. Backend Setup

#### Step 1: Install Dependencies

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Step 2: Set Up PostgreSQL Database

```bash
# Login to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE foodsafe_db;

# Exit
\q
```

#### Step 3: Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:your_password@localhost/foodsafe_db

# Blockchain Configuration
POLYGON_AMOY_RPC_URL=https://rpc-amoy.polygon.technology/
CONTRACT_ADDRESS=0xYourDeployedContractAddress

# IPFS/Pinata Configuration
PINATA_API_KEY=your_pinata_api_key_here
PINATA_SECRET_API_KEY=your_pinata_secret_api_key_here
```

**Getting Pinata API Keys:**

1. Sign up at [https://pinata.cloud](https://pinata.cloud)
2. Go to API Keys section
3. Create a new API key with permissions: `pinFileToIPFS`, `pinJSONToIPFS`, `unpin`
4. Copy the API Key and Secret API Key to your `.env` file

#### Step 4: Initialize Database Tables

```bash
python -c "from database import init_db; init_db()"
```

#### Step 5: Verify Setup

Run the automated setup verification:

```bash
python test_setup.py
```

This will check:

- ✅ Package imports
- ✅ Environment configuration
- ✅ Database connection
- ✅ Blockchain connection
- ✅ Contract ABI
- ✅ IPFS/Pinata authentication

#### Step 6: Run the Backend Services

The backend consists of two services that should run simultaneously:

**Terminal 1 - Event Indexer:**

```bash
python indexer.py
```

Expected output:

```
============================================================
Starting FoodSafe Event Indexer
============================================================
Blockchain connected: True
Contract address: 0x...
Starting from block: 0
Polling interval: 5 seconds
============================================================
```

**Terminal 2 - API Server:**

```bash
uvicorn main:app --reload
```

Expected output:

```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
Blockchain connected: True
```

The API will be available at:

- **API Base:** `http://localhost:8000`
- **Interactive Docs:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`


## Off-chain Storage

- IPFS (via Pinata) for certificates, sensor logs, shipping manifests
- PostgreSQL indexes blockchain events for fast queries
- Frontend (React/Next.js) consumes backend API and can interact directly with the blockchain via Ethers.js
- **Complete Traceability:** Full visibility from producer to retailer.  
- **Real-Time Transparency:** Instant access for authorized stakeholders.  
- **Rapid Recalls:** Smart contracts instantly flag and notify stakeholders of recalled batches.  
- **Immutable Records:** Ensures data integrity and compliance with food safety regulations.

This project uses the **Hardhat** environment for Ethereum smart contract development.


### 2. Smart Contract Setup (To Be Completed)

```bash
cd smart-contracts
npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox
npm install @openzeppelin/contracts dotenv
npx hardhat init
```

Configure Polygon Amoy in `hardhat.config.js` and deploy:

```bash
npx hardhat compile
npx hardhat test
npx hardhat run scripts/deploy.js --network amoy
```

### 3. Frontend Setup (To Be Implemented)

```bash
cd frontend
npm install
npm run dev
```

---

## API Endpoints

Once the backend is running, the following REST endpoints are available:

### Lot Management

- `GET /lots` — List all lots (paginated with skip/limit)
- `GET /lots/{token_id}` — Get specific lot details from database
- `GET /lots/{token_id}/history` — Get complete audit trail for a lot
- `GET /lots/{token_id}/blockchain` — Get lot details directly from blockchain
- `GET /lots/owner/{address}` — Get all lots owned by an Ethereum address
- `GET /lots/{token_id}/recalled` — Check if a lot is recalled

### Recalls

- `GET /recalls` — List all recall events (paginated, most recent first)

### IPFS

- `POST /upload` — Upload file to IPFS (returns IPFS hash)
- `POST /upload-json` — Upload JSON data to IPFS
- `GET /ipfs/{ipfs_hash}` — Retrieve content from IPFS

### System

- `GET /` — Health check
- `GET /blockchain/status` — Check blockchain connection status
- `GET /stats` — Get system statistics (total lots, recalls, lots by status)

**Interactive Documentation:** Visit `http://localhost:8000/docs` for Swagger UI with full API documentation and testing interface.

---

## Testing the API

### Health Check

```bash
curl http://localhost:8000/
```

Expected response:

```json
{
  "status": "ok",
  "service": "FoodSafe API"
}
```

### Check Blockchain Connection

```bash
curl http://localhost:8000/blockchain/status
```

### Get System Statistics

```bash
curl http://localhost:8000/stats
```

### Upload JSON to IPFS

```bash
curl -X POST http://localhost:8000/upload-json \
  -H "Content-Type: application/json" \
  -d '{"product": "Tomatoes", "origin": "Farm A", "harvest_date": "2024-01-01"}'
```

### Get Lot Details

```bash
curl http://localhost:8000/lots/1
```

---

## Smart Contract Overview

The `FoodTraceability.sol` smart contract implements the core on-chain logic for the FoodSafe system using **OpenZeppelin's AccessControl** and **ERC-721 standards**.

### Roles & Permissions

| Role                 | Description                                    | Capabilities                            |
| -------------------- | ---------------------------------------------- | --------------------------------------- |
| `DEFAULT_ADMIN_ROLE` | Super-admin, manages all roles                 | Can grant/revoke roles                  |
| `PRODUCER_ROLE`      | Assigned to farmers or factories               | Register new food lots                  |
| `DISTRIBUTOR_ROLE`   | Assigned to logistics or shipping partners     | Add tracking history, update lot status |
| `RETAILER_ROLE`      | Assigned to retailers                          | Mark lots as on-shelf                   |
| `REGULATOR_ROLE`     | Assigned to regulatory authorities (e.g., FDA) | Trigger recalls and view all data       |

### Key Functions

- `registerLot(productName, origin, ipfsHash)` — Producer creates new lot, mints NFT
- `updateLot(lotId, ipfsHash, newStatus)` — Update lot status and add history entry
- `triggerRecall(lotId)` — Regulator initiates recall
- `getLot(lotId)` — View complete lot information
- `getLotHistory(lotId)` — View complete audit trail
- `assignDistributor(address)` — Grant distributor role
- `assignRetailer(address)` — Grant retailer role

### Events

- `LotRegistered(lotId, productName, producer)` — Emitted when new lot is created
- `LotStatusUpdated(lotId, newStatus, ipfsHash, updater)` — Emitted on status changes
- `LotRecalled(lotId, regulator)` — Emitted when recall is triggered
- `Transfer(from, to, tokenId)` — Standard ERC-721 transfer event

---

## Troubleshooting

### Database Connection Failed

**Solution:** Ensure PostgreSQL is running and the DATABASE_URL is correct:

```bash
# Check if PostgreSQL is running
pg_isready

# Test connection
psql postgresql://postgres:password@localhost/foodsafe_db
```

### Blockchain Not Connected

**Solution:**

- Verify the RPC URL is correct and accessible
- Check if Polygon Amoy testnet is operational
- Try alternative RPC URLs:
  - `https://rpc-amoy.polygon.technology/`
  - `https://polygon-amoy.g.alchemy.com/v2/YOUR_KEY`

### IPFS Upload Failed

**Solution:**

- Verify Pinata API keys are correct
- Check Pinata account status and limits
- Test connection via the `/docs` endpoint

### No Events Being Indexed

**Solution:**

- Ensure the contract address is correct
- Check if there are any transactions on the contract
- Verify the contract ABI matches the deployed contract
- Look at indexer logs for errors

### Resetting the Database

If you need to start fresh:

```bash
# Drop and recreate database
dropdb foodsafe_db
createdb foodsafe_db

# Reinitialize tables
python -c "from database import init_db; init_db()"
```

---

## Development Tips

### Viewing Logs

The indexer prints detailed logs:

```
[2024-11-20 12:00:00] Indexing blocks 100 to 150
Indexed LotRegistered event for lot 1
Indexed Transfer event for lot 1
Successfully indexed blocks 100 to 150
```

### Database Queries

Access the database directly:

```bash
psql postgresql://postgres:password@localhost/foodsafe_db

# View all lots
SELECT * FROM lots;

# View history entries
SELECT * FROM history_entries ORDER BY timestamp DESC LIMIT 10;

# View recalls
SELECT * FROM recall_events;
```

---

## Production Deployment

For production deployment, consider:

1. **Use a production-grade server:** Gunicorn or Hypercorn instead of uvicorn directly

   ```bash
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

2. **Set up HTTPS:** Use nginx as reverse proxy with SSL certificates

3. **Environment variables:** Use proper secret management (AWS Secrets Manager, Vault)

4. **Database:** Use managed PostgreSQL (AWS RDS, Heroku Postgres)

5. **Monitoring:** Set up logging and monitoring (Sentry, CloudWatch)

6. **Auto-restart:** Use systemd or supervisor for the indexer service

7. **CORS:** Restrict allowed origins in production

8. **Rate limiting:** Add API rate limiting

---

## Project Status

**Phase 1 (Smart Contracts):** 30% Complete

- ✅ Smart contract written and compiled
- ❌ Hardhat project initialization
- ❌ Deployment scripts
- ❌ Test suite

**Phase 2 (Backend):** 100% Complete ✅

- ✅ All blockchain integration functions
- ✅ IPFS/Pinata service
- ✅ Event indexer with all event handlers
- ✅ REST API with 14 endpoints
- ✅ Database models and setup
- ✅ Environment configuration
- ✅ Setup verification script

**Phase 3 (Frontend):** 0% Complete

- ❌ Next.js project initialization
- ❌ Web3 wallet integration
- ❌ Role-based dashboards

For detailed implementation status, see [PROJECT_STATUS.md](PROJECT_STATUS.md).

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)

---

## Support

For issues or questions:

1. Check the logs from both indexer and API server
2. Verify all environment variables are set correctly
3. Ensure smart contract is deployed and accessible
4. Run `python test_setup.py` to verify configuration
5. Check the [PROJECT_STATUS.md](PROJECT_STATUS.md) for known issues and limitations
