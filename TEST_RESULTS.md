# 🧪 FoodSafe Blockchain Test Results

**Test Date:** December 5, 2024  
**Network:** Polygon Amoy Testnet  
**Contract:** `0x2C6568f8567ba1020ce1D644eE6C15d5bA92A6f9`

---

## ✅ Test Summary: ALL TESTS PASSED

| Test | Description | Status | Transaction Hash |
|------|-------------|--------|------------------|
| 1 | Register Food Lot |  PASSED | `0x92150bd3...` |
| 2 | Get Lot Details |  PASSED | N/A (read) |
| 3 | Get Lot History |  PASSED | N/A (read) |
| 4 | Update Status to InTransit |  PASSED | `0x8cefc2c0...` |
| 5 | Trigger Recall |  PASSED | `0x1cc0a48a...` |
| 6 | Indexer Processing |  PASSED | N/A |
| 7 | API Data Retrieval |  PASSED | N/A |

---

## 📝 Test 1: Register a New Food Lot

**Action:** Called `registerLot()` on smart contract

**Input:**
```
Product Name: Organic Romaine Lettuce
Origin: Salinas Valley, California
IPFS Hash: QmTest123456789abcdef_1764902235117
```

**Result:**
```
Transaction Hash: 0x92150bd351cd7075b212917fd6e26dbda63b6d65872e076029bc0620562859e0
Block Number: 29968059
Gas Used: 302,210
Lot ID Minted: 1
```

