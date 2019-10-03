const getContractInstance = async (
  web3,
  contractJson,
  address = null
) => {
  const networkId = await web3.eth.net.getId();
  const deployedNetwork = contractJson.networks[networkId];
  const deployedAddress = address == null ? deployedNetwork.address : address;
  const instance = new web3.eth.Contract(contractJson.abi, deployedAddress);
  return instance;
}

export default getContractInstance;