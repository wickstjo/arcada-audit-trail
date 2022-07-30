module.exports = {

    // BLOCKCHAIN SETTINGS
    networks: {
        development: {
            host: '127.0.0.1',
            port: 8545,
            network_id: "*",
            gas: 5000000,
            websockets: true
        }
    },

    // COMPILER SETTINGS
    compilers: {
        solc: {
            version: "^0.8.4",
            settings: {
                optimizer: {
                    enabled: true,
                    runs: 200
                }
            }
        }
    },

    // CONTRACTS TO UPLOAD
    contracts: [
        'DeviceManager',
    ]
}