**PolygonScan:** [View Transaction](https://amoy.polygonscan.com/tx/0x92150bd351cd7075b212917fd6e26dbda63b6d65872e076029bc0620562859e0)

---

## 🔍 Test 2: Get Lot Details from Blockchain

**Action:** Called `getLot(1)` on smart contract

**Result:**
```
Lot ID: 1
Product Name: Organic Romaine Lettuce
Origin: Salinas Valley, California
Current Owner: 0x635C0f9D399a1d7Ff1e9aC94571A07504821E46e
Status: Created
History Entries: 1
```

---

## 📜 Test 3: Get Lot History

**Action:** Called `getLotHistory(1)` on smart contract

**Result:**
```
Entry 1:
  - Timestamp: 2025-12-05T02:37:18.000Z
  - IPFS Hash: QmTest123456789abcdef_1764902235117
  - Status: Created
```

---

## 🔄 Test 4: Update Lot Status to InTransit

**Action:** Called `updateLot()` on smart contract

**Input:**
```
Lot ID: 1
New Status: InTransit (1)
IPFS Hash: QmUpdate_InTransit_1764902239682
```

**Result:**
```
Transaction Hash: 0x8cefc2c082aec910854d5231f576b4734c85c5a64abfd13e94413c85eb4b61c7
Block Number: 29968062
New Status: InTransit
History Entries: 2
```

**PolygonScan:** [View Transaction](https://amoy.polygonscan.com/tx/0x8cefc2c082aec910854d5231f576b4734c85c5a64abfd13e94413c85eb4b61c7)

---

## 🚨 Test 5: Trigger Recall

**Action:** Called `triggerRecall(1)` on smart contract

**Result:**
```
Transaction Hash: 0x1cc0a48aa771f28a5636093b3d20861076dd5b4c6204afe30c1bf7f32303fe42
Block Number: 29968064
Final Status: Recalled
History Entries: 3
```

**PolygonScan:** [View Transaction](https://amoy.polygonscan.com/tx/0x1cc0a48aa771f28a5636093b3d20861076dd5b4c6204afe30c1bf7f32303fe42)

---

## 📡 Test 6 & 7: API Data Verification

**After indexer processed blockchain events:**

### GET /lots/1
```json
{
    "token_id": 1,
    "owner_address": "0x635C0f9D399a1d7Ff1e9aC94571A07504821E46e",
    "status": "Recalled",
    "is_recalled": true,
    "created_at": "2025-12-05T02:37:23.844622",
    "updated_at": "2025-12-05T02:37:30.837740"
}
```

### GET /lots/1/history
```json
[
    {
        "id": 1,
        "token_id": 1,
        "timestamp": "2025-12-05T02:37:22.726134",
        "stakeholder_address": "0x635C0f9D399a1d7Ff1e9aC94571A07504821E46e",
        "event_type": "LotRegistered",
        "transaction_hash": "0x92150bd351cd7075b212917fd6e26dbda63b6d65872e076029bc0620562859e0"
    },
    {
        "id": 2,
        "token_id": 1,
        "timestamp": "2025-12-05T02:37:30.302566",
        "stakeholder_address": "0x635C0f9D399a1d7Ff1e9aC94571A07504821E46e",
        "ipfs_hash": "QmUpdate_InTransit_1764902239682",
        "event_type": "LotStatusUpdated",
        "transaction_hash": "0x8cefc2c082aec910854d5231f576b4734c85c5a64abfd13e94413c85eb4b61c7"
    },
    {
        "id": 3,
        "token_id": 1,
        "timestamp": "2025-12-05T02:37:31.018857",
        "ipfs_hash": "RECALL_TRIGGERED",
        "event_type": "LotRecalled",
        "transaction_hash": "0x1cc0a48aa771f28a5636093b3d20861076dd5b4c6204afe30c1bf7f32303fe42"
    }
]
```

### GET /stats
```json
{
    "total_lots": 1,
    "recalled_lots": 1,
    "lots_by_status": {
        "Created": 0,
        "InTransit": 0,
        "OnShelf": 0,
        "Recalled": 1
    },
    "total_history_entries": 3,
    "total_recall_events": 1
}
```

### GET /recalls
```json
[
    {
        "id": 1,
        "token_id": 1,
        "regulator_address": "0x635C0f9D399a1d7Ff1e9aC94571A07504821E46e",
        "timestamp": "2025-12-05T02:37:31.018857",
        "transaction_hash": "0x1cc0a48aa771f28a5636093b3d20861076dd5b4c6204afe30c1bf7f32303fe42"
    }
]
```

---

## 🔗 Verification Links

- **Contract on PolygonScan:** [View Contract](https://amoy.polygonscan.com/address/0x2C6568f8567ba1020ce1D644eE6C15d5bA92A6f9)
- **Contract Events:** [View Events](https://amoy.polygonscan.com/address/0x2C6568f8567ba1020ce1D644eE6C15d5bA92A6f9#events)

---

## 🔄 How to Reproduce These Tests

### Method 1: Run the Test Script

```bash
cd smart-contract
npx hardhat run scripts/test-flow.js --network amoy
```

### Method 2: Manual API Testing

```bash
# Check system status
curl http://localhost:8000/blockchain/status

# Get lot details
curl http://localhost:8000/lots/1

# Get lot history
curl http://localhost:8000/lots/1/history

# Get all recalls
curl http://localhost:8000/recalls

# Get system statistics
curl http://localhost:8000/stats
```

### Method 3: Using Hardhat Console

```bash
cd smart-contract
npx hardhat console --network amoy
```

```javascript
// Get contract
const contract = await ethers.getContractAt(
  "FoodTraceability", 
  "0x2C6568f8567ba1020ce1D644eE6C15d5bA92A6f9"
);

// Register a lot
await contract.registerLot("Test Product", "Test Origin", "QmTestHash");

// Get lot details
const lot = await contract.getLot(1);
console.log(lot);

// Update status
await contract.updateLot(1, "QmUpdateHash", 1); // 1 = InTransit

// Trigger recall
await contract.triggerRecall(1);
```

### Method 4: Using Streamlit Frontend

1. Open http://localhost:8501
2. Enter wallet address: `0x635C0f9D399a1d7Ff1e9aC94571A07504821E46e`
3. Enable transaction signing with your private key
4. Select "Producer" dashboard to register lots
5. Select "Regulator" dashboard to trigger recalls

---

## 📊 Gas Costs Summary

| Operation | Gas Used | Approx. Cost (at 50 gwei) |
|-----------|----------|---------------------------|
| Register Lot | 302,210 | ~0.015 MATIC |
| Update Status | ~100,000 | ~0.005 MATIC |
| Trigger Recall | ~80,000 | ~0.004 MATIC |

---

## ✅ Test Conclusion

All components of the FoodSafe system are working correctly:

1. **Smart Contract** - Deployed and functional on Polygon Amoy
2. **Blockchain Transactions** - All write operations succeed
3. **Event Emission** - Events are emitted correctly
4. **Event Indexer** - Captures and stores all events
5. **REST API** - Serves data correctly
6. **Database** - Stores indexed data properly

**The FoodSafe system is fully operational!** 

