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
- Distributor: updates custody in transit → `DISTRIBUTOR_ROLE`
- Retailer: marks received/on-shelf → `RETAILER_ROLE`
- Regulator: issues/clears recalls; can pause → `REGULATOR_ROLE`

**On-chain (Solidity)**
- ERC-721 token per lot (tokenId)
- Events: `BatchRegistered`, `CustodyTransferred`, `StatusUpdated`,
  `SensorReadingRecorded`, `RecallIssued`, `RecallCleared`
- RBAC via OpenZeppelin `AccessControl`
- Minimal on-chain storage + event-first design
- Recall bit per token, managed by regulator

**Off-chain**
- IPFS for certificates, CoAs, extended sensor logs
- Frontend (React/Streamlit) consumes chain events via Alchemy/Infura + Ethers

---

## Features (Draft)
- Lot registration (producer-only)
- Custody transfer (owner-only; emits history event)
- Status changes (`Created`, `InTransit`, `Received`, `OnShelf`, `Recalled`, `Destroyed`)
- Regulator recall (issue/clear) at token or list-of-tokens granularity

---

## Dependencies / Setup

**Core**
- Node.js ≥ 18, Yarn or npm
- Hardhat, Ethers.js, OpenZeppelin Contracts

```bash
# from repo root
npm init -y
npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox
npm install @openzeppelin/contracts dotenv
npx hardhat init
