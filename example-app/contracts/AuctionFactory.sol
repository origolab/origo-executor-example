pragma solidity ^0.5.0;

import "./Auction.sol";

contract AuctionFactory {
  address public owner;
  address public auctionVerifier;
  address[] public auctions;

  constructor(address _auctionVerifier) public {
    owner = msg.sender;
    auctionVerifier = _auctionVerifier;
  }

  function create() public {
    require(msg.sender == owner, "only owner can create auction.");
    Auction newAuction = new Auction(owner, auctionVerifier);
    auctions.push(address(newAuction));
  }

  function getContracts() public view returns (address[] memory) {
    return auctions;
  }
}