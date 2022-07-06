// THIS NEVER NEEDS TO BE MODIFIED
// READ THE TRUFFLE DOCS TO UNDERSTAND WHY
module.exports = (deployer) => {
    deployer.deploy(
        artifacts.require('./contracts/Migrations.sol')
    )
}