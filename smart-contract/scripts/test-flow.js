/**
 * Complete Test Flow for FoodSafe
 * This script tests the entire food lot lifecycle
 */

const hre = require("hardhat");

async function main() {
  console.log("🧪 FoodSafe Complete Test Flow");
  console.log("=".repeat(60) + "\n");

  // Get contract instance
  const CONTRACT_ADDRESS = "0x2C6568f8567ba1020ce1D644eE6C15d5bA92A6f9";
  const [signer] = await hre.ethers.getSigners();
  
  console.log("📋 Test Configuration:");
  console.log(`   Contract: ${CONTRACT_ADDRESS}`);
  console.log(`   Signer: ${signer.address}`);
  
  const balance = await hre.ethers.provider.getBalance(signer.address);
  console.log(`   Balance: ${hre.ethers.formatEther(balance)} MATIC\n`);

  const FoodTraceability = await hre.ethers.getContractFactory("FoodTraceability");
  const contract = FoodTraceability.attach(CONTRACT_ADDRESS);

  // Check roles
  console.log("🔐 Checking Roles:");
  const PRODUCER_ROLE = await contract.PRODUCER_ROLE();
  const REGULATOR_ROLE = await contract.REGULATOR_ROLE();
  
  const hasProducer = await contract.hasRole(PRODUCER_ROLE, signer.address);
  const hasRegulator = await contract.hasRole(REGULATOR_ROLE, signer.address);
  
  console.log(`   PRODUCER_ROLE: ${hasProducer ? '✅' : '❌'}`);
  console.log(`   REGULATOR_ROLE: ${hasRegulator ? '✅' : '❌'}\n`);

  if (!hasProducer) {
    console.log("❌ You don't have PRODUCER_ROLE. Cannot register lots.");
    return;
  }

  // TEST 1: Register a Food Lot
  console.log("=".repeat(60));
  console.log("📝 TEST 1: Register a New Food Lot");
  console.log("=".repeat(60));
  
  const productName = "Organic Romaine Lettuce";
  const origin = "Salinas Valley, California";
  const ipfsHash = "QmTest123456789abcdef_" + Date.now();
  
  console.log(`   Product: ${productName}`);
  console.log(`   Origin: ${origin}`);
  console.log(`   IPFS Hash: ${ipfsHash}`);
  console.log("\n   ⏳ Sending transaction...");
  
  const tx1 = await contract.registerLot(productName, origin, ipfsHash);
  console.log(`   📤 TX Hash: ${tx1.hash}`);
  
  const receipt1 = await tx1.wait();
  console.log(`   ✅ Confirmed in block: ${receipt1.blockNumber}`);
  console.log(`   ⛽ Gas used: ${receipt1.gasUsed.toString()}`);
  
  // Get the lot ID from the event
  const lotRegisteredEvent = receipt1.logs.find(log => {
    try {
      const parsed = contract.interface.parseLog(log);
      return parsed.name === 'LotRegistered';
    } catch { return false; }
  });
  
  let lotId = 1;
  if (lotRegisteredEvent) {
    const parsed = contract.interface.parseLog(lotRegisteredEvent);
    lotId = parsed.args[0];
    console.log(`   🎫 Lot ID: ${lotId}`);
  }
  
  // TEST 2: Get Lot Details
  console.log("\n" + "=".repeat(60));
  console.log("🔍 TEST 2: Get Lot Details from Blockchain");
  console.log("=".repeat(60));
  
  const lot = await contract.getLot(lotId);
  console.log(`   Lot ID: ${lot[0]}`);
  console.log(`   Product Name: ${lot[1]}`);
  console.log(`   Origin: ${lot[2]}`);
  console.log(`   Current Owner: ${lot[3]}`);
  console.log(`   Status: ${['Created', 'InTransit', 'OnShelf', 'Recalled'][lot[4]]}`);
  console.log(`   History Entries: ${lot[5].length}`);
  
  // TEST 3: Get Lot History
  console.log("\n" + "=".repeat(60));
  console.log("📜 TEST 3: Get Lot History");
  console.log("=".repeat(60));
  
  const history = await contract.getLotHistory(lotId);
  console.log(`   Total entries: ${history.length}`);
  for (let i = 0; i < history.length; i++) {
    const entry = history[i];
    const date = new Date(Number(entry[0]) * 1000);
    console.log(`   Entry ${i + 1}:`);
    console.log(`     - Timestamp: ${date.toISOString()}`);
    console.log(`     - IPFS Hash: ${entry[1]}`);
    console.log(`     - Status: ${['Created', 'InTransit', 'OnShelf', 'Recalled'][entry[2]]}`);
  }

  // TEST 4: Update Lot Status (if we have the role)
  console.log("\n" + "=".repeat(60));
  console.log("🔄 TEST 4: Update Lot Status to InTransit");
  console.log("=".repeat(60));
  
  const updateIpfsHash = "QmUpdate_InTransit_" + Date.now();
  console.log(`   New IPFS Hash: ${updateIpfsHash}`);
  console.log("   ⏳ Sending transaction...");
  
  const tx2 = await contract.updateLot(lotId, updateIpfsHash, 1); // 1 = InTransit
  console.log(`   📤 TX Hash: ${tx2.hash}`);
  
  const receipt2 = await tx2.wait();
  console.log(`   ✅ Confirmed in block: ${receipt2.blockNumber}`);
  
  // Verify update
  const lotAfterUpdate = await contract.getLot(lotId);
  console.log(`   📊 New Status: ${['Created', 'InTransit', 'OnShelf', 'Recalled'][lotAfterUpdate[4]]}`);
  console.log(`   📊 History Entries: ${lotAfterUpdate[5].length}`);

  // TEST 5: Trigger Recall (if we have REGULATOR_ROLE)
  if (hasRegulator) {
    console.log("\n" + "=".repeat(60));
    console.log("🚨 TEST 5: Trigger Recall");
    console.log("=".repeat(60));
    
    console.log("   ⏳ Sending recall transaction...");
    
    const tx3 = await contract.triggerRecall(lotId);
    console.log(`   📤 TX Hash: ${tx3.hash}`);
    
    const receipt3 = await tx3.wait();
    console.log(`   ✅ Confirmed in block: ${receipt3.blockNumber}`);
    
    // Verify recall
    const lotAfterRecall = await contract.getLot(lotId);
    console.log(`   📊 Final Status: ${['Created', 'InTransit', 'OnShelf', 'Recalled'][lotAfterRecall[4]]}`);
    console.log(`   📊 History Entries: ${lotAfterRecall[5].length}`);
  } else {
    console.log("\n⚠️  Skipping recall test (no REGULATOR_ROLE)");
  }

  // Summary
  console.log("\n" + "=".repeat(60));
  console.log("📊 TEST SUMMARY");
  console.log("=".repeat(60));
  console.log(`   ✅ Lot Registered: ID ${lotId}`);
  console.log(`   ✅ Lot Details Retrieved`);
  console.log(`   ✅ Lot History Retrieved`);
  console.log(`   ✅ Lot Status Updated to InTransit`);
  if (hasRegulator) {
    console.log(`   ✅ Lot Recalled`);
  }
  
  console.log("\n🔗 View on PolygonScan:");
  console.log(`   https://amoy.polygonscan.com/address/${CONTRACT_ADDRESS}#events`);
  
  console.log("\n📡 Check API for indexed data:");
  console.log(`   curl http://localhost:8000/lots/${lotId}`);
  console.log(`   curl http://localhost:8000/lots/${lotId}/history`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Test failed:", error);
    process.exit(1);
  });
