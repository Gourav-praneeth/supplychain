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
   git clone <your-repo-url>
   cd FoodSafe
   
2.  **Install Node.js dependencies:**
    npm install

3. **Install Hardhat and OpenZeppelin:**
   npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox
   npm install @openzeppelin/contracts


## 🧠 Draft Smart Contract — `FoodSafe.sol`

The `FoodSafe` smart contract implements the **core on-chain logic** for the FoodSafe system.  
It leverages **OpenZeppelin’s AccessControl** and **ERC-721 standards** to provide secure, role-based management and unique lot tracking on the blockchain.

---

### 🔑 Roles & Permissions

| Role | Description | Capabilities |
|------|--------------|---------------|
| `DEFAULT_ADMIN_ROLE` | Super-admin, manages all roles. | Can grant/revoke roles. |
| `PRODUCER_ROLE` | Assigned to farmers or factories. | Register new food lots. |
| `DISTRIBUTOR_ROLE` | Assigned to logistics or shipping partners. | Add tracking history, mark lots as "On Shelf". |
| `REGULATOR_ROLE` | Assigned to regulatory authorities (e.g., FDA). | Trigger recalls and view all data. |



