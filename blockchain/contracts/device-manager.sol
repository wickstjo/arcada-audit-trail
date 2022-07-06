pragma solidity ^0.8.4;
pragma experimental ABIEncoderV2;
// SPDX-License-Identifier: MIT

// IMPORT THE DEVICE CONTRACTS INTERFACE
import { Device } from './device.sol';

contract DeviceManager {

    // MAP OF EXISTING DEVICE CONTRACTS
    // IDENTIFIER => DEVICE CONTRACT
    mapping (string => Device) public devices;

    // USER DEVICE CONTRACT COLLECTIONS
    // OWNER => LIST OF DEVICE IDENTIFIERS
    mapping (address => string[]) public collections;

    // FETCH A DEVICE CONTRACT BY IDENTIFIER
    function fetch_device(string memory identifier) public view returns(Device) {
        return devices[identifier];
    }

    // FETCH USER DEVICE COLLECTION
    // THIS IS NECESSARY BECAUSE MAPS ARE NOT ITERABLE WHILE ARRAYS ARE
    function fetch_collection(address user) public view returns(string[] memory) {
        return collections[user];
    }

    // CREATE NEW CHILD CONTRACT
    function create_device(string memory identifier, string memory name) public {

        // IF THE NAME IS NOT ALREADY TAKEN
        require(!exists(identifier), 'this identifier already exists');

        // INSTANTIATE A NEW CHILD CONTRACT
        Device device = new Device(identifier, name, msg.sender);

        // INDEX IN BOTH CONTAINERS
        devices[identifier] = device;
        collections[msg.sender].push(identifier);
    }

    // CHECK IF A DEVICE EXISTS
    function exists(string memory identifier) public view returns(bool) {
        if (address(devices[identifier]) != 0x0000000000000000000000000000000000000000) {
            return true;
        } else {
            return false;
        }
    }
}