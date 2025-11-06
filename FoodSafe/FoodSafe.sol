// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";

contract FoodSafe is AccessControl {
    // Roles
    bytes32 public constant PRODUCER_ROLE = keccak256("PRODUCER_ROLE");
    bytes32 public constant DISTRIBUTOR_ROLE = keccak256("DISTRIBUTOR_ROLE");
    bytes32 public constant REGULATOR_ROLE = keccak256("REGULATOR_ROLE");

    // Lot structure
    struct FoodLot {
        uint256 lotId;
        string description;
        string origin;
        string currentLocation;
        bool recalled;
        string status;
    }

    // Mapping lotId => FoodLot
    mapping(uint256 => FoodLot) public lots;

    // Events
    event LotRegistered(uint256 lotId, string description, string origin);
    event LotUpdated(uint256 lotId, string newLocation, string status);
    event LotRecalled(uint256 lotId);

    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
    }

    // Producer registers a new lot
    function registerLot(
        uint256 lotId,
        string memory description,
        string memory origin
    ) public onlyRole(PRODUCER_ROLE) {
        require(lots[lotId].lotId == 0, "Lot already exists"); // check mapping
        lots[lotId] = FoodLot({
            lotId: lotId,
            description: description,
            origin: origin,
            currentLocation: origin,
            recalled: false,
            status: "Produced"
        });
        emit LotRegistered(lotId, description, origin);
    }

    // Distributor updates location/status
    function updateLocation(uint256 lotId, string memory newLocation)
        public onlyRole(DISTRIBUTOR_ROLE)
    {
        require(lots[lotId].lotId != 0, "Lot does not exist");
        require(!lots[lotId].recalled, "Lot has been recalled");
        lots[lotId].currentLocation = newLocation;
        lots[lotId].status = "In Transit / On Shelf";
        emit LotUpdated(lotId, newLocation, lots[lotId].status);
    }

    // Regulator recalls a lot
    function recallLot(uint256 lotId) public onlyRole(REGULATOR_ROLE) {
        require(lots[lotId].lotId != 0, "Lot does not exist");
        lots[lotId].recalled = true;
        lots[lotId].status = "Recalled";
        emit LotRecalled(lotId);
    }

    // View lot details
    function getLot(uint256 lotId) public view returns (FoodLot memory) {
        require(lots[lotId].lotId != 0, "Lot does not exist");
        return lots[lotId];
    }
}
