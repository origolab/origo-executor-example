const env = require("./environment");
const BN = require("bn.js");
const forge = require('node-forge');

const _fieldBitLimit = new BN("21888242871839275222246405745257275088548364400416034343698204186575808495616");

function sha256(content) {
  const md = forge.md.sha256.create();
  md.update(content);
  console.log(md.digest().toHex());
  return md.digest().toHex();
}

/**
 * Function that converts a string into its binary representation
 */
function stringToBinary(str) {
  function zeroPad(num) {
      return "00000000".slice(String(num).length) + num;
  }

  return str.replace(/[\s\S]/g, str => zeroPad(str.charCodeAt().toString(2)));
};

function binaryAgent(str) {
  // Removes the spaces from the binary string
  str = str.replace(/\s+/g, '');
  // Pretty (correct) print binary (add a space every 8 characters)
  str = str.match(/.{1,8}/g).join(" ");

  return str.split(" ").map(function (elem) {
    return String.fromCharCode(parseInt(elem, 2));
  }).join("");
}

// Generate 128 bits random number for padding input.
function generateRandom() {
  return new BN(stringToBinary(forge.random.getBytesSync(16)), 2);
}

function generateCommitment(input, randomNum) {
  const inputNum = new BN(input).toString(2, 512);

  const c1 = new BN(inputNum.slice(0, 128), 2).add(randomNum).mod(_fieldBitLimit).toString(2, 128);
  const c2 = new BN(inputNum.slice(128, 256), 2).add(randomNum).mod(_fieldBitLimit).toString(2, 128);
  const c3 = new BN(inputNum.slice(256, 384), 2).add(randomNum).mod(_fieldBitLimit).toString(2, 128);
  const c4 = new BN(inputNum.slice(384, 512), 2).add(randomNum).mod(_fieldBitLimit).toString(2, 128);

  const oc = c1 + c2 + c3 + c4;
  const shaResult = sha256(binaryAgent(oc));

  const bSha = new BN(shaResult, 16).toString(2, 256);
  return {
    commitPart1: new BN(bSha.slice(0, 128), 2),
    commitPart2: new BN(bSha.slice(128, 256), 2)
  }
}

// input as a BN.
function encrypt(bnMessage) {
  const data = new BN(bnMessage).toString(2, 512);
  const pubKey = forge.pki.publicKeyFromPem(env.keys.publicKey);
  const encryptText = pubKey.encrypt(binaryAgent(data), 'RSAES-PKCS1-V1_5');
  const binaryEncryptText = stringToBinary(encryptText);
  return [
    new BN(binaryEncryptText.slice(0, 256), 2),
    new BN(binaryEncryptText.slice(256, 512), 2),
    new BN(binaryEncryptText.slice(512, 768), 2),
    new BN(binaryEncryptText.slice(768, 1024), 2),
  ];
}

function decrypt(encryptText) {
  const text = new BN(encryptText).toString(2, 1024);
  const eText = binaryAgent(text);
  const privateKey = forge.pki.privateKeyFromPem(env.keys.privateKey);
  const message = privateKey.decrypt(eText, 'RSAES-PKCS1-V1_5');
  return message;
}

exports.generateRandom = generateRandom;
exports.generateCommitment = generateCommitment;
exports.encrypt = encrypt;
exports.decrypt = decrypt;