import React, { Component } from "react";

import AuctionContractJson from "./contracts/Auction.json.js";
import AuctionFactoryContractJson from "./contracts/AuctionFactory.json.js";

import getWeb3 from "./utils/getWeb3";
import getContractInstance from './utils/getContractInstance';

import { Input, Button } from 'semantic-ui-react'
import "./App.css";

const origoUtils = require('./lib/origo-utils')
const GAS = 1000000
const callGAS = 40000

class App extends Component {
  constructor(props) {
    super(props)
    this.state = {
      web3Ready: false,
      inputValue: null,
      randomValue: null,
      loading: false
    }
    this.web3 = null
    this.accounts = null
    this.factoryContract = null
    this.contract = null
    this.timerId = null
  }

  componentDidMount = async () => {
    try {
      // Get network provider and web3 instance.
      this.web3 = await getWeb3();

      // Use web3 to get the user's accounts.
      this.accounts = await this.web3.eth.getAccounts();

      // Get the contract instance.
      this.factoryContract = await getContractInstance(
        this.web3,
        AuctionFactoryContractJson
      );
      await this.getLastContract(
        this.web3,
        this.factoryContract,
        AuctionContractJson
      );

      if (this.web3) {
        this.setState({ web3Ready: true });
      }
      await this.checkState();
    } catch (error) {
      // Catch any errors for any of the above operations.
      alert(
        `Failed to load web3, accounts, or contract. Check console for details.`
      )
      console.log(error)
    }
  }

  componentWillUnmount = () => {
    if (this.timerId) {
      clearTimeout(this.timerId)
    }
  }

  async checkState() {
    console.log('check state here')
    console.log((await this.web3.eth.getAccounts())[0])
    if (this.contract == null) {
      return
    }
    console.log('check state return')
    this.setState({
      inputSubmitted: await this.contract.methods
        .isInputSubmitted(this.accounts[0])
        .call({ from: this.accounts[0], gas: callGAS }),
      userCount: await this.contract.methods
        .getUserCount()
        .call({ from: this.accounts[0], gas: callGAS }),
      openCount: await this.contract.methods
        .getOpenCount()
        .call({ from: this.accounts[0], gas: callGAS }),
      isGameOver: await this.contract.methods
        .getIsGameOver()
        .call({ from: this.accounts[0], gas: callGAS }),
      isOpenFinished: await this.contract.methods
        .isOpenFinished()
        .call({ from: this.accounts[0], gas: callGAS }),
      result: await this.contract.methods
        .getResult()
        .call({ from: this.accounts[0], gas: callGAS })
    })
    this.timerId = setTimeout(async () => await this.checkState(), 60000)
  }

  // Create fresh, new Vote contract
  async create(json) {
    console.log('start to create game.')
    await this.factoryContract.methods.create().send({
      from: this.accounts[0],
      gasPrice: '10000000',
      gas: GAS * 6
    })
    console.log('game created')
    await this.getLastContract(this.web3, this.factoryContract, json)
  }  

  async getLastContract(web3, factoryContract, json) {
    // Obtain the latest-deployed Vote instance, this will be the one we interact with
    const contracts = await factoryContract.methods
      .getContracts()
      .call({ from: this.accounts[0], gas: callGAS })
    console.log(contracts)
    if (contracts.length !== 0) {
      const contract = await getContractInstance(
        web3,
        json,
        contracts[contracts.length - 1]
      )
      console.log(contract)
      console.log('contract address: ' + contract._address)
      this.contract = contract
      this.setState({
        loading: false
      })
    }
  }

  handleMessage(event) {
    this.setState({
      inputValue: event.target.value
    })
  }

  handleCommit(event) {
    event.preventDefault()
    const randomValue = origoUtils.generateRandom()
    const commitment = origoUtils.generateCommitment(
      this.state.inputValue,
      randomValue
    )

    console.log('commitment: ' + commitment)
    this.setState({
      randomValue,
      commitment
    })
    const contract = this.contract
    const web3 = this.web3
    const encryptedInput = origoUtils.encrypt(this.state.inputValue)
    const encryptedRandom = origoUtils.encrypt(randomValue)

    contract.methods
      .submitCommitAndInput(
        encryptedInput.map(x => web3.utils.toHex(x.toString())),
        encryptedRandom.map(x => web3.utils.toHex(x.toString())),
        web3.utils.toHex(commitment.commitPart1.toString()),
        web3.utils.toHex(commitment.commitPart2.toString())
      )
      .send({
        from: this.accounts[0],
        // value: web3.utils.toWei("2", "ether"),
        gas: GAS
      })
      .then(function(receipt) {
        console.log(receipt)
      })
  }

  handleNewGame(event) {
    event.preventDefault()
    this.setState({
      loading: true
    })
    this.create(AuctionContractJson)
  }

  handleRegister(event) {
    event.preventDefault()

    if (this.contract == null) return

    fetch('http://127.0.0.1:28888/register_contract/' + this.contract._address)
      .then(function(response) {
        return response.json()
      })
      .then(function(myJson) {
        console.log(JSON.stringify(myJson))
      })
  }

  handleUnregister(event) {
    event.preventDefault()

    if (this.contract == null) return

    fetch('http://127.0.0.1:28888/unregister_contract/' + this.contract._address)
      .then(function(response) {
        return response.json()
      })
      .then(function(myJson) {
        console.log(JSON.stringify(myJson))
      })
  }

  render() {
    if (!this.state.web3Ready) {
      return <div>Loading Web3, accounts, and contract...</div>
    }
    return (
      <div className="App">
        <Input
          onChange={this.handleMessage.bind(this)}
          placeholder="Your commit..."
        />
        <Button primary onClick={this.handleCommit.bind(this)}>
          Submit
        </Button>
        <Button
          secondary
          loading={this.state.loading}
          onClick={this.handleNewGame.bind(this)}
        >
          Create New Game
        </Button>
        <Button primary onClick={this.handleRegister.bind(this)}>
          register
        </Button>
        <Button primary onClick={this.handleUnregister.bind(this)}>
          unregister
        </Button>
        <h3>inputSubmitted: {'' + this.state.inputSubmitted}</h3>
        <h3>userCount: {this.state.userCount}</h3>
        <h3>openCount: {this.state.openCount}</h3>
        <h3>isGameOver: {'' + this.state.isGameOver}</h3>
        <h3>isOpenFinished: {'' + this.state.isOpenFinished}</h3>
        <h3>result: {'' + this.state.result}</h3>
      </div>
    )
  }
}

export default App;
