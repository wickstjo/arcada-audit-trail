// IMPORT A LIST OF CONTRACTS TO UPLOAD
const config = require('../truffle-config.js')

// TRUFFLE RUNS THIS AUTOMATICALLY
module.exports = (deployer) => {
    config.contracts.forEach(path => {
        deployer.deploy(
            artifacts.require('./contracts/' + path + '.sol')
        )
    })
}