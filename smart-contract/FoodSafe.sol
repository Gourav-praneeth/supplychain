// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/*
 * Food Traceability Smart Contract
 * ERC721 + AccessControl + IPFS-based history tracking
 * Authors: Aakash, Gourav, Nimesh, Niranth, Mandar
 */

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract FoodTraceability is ERC721, AccessControl {
    using Counters for Counters.Counter;
    Counters.Counter private _lotCounter;

    // ROLE DEFINITIONS 
    bytes32 public constant PRODUCER_ROLE = keccak256("PRODUCER_ROLE");
    bytes32 public constant DISTRIBUTOR_ROLE = keccak256("DISTRIBUTOR_ROLE");
    bytes32 public constant RETAILER_ROLE = keccak256("RETAILER_ROLE");
    bytes32 public constant REGULATOR_ROLE = keccak256("REGULATOR_ROLE");

    // STATUS ENUM 
    enum Status { Created, InTransit, OnShelf, Recalled }

    // STRUCTS 
    /**
     * @dev Stores historical data for each status update, including 
     * timestamp, IPFS reference, and status.
     */
    struct HistoryEntry {
        uint256 timestamp;
        string ipfsHash;
        Status status;
    }

    /**
     * @dev Represents a single food lot, including its name, origin, 
     * current owner, current status, and full history of updates.
     */
    struct FoodLot {
        uint256 lotId;
        string productName;
        string origin;
        address currentOwner;
        Status status;
        HistoryEntry[] history;
    }

    // STORAGE 
    mapping(uint256 => FoodLot) private lots;

    // EVENTS
    event LotRegistered(uint256 lotId, string productName, address indexed producer);
    event LotStatusUpdated(uint256 lotId, Status newStatus, string ipfsHash, address indexed updater);
    event LotRecalled(uint256 lotId, address indexed regulator);

    // CONSTRUCTOR
    /**
     * @dev Constructor sets up contract roles and token metadata.
     * @param regulator Address that will be granted the REGULATOR_ROLE.
     */
    constructor(address regulator) ERC721("FoodTraceabilityNFT", "FTN") {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(REGULATOR_ROLE, regulator);
    }

    // REGISTER NEW LOT (Producer only)
    /**
     * @dev Allows a producer to register a new food lot.
     * Creates a new NFT and logs the initial metadata and IPFS record.
     */
    function registerLot(
        string memory _productName,
        string memory _origin,
        string memory _ipfsHash
    ) external onlyRole(PRODUCER_ROLE) {
        _lotCounter.increment();
        uint256 newLotId = _lotCounter.current();
        _safeMint(msg.sender, newLotId);

        // Create the initial history entry
        HistoryEntry memory entry = HistoryEntry({
            timestamp: block.timestamp,
            ipfsHash: _ipfsHash,
            status: Status.Created
        });

        // Store the new lot data
        FoodLot storage lot = lots[newLotId];
        lot.lotId = newLotId;
        lot.productName = _productName;
        lot.origin = _origin;
        lot.currentOwner = msg.sender;
        lot.status = Status.Created;
        lot.history.push(entry);

        emit LotRegistered(newLotId, _productName, msg.sender);
    }

    // ASSIGN ROLES
    /**
     * @dev Producers can assign the DISTRIBUTOR_ROLE to another address.
     */
    function assignDistributor(address account) external onlyRole(PRODUCER_ROLE) {
        _grantRole(DISTRIBUTOR_ROLE, account);
    }

    /**
     * @dev Distributors can assign the RETAILER_ROLE to another address.
     */
    function assignRetailer(address account) external onlyRole(DISTRIBUTOR_ROLE) {
        _grantRole(RETAILER_ROLE, account);
    }

    // --- UPDATE LOT STATUS + IPFS HASH ---
    /**
     * @dev Allows authorized roles (producer, distributor, retailer) 
     * to update the lot’s status and add a new IPFS record.
     * @param _lotId ID of the lot to update.
     * @param _ipfsHash IPFS hash containing updated information.
     * @param _newStatus New status of the lot.
     */
    function updateLot(uint256 _lotId, string memory _ipfsHash, Status _newStatus) external {
        // Ensure caller has a valid role in the supply chain
        require(
            hasRole(PRODUCER_ROLE, msg.sender) ||
            hasRole(DISTRIBUTOR_ROLE, msg.sender) ||
            hasRole(RETAILER_ROLE, msg.sender),
            "Unauthorized role"
        );

        _requireOwned(_lotId); // Verify that the NFT exists
        
        // Update lot details
        lots[_lotId].status = _newStatus;
        lots[_lotId].currentOwner = msg.sender;

        // Record the history entry
        lots[_lotId].history.push(HistoryEntry({
            timestamp: block.timestamp,
            ipfsHash: _ipfsHash,
            status: _newStatus
        }));

        emit LotStatusUpdated(_lotId, _newStatus, _ipfsHash, msg.sender);
    }

    // REGULATOR TRIGGERS RECALL 
    /**
     * @dev Allows a regulator to recall a food lot.
     * Changes its status to Recalled and logs the event.
     */
    function triggerRecall(uint256 _lotId) external onlyRole(REGULATOR_ROLE) {
        _requireOwned(_lotId); // ensures token exists
        lots[_lotId].status = Status.Recalled;
        lots[_lotId].history.push(HistoryEntry({
            timestamp: block.timestamp,
            ipfsHash: "RECALL_TRIGGERED",
            status: Status.Recalled
        }));
        emit LotRecalled(_lotId, msg.sender);
    }

    /**
     * @dev Returns all data for a specific lot.
     */
    function getLot(uint256 _lotId) external view returns (FoodLot memory) {
        _requireOwned(_lotId);
        return lots[_lotId];
    }

    // VIEW LOT HISTORY
    function getLotHistory(uint256 _lotId) external view returns (HistoryEntry[] memory) {
        _requireOwned(_lotId);
        return lots[_lotId].history;
    }

    // SUPPORT INTERFACES
    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, AccessControl)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}