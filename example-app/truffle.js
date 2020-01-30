const path = require('path')
const HDWalletProvider = require('truffle-hdwallet-provider')
const mnemonic = "use your own test account here!!!!";

module.exports = {
  contracts_build_directory: path.join(__dirname, "client/src/contracts"),
  networks: {
    development: {
      host: "127.0.0.1",
      port: 6622,
      network_id: "*" // Match any network id
    },
    origo: {
      provider: function() {
        return new HDWalletProvider(mnemonic, "https://rpc.medietas.origo.network")
        // return new HDWalletProvider(mnemonic, "http://127.0.0.1:6622")
        // return new HDWalletProvider(mnemonic, "http://127.0.0.1:7545")
      },
      // provider: function() {
      //   return new HDWalletProvider(mnemonic, "http://127.0.0.1:7545")
      // },
      network_id: "*", // Match any network id
      gas: 3000000
    }
  },
  // compilers: {
  //   solc: {
  //     version: "0.5.0",
  //   settings: {
  //      evmVersion: "byzantium" // Default: "petersburg"
  //    }	
  //   }
  //  }
};
