# supplychain
# FoodRecallSystem

Lot-level traceability on Ethereum/Polygon to enable **surgical food recalls**. Each batch is an ERC-721 token with on-chain custody, status events, and a regulator-controlled recall switch. IPFS stores certificates/attachments; events power the UI & audits.

> **Why:** Current recalls are slow and broad. Lot-level blockchain provenance enables fast, narrow recalls that protect public health while reducing waste and cost.
> Refs: Course Project 1 brief & resources (Remix, MetaMask, Polygon Amoy).  
> 
> - Proposal: surgical recalls, Ethereum + Solidity, OZ ERC-721, IPFS. 
> - Course setup: MetaMask, Polygon Amoy Testnet, Faucet, Remix & Solidity docs.

---

## Architecture (High Level)

**Stakeholders & Roles**
- Producer: registers new lots (batches) → `PRODUCER_ROLE`
- Distributor: updates custody in transit, marks on-shelf → `DISTRIBUTOR_ROLE`
- Regulator: issues recalls → `REGULATOR_ROLE`

**On-chain (Solidity) - FoodSafe Contract**
- ERC-721 token per lot (tokenId)
- Three status states: `InTransit`, `OnShelf`, `Recalled`
- Events: `Transfer` (ERC-721 standard), `LotRecalled`
- RBAC via OpenZeppelin `AccessControl`
- Minimal on-chain storage + event-first design
- History entries stored as array with IPFS hashes

**Backend (Python/FastAPI)**
- Event indexer listens to blockchain events and stores in PostgreSQL
- RESTful API serves lot data, history, and recall information to frontend
- IPFS service handles file uploads via Pinata
- Web3 integration for real-time blockchain queries

**Off-chain Storage**
- IPFS (via Pinata) for certificates, sensor logs, shipping manifests
- PostgreSQL indexes blockchain events for fast queries
- Frontend (React/Next.js) consumes backend API + direct blockchain interaction via Ethers

---

## Features
- Lot registration (producer-only) with IPFS metadata
- Custody transfer via NFT ownership
- Status tracking: `InTransit` → `OnShelf` → `Recalled`
- Audit trail with history entries (on-chain + IPFS)
- Regulator recall at individual lot granularity
- Real-time event indexing to database
- RESTful API for querying lot data and history

---

## Technology Stack

**Smart Contracts**
- Solidity ^0.8.20
- Hardhat (development & deployment)
- OpenZeppelin Contracts (ERC-721, AccessControl)
- Polygon Amoy Testnet

**Backend**
- Python 3.9+
- FastAPI (REST API)
- Web3.py (blockchain integration)
- SQLAlchemy + PostgreSQL (event indexing)
- Pinata (IPFS pinning service)

**Frontend**
- React with Next.js
- Ethers.js / Wagmi (blockchain interaction)
- MetaMask integration

---

## Project Structure

```
supplychain/
├── backend/              # Python FastAPI backend
│   ├── blockchain.py     # Web3 integration
│   ├── config.py         # Environment configuration
│   ├── database.py       # SQLAlchemy models
│   ├── indexer.py        # Event listener/indexer
│   ├── ipfs_service.py   # Pinata IPFS integration
│   ├── main.py           # FastAPI application
│   ├── requirements.txt  # Python dependencies
│   └── .env.example      # Environment template
├── frontend/             # React Next.js frontend (TBD)
├── smart-contracts/      # Hardhat project (TBD)
└── message.txt           # FoodSafe.sol draft contract
```

---

## Setup Instructions

### Prerequisites
- Node.js ≥ 18
- Python ≥ 3.9
- PostgreSQL
- MetaMask browser extension
- Pinata account (for IPFS)
- Polygon Amoy testnet RPC URL (Alchemy/Infura)

### 1. Smart Contracts Setup

```bash
cd smart-contracts
npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox
npm install @openzeppelin/contracts dotenv
npx hardhat init
```

Move the FoodSafe contract:
```bash
mv ../message.txt contracts/FoodSafe.sol
```

Configure Polygon Amoy in `hardhat.config.js` and deploy:
```bash
npx hardhat compile
npx hardhat test
npx hardhat run scripts/deploy.js --network amoy
```

### 2. Backend Setup

**Step 1: Install Dependencies**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -r requirements.txt
```

**Step 2: Configure Environment**

Copy `.env.example` to `.env` and fill in your values:
```bash
cp .env.example .env
```

Edit `.env` with:
- PostgreSQL connection URL
- Polygon Amoy RPC URL (from Alchemy/Infura)
- Deployed FoodSafe contract address
- Pinata API credentials

**Step 3: Initialize Database**

Create PostgreSQL database:
```bash
psql -U postgres
CREATE DATABASE foodsafe_db;
\\q
```

Database tables will be auto-created on first run.

**Step 4: Run the Backend**

Terminal 1 - Event Indexer (listens to blockchain):
```bash
python indexer.py
```

Terminal 2 - API Server:
```bash
uvicorn main:app --reload
```

API will be available at `http://localhost:8000`
API docs at `http://localhost:8000/docs`

### 3. Frontend Setup (Coming Soon)

```bash
cd frontend
npm install
npm run dev
```

---

## API Endpoints

Once the backend is running, the following endpoints are available:

**Lot Management**
- `GET /lots` - List all lots (paginated)
- `GET /lots/{token_id}` - Get specific lot details
- `GET /lots/{token_id}/history` - Get lot audit trail
- `GET /lots/owner/{address}` - Get lots by owner address
- `GET /lots/{token_id}/recalled` - Check recall status

**Recalls**
- `GET /recalls` - List all recall events

**IPFS**
- `POST /upload` - Upload file to IPFS
- `POST /upload-json` - Upload JSON data to IPFS

**System**
- `GET /` - Health check
- `GET /blockchain/status` - Check blockchain connection
- `GET /stats` - System statistics

Interactive API documentation: `http://localhost:8000/docs`
