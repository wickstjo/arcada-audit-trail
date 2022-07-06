pragma solidity ^0.8.4;
// SPDX-License-Identifier: MIT

// THIS CONTRACT DOES NOT EVER NEED TO BE MODIFIED
// READ THE TRUFFLE DOCS TO UNDERSTAND WHY
contract Migrations {

    address public owner;
    uint public last_completed_migration;

    modifier restricted() {
        if (msg.sender == owner) _;
    }

    constructor() {
        owner = msg.sender;
    }

    function setCompleted(uint completed) public restricted {
        last_completed_migration = completed;
    }

    function upgrade(address new_address) public restricted {
        Migrations upgraded = Migrations(new_address);
        upgraded.setCompleted(last_completed_migration);
    }
}