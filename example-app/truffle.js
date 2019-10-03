const path = require("path");
const HDWalletProvider = require("truffle-hdwallet-provider");
const mnemonic = "use your own test account here!!!!";

module.exports = {
  contracts_build_directory: path.join(__dirname, "client/src/contracts"),
  networks: {
    development: {
      host: "127.0.0.1",
      port: 7545,
      network_id: "*" // Match any network id
    },
    origo: {
      provider: function() {
        return new HDWalletProvider(mnemonic, "https://rpc.originis.origo.network")
      },
      // provider: function() {
      //   return new HDWalletProvider(mnemonic, "http://127.0.0.1:7545")
      // },
      network_id: "27" // Match any network id
    }
  }
};
