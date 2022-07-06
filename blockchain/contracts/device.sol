pragma solidity ^0.8.4;
// SPDX-License-Identifier: MIT

contract Device {

    // ETH WALLET THAT OWNS THE CONTRACT
    address public owner;

    // ASSIGNED IDENTIFIER & NAME
    string public identifier;
    string public name;

    // CREATED DURING BLOCK
    uint public created;

    // ACTIVE STATUS
    bool public active;

    // WHEN CREATED..
    constructor(
        string memory _identifier,
        string memory _name,
        address _owner
    ) {

        // SET STATIC VARIABLES
        identifier = _identifier;
        name = _name;
        owner = _owner;

        // SET CREATION BLOCK
        created = block.number;

        // SET ACTIVE STATUS TO FALSE
        active = false;
    }

    // TOGGLE ACTIVE STATUS
    function toggle_active() public {

        // IF THE NAME IS NOT ALREADY TAKEN
        require(msg.sender == owner, 'only the owner can perform this action');

        // CHANGE ACTIVE STATUS
        active = !active;
    }

    // FETCH THE CONTRACT DETAILS
    function details() public view returns(address, string memory, string memory, uint, bool) {
        return (owner, identifier, name, created, active);
    }
}