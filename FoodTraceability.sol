// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/*
 * Food Traceability Smart Contract
 * Based on blockchain + IPFS architecture for contamination tracking and recall management
 */

contract FoodTraceability {
    uint256 public lotCounter;
    address public regulator;

    enum Status { Created, InTransit, OnShelf, Recalled }

    struct FoodLot {
        uint256 lotId;
        string productName;
        string origin;
        string ipfsHash;     // IoT or certification data stored in IPFS
        address producer;
        address distributor;
        address retailer;
        Status status;
    }

    mapping(uint256 => FoodLot) public lots;

    event LotRegistered(uint256 lotId, string productName, address indexed producer);
    event StatusUpdated(uint256 lotId, Status newStatus, address indexed updater);
    event RecallTriggered(uint256 lotId, address indexed regulator);

    constructor(address _regulator) {
        regulator = _regulator;
    }

    // Step 1: Farmer registers new product batch
    function registerLot(
        string memory _productName,
        string memory _origin,
        string memory _ipfsHash
    ) public {
        lotCounter++;
        lots[lotCounter] = FoodLot({
            lotId: lotCounter,
            productName: _productName,
            origin: _origin,
            ipfsHash: _ipfsHash,
            producer: msg.sender,
            distributor: address(0),
            retailer: address(0),
            status: Status.Created
        });
        emit LotRegistered(lotCounter, _productName, msg.sender);
    }

    // Step 2: Assign distributor (only by producer)
    function assignDistributor(uint256 _lotId, address _distributor) public {
        require(msg.sender == lots[_lotId].producer, "Only producer can assign distributor");
        lots[_lotId].distributor = _distributor;
    }

    // Step 3: Assign retailer (only by distributor)
    function assignRetailer(uint256 _lotId, address _retailer) public {
        require(msg.sender == lots[_lotId].distributor, "Only distributor can assign retailer");
        lots[_lotId].retailer = _retailer;
    }

    // Step 4: Update IPFS hash or shipment status
    function updateIPFS(uint256 _lotId, string memory _newIPFSHash, Status _newStatus) public {
        require(
            msg.sender == lots[_lotId].producer ||
            msg.sender == lots[_lotId].distributor ||
            msg.sender == lots[_lotId].retailer,
            "Unauthorized"
        );
        lots[_lotId].ipfsHash = _newIPFSHash;
        lots[_lotId].status = _newStatus;
        emit StatusUpdated(_lotId, _newStatus, msg.sender);
    }

    // Step 5: Regulator triggers recall
    function triggerRecall(uint256 _lotId) public {
        require(msg.sender == regulator, "Only regulator can trigger recall");
        lots[_lotId].status = Status.Recalled;
        emit RecallTriggered(_lotId, msg.sender);
    }

    // Step 6: View details for authenticity verification
    function getLot(uint256 _lotId) public view returns (FoodLot memory) {
        return lots[_lotId];
    }

    // Step 7: Regulator audits all lots (returns recalled and active)
    function auditAllLots() public view returns (FoodLot[] memory) {
        require(msg.sender == regulator, "Only regulator can audit");
        FoodLot[] memory all = new FoodLot[](lotCounter);
        for (uint256 i = 1; i <= lotCounter; i++) {
            all[i - 1] = lots[i];
        }
        return all;
    }
}
