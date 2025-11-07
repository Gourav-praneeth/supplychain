# FoodSafe: Blockchain Food Safety and Recall System

## Description

**FoodSafe** addresses critical flaws in traditional food supply chains.  
When contamination (like *E. coli* or *Salmonella*) occurs, tracing the source can take **days or weeks**, leading to dangerous *blanket recalls* that waste safe food and damage consumer trust.

**FoodSafe** is a **blockchain-based traceability system** enabling **surgical recalls**.  
By maintaining an **immutable, lot-level ledger** of a food product’s journey from farm to shelf, the system allows regulators to trace contamination sources in seconds — and recall **only the affected batches**.

### System Benefits
- **Complete Traceability:** Full visibility from producer to retailer.
- **Real-Time Transparency:** Instant access for authorized stakeholders.
- **Rapid Recalls:** Smart contracts instantly flag and notify stakeholders of recalled batches.
- **Immutable Records:** Ensures data integrity and compliance with food safety regulations.

---

## Architecture

FoodSafe uses a **three-tier architecture** to ensure scalability, performance, and user experience:

### Layer 1: Smart Contracts (Blockchain)
- **FoodSafe.sol** — ERC-721 contract on **Polygon Amoy Testnet**
- Each food lot is a unique NFT (tokenId)
- Three status states: `InTransit`, `OnShelf`, `Recalled`
- Role-based access control (PRODUCER, DISTRIBUTOR, REGULATOR)
- Emits events: `Transfer`, `LotRecalled`
- Stores minimal on-chain data; history entries reference IPFS hashes

### Layer 2: Backend (API & Indexer)
- **FastAPI** REST API serves lot data to frontend
- **Event Indexer** listens to blockchain events and stores them in PostgreSQL
- **Web3.py** integration for real-time blockchain queries
- **Pinata** service handles IPFS file uploads/retrieval
- Database models: `Lot`, `HistoryEntry`, `RecallEvent`

### Layer 3: Frontend (DApp)
- **React/Next.js** web application
- **MetaMask** integration for wallet connectivity
- **Ethers.js** for direct blockchain interaction
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
- **Ethers.js** / **Wagmi** — Blockchain interaction
- **MetaMask** — Wallet connectivity

---

## Project Structure

```
supplychain/
├── backend/                  # Python FastAPI Backend
│   ├── blockchain.py         # Web3 integration with FoodSafe contract
│   ├── config.py             # Environment configuration
│   ├── database.py           # SQLAlchemy models (Lot, HistoryEntry, RecallEvent)
│   ├── indexer.py            # Event listener/indexer service
│   ├── ipfs_service.py       # Pinata IPFS integration
│   ├── main.py               # FastAPI REST API application
│   ├── requirements.txt      # Python dependencies
│   └── .env.example          # Environment variables template
├── smart-contracts/          # Hardhat project (to be initialized)
├── frontend/                 # React Next.js frontend (to be implemented)
└── message.txt               # FoodSafe.sol draft contract
```

---

## Dependencies & Setup

**Stakeholders & Roles**
- Producer: registers new lots (batches) → `PRODUCER_ROLE`
- Distributor: updates custody in transit, marks on-shelf → `DISTRIBUTOR_ROLE`
- Regulator: issues recalls → `REGULATOR_ROLE`

### Prerequisites

- **Node.js** ≥ 18
- **Python** ≥ 3.9
- **PostgreSQL** database
- **MetaMask** browser extension
- **Pinata** account for IPFS
- **Polygon Amoy** RPC URL (Alchemy/Infura)

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

#### 1. Smart Contracts Setup

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

#### 2. Backend Setup

**Step 1: Install Dependencies**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Step 2: Configure Environment**

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
- `DATABASE_URL` — PostgreSQL connection string
- `POLYGON_AMOY_RPC_URL` — Your Alchemy/Infura RPC endpoint
- `CONTRACT_ADDRESS` — Deployed FoodSafe contract address
- `PINATA_API_KEY` — Pinata API key
- `PINATA_SECRET_API_KEY` — Pinata secret key

