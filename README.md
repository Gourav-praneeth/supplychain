# FoodSafe: Blockchain Food Safety and Recall System

[![Polygon Amoy](https://img.shields.io/badge/Network-Polygon%20Amoy-8247E5)](https://amoy.polygonscan.com/)
[![Smart Contract](https://img.shields.io/badge/Contract-Deployed-success)](https://amoy.polygonscan.com/address/0x2C6568f8567ba1020ce1D644eE6C15d5bA92A6f9)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## 🎯 Overview

**FoodSafe** is a **blockchain-based food traceability system** that enables **surgical recalls** by maintaining an **immutable, lot-level ledger** of food products from farm to shelf.

When contamination (like _E. coli_ or _Salmonella_) occurs, traditional systems take **days or weeks** to trace the source, leading to dangerous blanket recalls. FoodSafe allows regulators to trace contamination sources in **seconds** — recalling **only the affected batches**.

### ✨ Key Features

- **🔗 Complete Traceability** — Full visibility from producer to retailer
- **⚡ Real-Time Transparency** — Instant access for authorized stakeholders
- **🚨 Rapid Surgical Recalls** — Smart contracts instantly flag affected batches only
- **🔒 Immutable Records** — Blockchain ensures data integrity and compliance
- **📄 IPFS Integration** — Off-chain storage for certificates and documents

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Polygon Amoy Testnet                     │
│           FoodTraceability Smart Contract (ERC-721)         │
│           0x2C6568f8567ba1020ce1D644eE6C15d5bA92A6f9        │
└────────────────────────┬────────────────────────────────────┘
                         │ Web3.py
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
┌─────────────────┐            ┌─────────────────┐
│  Event Indexer  │            │   REST API      │
│  (indexer.py)   │            │   (FastAPI)     │
│   Port: N/A     │            │   Port: 8000    │
└────────┬────────┘            └────────┬────────┘
         │                               │
         └───────────┬───────────────────┘
                     ▼
         ┌──────────────────────┐
         │   PostgreSQL DB      │
         │   (foodsafe_db)      │
         └──────────────────────┘
                     │
                     ▼
         ┌──────────────────────┐
         │  Streamlit Frontend  │
         │     Port: 8501       │
         └──────────────────────┘

         ┌───────────────┐
         │ IPFS (Pinata) │◄──── Off-chain Storage
         └───────────────┘
```

---

## 🛠️ Technology Stack

| Layer                 | Technology                                |
| --------------------- | ----------------------------------------- |
| **Blockchain**        | Solidity ^0.8.20, Polygon Amoy Testnet    |
| **Smart Contract**    | ERC-721 NFT, OpenZeppelin AccessControl   |
| **Backend**           | Python 3.9+, FastAPI, Web3.py, SQLAlchemy |
| **Database**          | PostgreSQL                                |
| **Frontend**          | Streamlit (Python)                        |
| **Off-Chain Storage** | IPFS via Pinata                           |

---

## 📁 Project Structure

```
supplychain/
├── backend/                      # Python FastAPI Backend
│   ├── blockchain.py             # Web3 integration
│   ├── config.py                 # Environment configuration
│   ├── database.py               # SQLAlchemy models
│   ├── indexer.py                # Blockchain event indexer
│   ├── ipfs_service.py           # Pinata IPFS integration
│   ├── main.py                   # FastAPI REST API
│   ├── contract_abi.json         # Smart contract ABI
│   ├── test_setup.py             # Setup verification script
│   └── requirements.txt          # Python dependencies
│
├── smart-contract/               # Hardhat Smart Contract Project
│   ├── contracts/
│   │   └── FoodTraceability.sol  # Main ERC-721 contract
│   ├── scripts/
│   │   ├── deploy.js             # Deployment script
│   │   ├── assign-roles.js       # Role management script
│   │   └── check-config.js       # Config verification
│   ├── hardhat.config.js         # Hardhat configuration
│   └── package.json              # Node.js dependencies
│
├── frontend/                     # Streamlit Frontend
│   ├── streamlit_app.py          # Main Streamlit application
│   ├── .streamlit/
│   │   └── secrets.toml          # Frontend secrets (gitignored)
│   └── requirements.txt          # Python dependencies
│
├── artifacts/                    # Compiled contract artifacts
├── .gitignore                    # Git ignore rules
├── PROJECT_STATUS.md             # Detailed implementation status
└── README.md                     # This file
```

---

## 🚀 Quick Start

### Prerequisites

- **Node.js** ≥ 18
- **Python** ≥ 3.9
- **PostgreSQL** (install via `brew install postgresql@15`)
- **MetaMask** browser extension
- **Pinata** account for IPFS ([Sign up here](https://pinata.cloud))

### 1. Clone the Repository

```bash
git clone <repository-url>
cd supplychain
```

### 2. Smart Contract Setup

```bash
cd smart-contract

# Install dependencies
npm install

# Create .env file with your private key
echo "PRIVATE_KEY=your_wallet_private_key" > .env

# Verify configuration
npm run check

# Deploy to Polygon Amoy
npm run deploy:amoy
```

**Note:** You need testnet MATIC from [Polygon Faucet](https://faucet.polygon.technology/).

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python -c "from database import init_db; init_db()"

# Verify setup
python test_setup.py

# Start Event Indexer (Terminal 1)
python indexer.py

# Start API Server (Terminal 2)
uvicorn main:app --reload
```

### 4. Frontend Setup

```bash
cd frontend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create secrets file
mkdir -p .streamlit
cat > .streamlit/secrets.toml << EOF
[api]
API_URL = "http://localhost:8000"

[blockchain]
POLYGON_AMOY_RPC_URL = "https://rpc-amoy.polygon.technology/"
CONTRACT_ADDRESS = "0x2C6568f8567ba1020ce1D644eE6C15d5bA92A6f9"

[ipfs]
PINATA_API_KEY = "your_pinata_api_key"
PINATA_SECRET_API_KEY = "your_pinata_secret_key"
EOF

# Start Streamlit
streamlit run streamlit_app.py
```

### 5. Access the Application

| Service                     | URL                                                                                              |
| --------------------------- | ------------------------------------------------------------------------------------------------ |
| **Frontend**                | http://localhost:8501                                                                            |
| **Backend API**             | http://localhost:8000                                                                            |
| **API Docs (Swagger)**      | http://localhost:8000/docs                                                                       |
| **Contract on PolygonScan** | [View Contract](https://amoy.polygonscan.com/address/0x2C6568f8567ba1020ce1D644eE6C15d5bA92A6f9) |

---

## 👥 Roles & Permissions

| Role                 | Description        | Capabilities                       |
| -------------------- | ------------------ | ---------------------------------- |
| `DEFAULT_ADMIN_ROLE` | Contract deployer  | Grant/revoke all roles             |
| `PRODUCER_ROLE`      | Farmers, factories | Register new food lots             |
| `DISTRIBUTOR_ROLE`   | Logistics partners | Update lot status, track shipments |
| `RETAILER_ROLE`      | Retailers          | Mark lots as on-shelf              |
| `REGULATOR_ROLE`     | FDA, authorities   | Trigger recalls, view all data     |

---

## 📡 API Endpoints

### Lot Management

| Method | Endpoint                      | Description               |
| ------ | ----------------------------- | ------------------------- |
| `GET`  | `/lots`                       | List all lots (paginated) |
| `GET`  | `/lots/{token_id}`            | Get specific lot details  |
| `GET`  | `/lots/{token_id}/history`    | Get audit trail           |
| `GET`  | `/lots/{token_id}/blockchain` | Direct blockchain query   |
| `GET`  | `/lots/owner/{address}`       | Get lots by owner         |
| `GET`  | `/lots/{token_id}/recalled`   | Check recall status       |

### Recalls

| Method | Endpoint   | Description            |
| ------ | ---------- | ---------------------- |
| `GET`  | `/recalls` | List all recall events |

### IPFS

| Method | Endpoint       | Description         |
| ------ | -------------- | ------------------- |
| `POST` | `/upload`      | Upload file to IPFS |
| `POST` | `/upload-json` | Upload JSON to IPFS |
| `GET`  | `/ipfs/{hash}` | Retrieve from IPFS  |

### System

| Method | Endpoint             | Description       |
| ------ | -------------------- | ----------------- |
| `GET`  | `/`                  | Health check      |
| `GET`  | `/blockchain/status` | Connection status |
| `GET`  | `/stats`             | System statistics |

---

## 🔧 Smart Contract Functions

```solidity
// Register a new food lot (Producer only)
function registerLot(string productName, string origin, string ipfsHash)

// Update lot status (Producer, Distributor, Retailer)
function updateLot(uint256 lotId, string ipfsHash, Status newStatus)

// Trigger recall (Regulator only)
function triggerRecall(uint256 lotId)

// View functions
function getLot(uint256 lotId) returns (FoodLot)
function getLotHistory(uint256 lotId) returns (HistoryEntry[])
```

### Events

- `LotRegistered(lotId, productName, producer)`
- `LotStatusUpdated(lotId, newStatus, ipfsHash, updater)`
- `LotRecalled(lotId, regulator)`
- `Transfer(from, to, tokenId)` — ERC-721 standard

---

## 🎮 Using the DApp: A Journey from Farm to Fork

Experience the full lifecycle of a food product on the FoodSafe blockchain through this interactive walkthrough.

### 1. Producer: The Journey Begins

**Role:** Producer (Farmer/Manufacturer)  
**Action:** Registering a new food lot.

The producer logs in and registers a new batch of produce (e.g., "Organic Spinach - Lot 101"). They enter details like origin, harvest date, and upload safety certificates to IPFS. The system mints a unique NFT representing this specific lot.

![Producer Dashboard](Producer%20Dashboard.png)

### 2. Distributor: Maintaining the Chain of Custody

**Role:** Distributor (Logistics Provider)  
**Action:** Updating status and custody.

As the goods move, the distributor takes custody. They scan the lot ID and update the status to "In Transit". They can also upload shipping manifests or temperature logs (e.g., "Temperature maintained at 4°C") to ensure quality control.

![Distributor Dashboard](Distributor%20Dashboard.png)

### 3. Tracking: Real-Time Visibility

**Role:** Retailer / Consumer  
**Action:** Verifying provenance.

Retailers and consumers can view the complete history of the product. By entering the Lot ID, they see an immutable timeline of every handoff and status update, ensuring the food is authentic and safe.

![Tracking Dashboard](Tracking%20Dashboard.png)

### 4. Regulator: Ensuring Safety

**Role:** Regulator (FDA/Food Safety Authority)  
**Action:** Oversight and Rapid Response.

Regulators have a high-level view of the entire supply chain. They can inspect any lot's history and verify compliance.

![Regulator Dashboard Overview](Regulator%20Dashboard%20-%201.png)

### 5. The Recall: Surgical Precision

**Role:** Regulator  
**Action:** Triggering a recall.

If a safety issue is detected (e.g., a contamination report for Lot 101), the regulator can instantly trigger a **surgical recall**. This updates the smart contract status to "Recalled" immediately. Unlike blanket recalls, this targets _only_ the affected batch, notifying stakeholders instantly and preventing the unsafe product from reaching consumers.

![Regulator Recall Action](Regulator%20Dashboard%20-%202.png)

---

### 6. System Status & Admin

- **System Status:** Check blockchain connection, API health, and contract details.
- **Admin Dashboard:** Manage role-based access control (granting/revoking Producer, Distributor, Regulator roles).

---

## 📊 Project Status

| Phase               | Status      | Completion |
| ------------------- | ----------- | ---------- |
| **Smart Contracts** | ✅ Complete | 100%       |
| **Backend API**     | ✅ Complete | 100%       |
| **Event Indexer**   | ✅ Complete | 100%       |
| **Frontend**        | ✅ Complete | 100%       |

### Deployed Contract

- **Network:** Polygon Amoy Testnet
- **Address:** `0x2C6568f8567ba1020ce1D644eE6C15d5bA92A6f9`
- **Explorer:** [View on PolygonScan](https://amoy.polygonscan.com/address/0x2C6568f8567ba1020ce1D644eE6C15d5bA92A6f9)

---

## 👨‍💻 Authors

- Aakash
- Gourav
- Nimesh
- Niranth
- Mandar

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---
