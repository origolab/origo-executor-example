var AuctionVerifier = artifacts.require("./AuctionVerifier.sol");
var AuctionFactory = artifacts.require("./AuctionFactory.sol");

module.exports = function(deployer) {
  deployer.deploy(AuctionVerifier).then(function() {
    return deployer.deploy(AuctionFactory, AuctionVerifier.address);
  });
};