**Step 3: Initialize Database**

Create PostgreSQL database:
```bash
psql -U postgres
CREATE DATABASE foodsafe_db;
\q
```

Database tables will be auto-created when you first run the indexer or API.

**Step 4: Run the Backend**

Terminal 1 — Event Indexer (listens to blockchain):
```bash
python indexer.py
```

Terminal 2 — API Server:
```bash
uvicorn main:app --reload
```

The API will be available at:
- **API Base:** `http://localhost:8000`
- **Interactive Docs:** `http://localhost:8000/docs`

#### 3. Frontend Setup (Coming Soon)

```bash
cd frontend
npm install
npm run dev
```

---

## Off-chain Storage

- IPFS (via Pinata) for certificates, sensor logs, shipping manifests
- PostgreSQL indexes blockchain events for fast queries
- Frontend (React/Next.js) consumes backend API and can interact directly with the blockchain via Ethers.js
- **Complete Traceability:** Full visibility from producer to retailer.  
- **Real-Time Transparency:** Instant access for authorized stakeholders.  
- **Rapid Recalls:** Smart contracts instantly flag and notify stakeholders of recalled batches.  
- **Immutable Records:** Ensures data integrity and compliance with food safety regulations.

---

## Dependencies & Setup

This project uses the **Hardhat** environment for Ethereum smart contract development.

### Core Dependencies
- **Solidity:** Smart contract language (`v0.8.20+`)
- **Hardhat:** Development, testing, and deployment framework.
- **OpenZeppelin Contracts:** Secure, audited base contracts (ERC-721, AccessControl).
- **IPFS:** Off-chain storage for large files (e.g., IoT logs, production credentials).

### Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Gourav-praneeth/supplychain.git
   cd FoodSafe
   
2.  **Install Node.js dependencies:**
    npm install

3. **Install Hardhat and OpenZeppelin:**
   npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox
   npm install @openzeppelin/contracts

## API Endpoints

Once the backend is running, the following REST endpoints are available:

### Lot Management
- `GET /lots` — List all lots (paginated)
- `GET /lots/{token_id}` — Get specific lot details
- `GET /lots/{token_id}/history` — Get complete audit trail for a lot
- `GET /lots/owner/{address}` — Get all lots owned by an address
- `GET /lots/{token_id}/recalled` — Check if a lot is recalled

### Recalls
- `GET /recalls` — List all recall events (paginated)

### IPFS
- `POST /upload` — Upload file to IPFS (returns IPFS hash)
- `POST /upload-json` — Upload JSON data to IPFS

### System
- `GET /` — Health check
- `GET /blockchain/status` — Check blockchain connection status
- `GET /stats` — Get system statistics (total lots, recalls, etc.)

**Interactive Documentation:** Visit `http://localhost:8000/docs` for Swagger UI with full API documentation and testing interface.


## Draft Smart Contract — `FoodSafe.sol`

The `FoodSafe` smart contract implements the **core on-chain logic** for the FoodSafe system.  
It leverages **OpenZeppelin’s AccessControl** and **ERC-721 standards** to provide secure, role-based management and unique lot tracking on the blockchain.

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

### Roles & Permissions

| Role | Description | Capabilities |
|------|--------------|---------------|
| `DEFAULT_ADMIN_ROLE` | Super-admin, manages all roles. | Can grant/revoke roles. |
| `PRODUCER_ROLE` | Assigned to farmers or factories. | Register new food lots. |
| `DISTRIBUTOR_ROLE` | Assigned to logistics or shipping partners. | Add tracking history, mark lots as "On Shelf". |
| `REGULATOR_ROLE` | Assigned to regulatory authorities (e.g., FDA). | Trigger recalls and view all data. |



