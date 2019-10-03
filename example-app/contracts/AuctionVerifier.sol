// This file is MIT Licensed.
//
// Copyright 2017 Christian Reitwiessner
// Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
// The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

pragma solidity ^0.5.0;

import "./IVerifier.sol";

library Pairing {
  struct G1Point {
    uint X;
    uint Y;
  }
  // Encoding of field elements is: X[0] * z + X[1]
  struct G2Point {
    uint[2] X;
    uint[2] Y;
  }
  /// @return the generator of G1
    function P1() pure internal returns (G1Point memory) {
    return G1Point(1, 2);
  }
  /// @return the generator of G2
    function P2() pure internal returns (G2Point memory) {
    return G2Point(
      [
        11559732032986387107991004021392285783925812861821192530917403151452391805634,
        10857046999023057135944570762232829481370756359578518086990519993285655852781
      ],
      [
        4082367875863433681332203403145435568316851327593401208105741076214120093531,
        8495653923123431417604973247489272438418190587263600148770280649306958101930
      ]
    );
  }
  /// @return the negation of p, i.e. p.addition(p.negate()) should be zero.
  function negate(G1Point memory p) pure internal returns (G1Point memory) {
    // The prime q in the base field F_q for G1
    uint q = 21888242871839275222246405745257275088696311157297823662689037894645226208583;
    if (p.X == 0 && p.Y == 0)
      return G1Point(0, 0);
    return G1Point(p.X, q - (p.Y % q));
  }
  /// @return the sum of two points of G1
  function addition(G1Point memory p1, G1Point memory p2) internal returns (G1Point memory r) {
    uint[4] memory input;
    input[0] = p1.X;
    input[1] = p1.Y;
    input[2] = p2.X;
    input[3] = p2.Y;
    bool success;
    assembly {
      success := call(sub(gas, 2000), 6, 0, input, 0xc0, r, 0x60)
      // Use "invalid" to make gas estimation work
      switch success case 0 { invalid() }
    }
    require(success);
  }
  /// @return the product of a point on G1 and a scalar, i.e.
  /// p == p.scalar_mul(1) and p.addition(p) == p.scalar_mul(2) for all points p.
  function scalar_mul(G1Point memory p, uint s) internal returns (G1Point memory r) {
    uint[3] memory input;
    input[0] = p.X;
    input[1] = p.Y;
    input[2] = s;
    bool success;
    assembly {
      success := call(sub(gas, 2000), 7, 0, input, 0x80, r, 0x60)
      // Use "invalid" to make gas estimation work
      switch success case 0 { invalid() }
    }
    require (success);
  }
  /// @return the result of computing the pairing check
  /// e(p1[0], p2[0]) *  .... * e(p1[n], p2[n]) == 1
  /// For example pairing([P1(), P1().negate()], [P2(), P2()]) should
  /// return true.
  function pairing(G1Point[] memory p1, G2Point[] memory p2) internal returns (bool) {
    require(p1.length == p2.length);
    uint elements = p1.length;
    uint inputSize = elements * 6;
    uint[] memory input = new uint[](inputSize);
    for (uint i = 0; i < elements; i++)
    {
      input[i * 6 + 0] = p1[i].X;
      input[i * 6 + 1] = p1[i].Y;
      input[i * 6 + 2] = p2[i].X[0];
      input[i * 6 + 3] = p2[i].X[1];
      input[i * 6 + 4] = p2[i].Y[0];
      input[i * 6 + 5] = p2[i].Y[1];
    }
    uint[1] memory out;
    bool success;
    assembly {
      success := call(sub(gas, 2000), 8, 0, add(input, 0x20), mul(inputSize, 0x20), out, 0x20)
      // Use "invalid" to make gas estimation work
      switch success case 0 { invalid() }
    }
    require(success);
    return out[0] != 0;
  }
  /// Convenience method for a pairing check for two pairs.
  function pairingProd2(G1Point memory a1, G2Point memory a2, G1Point memory b1, G2Point memory b2) internal returns (bool) {
    G1Point[] memory p1 = new G1Point[](2);
    G2Point[] memory p2 = new G2Point[](2);
    p1[0] = a1;
    p1[1] = b1;
    p2[0] = a2;
    p2[1] = b2;
    return pairing(p1, p2);
  }
  /// Convenience method for a pairing check for three pairs.
  function pairingProd3(
    G1Point memory a1, G2Point memory a2,
    G1Point memory b1, G2Point memory b2,
    G1Point memory c1, G2Point memory c2
  ) internal returns (bool) {
    G1Point[] memory p1 = new G1Point[](3);
    G2Point[] memory p2 = new G2Point[](3);
    p1[0] = a1;
    p1[1] = b1;
    p1[2] = c1;
    p2[0] = a2;
    p2[1] = b2;
    p2[2] = c2;
    return pairing(p1, p2);
  }
  /// Convenience method for a pairing check for four pairs.
  function pairingProd4(
    G1Point memory a1, G2Point memory a2,
    G1Point memory b1, G2Point memory b2,
    G1Point memory c1, G2Point memory c2,
    G1Point memory d1, G2Point memory d2
  ) internal returns (bool) {
    G1Point[] memory p1 = new G1Point[](4);
    G2Point[] memory p2 = new G2Point[](4);
    p1[0] = a1;
    p1[1] = b1;
    p1[2] = c1;
    p1[3] = d1;
    p2[0] = a2;
    p2[1] = b2;
    p2[2] = c2;
    p2[3] = d2;
    return pairing(p1, p2);
  }
}

contract AuctionVerifier is IVerifier {
  using Pairing for *;
  struct VerifyingKey {
    Pairing.G2Point A;
    Pairing.G1Point B;
    Pairing.G2Point C;
    Pairing.G2Point gamma;
    Pairing.G1Point gammaBeta1;
    Pairing.G2Point gammaBeta2;
    Pairing.G2Point Z;
    Pairing.G1Point[] IC;
  }
  struct Proof {
    Pairing.G1Point A;
    Pairing.G1Point A_p;
    Pairing.G2Point B;
    Pairing.G1Point B_p;
    Pairing.G1Point C;
    Pairing.G1Point C_p;
    Pairing.G1Point K;
    Pairing.G1Point H;
  }
  function verifyingKey() pure internal returns (VerifyingKey memory vk) {
    vk.A = Pairing.G2Point([0x29c3babd03a5e28a2cd39f1cc5ce16d452b798ae9115b9681dcfa16c34ebd50d, 0x298e659c28ca08b582bd7e200cdf1278b1a903a41ccfd95a3a22adcff2e2daea], [0x15c805ef2079324af613c0eb32bdeea2b321be277fedf45c9a5734ce08b99206, 0x2be76d106e4cf2fbdb1840b54b246a5d09ad79c5c7c23584824be6fd02aa02aa]);
    vk.B = Pairing.G1Point(0x1815ae0649042e153600b6498156527bed4f5d46c2b88725725d6f55103830d2, 0x1a399e82ca6f41312c8aad3ed2ad0dcbe690b8be19ca8bad457ba97188388f3f);
    vk.C = Pairing.G2Point([0x2676ddbe277cf3b73f7acfda3849d44273f2b5c0ddc2eaaa3b38e16784b6de54, 0xdf45e33a230ba206aeaeee9adfac143c99b6acc732b8267981ce18b9f189553], [0xd1a25a3d6e377ceb40377075ca189fb19601726544a4afe27e71b17e2521958, 0x12be9d577f1a3ec7d7b34f2298d5c85b1fe6c0785904655adcf2dfef18738017]);
    vk.gamma = Pairing.G2Point([0x1a3492627bce4f7fc7aea0e0990f7a775c39aaf7d125a673b9aa0ee81d25d71b, 0x27745b98949916c14df5808c6978f6597095f7f88d9238f8a9ae6676892dfc47], [0x1f2886339f0949382f83a3cce958e36861cff5c04844d63d67ff5e7279beb2cd, 0x11af8d98edf5418116208b5dd1d383627ed7d95e45b8938436e4805acb315c6c]);
    vk.gammaBeta1 = Pairing.G1Point(0x60539a5f0f35aa5ce85fc3042b45cdef726e3cb0536b9674274c3a203861a49, 0xc867e44f1d14ba0a4a2eb69351fbc33278cb83b5d14e4a8232936d2f1bf7689);
    vk.gammaBeta2 = Pairing.G2Point([0x1279f64c6d66201b43502443341fccdd46fa722c579aebb533b94c5e73c7c4ed, 0x2f5a6284435a7f1d2d278264f608cf92c800f88c0597342e6c95a2452bad7b2e], [0xd2158ac446f44fabad5bddb71a2e92cea6b6c25d4449ed4ed08e838dc65d1eb, 0x236bcc7f040fc13e3bdceb920cc98c09d769af21a1870dd77676731383950f51]);
    vk.Z = Pairing.G2Point([0x406e18e9abb8192ed39781d2be46d92ba48c44b60ad4902db8be4ad785f15cf, 0x2b20acab4041ccc00a0f8ef710254039edcecf6fc2344e61d51104b1a5cbd425], [0x1fe414c34eecf0f686813be15b02f94698c3b69f3c2973499839d9097e6c32f3, 0x792539bb74d9c104768747d23022a5f7a0810981c9021ea6cc443bd12c0b154]);
    vk.IC = new Pairing.G1Point[](13);
    vk.IC[0] = Pairing.G1Point(0x27175f6fd1638752b9d5fea4b5f671dfe240bb70f20789d2c327a87945db364f, 0x1ca68df96967ee371a29edb66b33ae62710eae05676e1b0e3b807fbc55ae8c5);
    vk.IC[1] = Pairing.G1Point(0x1d5c4c560a2220ef76192c0480b365deab67561f9327d7ede59b339d1b0d0c5, 0x1e8dbb22003c52f3a0d3f2d3836ac75f7c6e5ed4463d2571d6bbafa9152b75ec);
    vk.IC[2] = Pairing.G1Point(0x118bc49a6c5c410f5c7c1fb019d7e6fb081fe67e350b86f2415452de75bae4aa, 0x2dae87c1e01f1f258c40ab08cd65fe2826bdd89c9bef5493ad26085e74441118);
    vk.IC[3] = Pairing.G1Point(0x13518290041661d43fba4f12023ab24c54c73018c860b1b0d2a4a933d4626b16, 0x1f5a109846373ee32561521be5e43613a049dd3eebb7347376417d1058cab5e6);
    vk.IC[4] = Pairing.G1Point(0x1eb29c4cbb5bcc2a55074be6b7aae8bc99777e7e6966543cc0a36a2ee976308c, 0x2d5c27bf23b90411e1d3973043066f32d464fbb8dbad731bb363ce55cd473004);
    vk.IC[5] = Pairing.G1Point(0x1be1dfebef69306eb1b9e5a57a2b0966b89bb04812d05ada2cbfb8054cbf0aa5, 0x2dc694124045c7c7c5037a709b2b0670e24f5b9728aae3551a54dafbf6b0c043);
    vk.IC[6] = Pairing.G1Point(0x1c7c1bf5466330d5ec23cbf2fc4bbab0cb7f87a8a76945269a70c66ee604524a, 0x270a04e8096dc3374befacd53292a649b2a8e3fd4e1db8cb02dacb12d96a45af);
    vk.IC[7] = Pairing.G1Point(0x1b94b317f000c9af46dbd24ed3b612b062a82d0ba38b03f7da20a1ef8299e200, 0x1b79795487a977e02252dbd2c878ac2b4f784fb8f4eaacdc180441b672f8ccc8);
    vk.IC[8] = Pairing.G1Point(0x130efef699d36fd4dc1480e8c8a21cef098b7f610478827dcccbc6b31f5212c7, 0x20260e98fe9a310b3cb07168af6b9471472d279b94d2fb3163645a926c1c2883);
    vk.IC[9] = Pairing.G1Point(0x38b4a73b707d902ce1dd8ff7e78a3e5f2a4e63bc86951fcd179b721b75f8f5d, 0x14418b2177e0d3e953b4f083039c7e0dc7f7878e32b19970cb370583ccd84cbf);
    vk.IC[10] = Pairing.G1Point(0x277f3b3045bd7fe430543091dc538f4dbe5694d3c930983bf66d95310e13cfd8, 0xc4fc1716c6017eb7f107e3c27f1ac0b71b02483db7e5e8b69e0f5f8618fe849);
    vk.IC[11] = Pairing.G1Point(0x2e9f5901a11f3f249c5b6ec2415d17b0978469cfe57cf16f9594793c22a0201d, 0xe834ffbfd34eebe76f164c6be3e1495dfd7e80ec0bbc422d69bb03676f770aa);
    vk.IC[12] = Pairing.G1Point(0xa27f6f704fab4c7e107778206611bf672fb4ded37515e5ed6b017498c19a25c, 0x142f3f1a74a633080719a7411935e9c89dc8e5fba869405e1bd8f2d0c811df4d);
  }
  function verify(uint[] memory input, Proof memory proof) internal returns (uint) {
    VerifyingKey memory vk = verifyingKey();
    require(input.length + 1 == vk.IC.length);
    // Compute the linear combination vk_x
    Pairing.G1Point memory vk_x = Pairing.G1Point(0, 0);
    for (uint i = 0; i < input.length; i++)
      vk_x = Pairing.addition(vk_x, Pairing.scalar_mul(vk.IC[i + 1], input[i]));
    vk_x = Pairing.addition(vk_x, vk.IC[0]);
    if (!Pairing.pairingProd2(proof.A, vk.A, Pairing.negate(proof.A_p), Pairing.P2())) return 1;
    if (!Pairing.pairingProd2(vk.B, proof.B, Pairing.negate(proof.B_p), Pairing.P2())) return 2;
    if (!Pairing.pairingProd2(proof.C, vk.C, Pairing.negate(proof.C_p), Pairing.P2())) return 3;
    if (!Pairing.pairingProd3(
      proof.K, vk.gamma,
      Pairing.negate(Pairing.addition(vk_x, Pairing.addition(proof.A, proof.C))), vk.gammaBeta2,
      Pairing.negate(vk.gammaBeta1), proof.B
    )) return 4;
    if (!Pairing.pairingProd3(
        Pairing.addition(vk_x, proof.A), proof.B,
        Pairing.negate(proof.H), vk.Z,
        Pairing.negate(proof.C), Pairing.P2()
    )) return 5;
    return 0;
  }

  function verifyTx(
    uint[2] calldata a,
    uint[2] calldata a_p,
    uint[2][2] calldata b,
    uint[2] calldata b_p,
    uint[2] calldata c,
    uint[2] calldata c_p,
    uint[2] calldata h,
    uint[2] calldata k,
    uint[] calldata input
    ) external returns (bool r) {
    Proof memory proof;
    proof.A = Pairing.G1Point(a[0], a[1]);
    proof.A_p = Pairing.G1Point(a_p[0], a_p[1]);
    proof.B = Pairing.G2Point([b[0][0], b[0][1]], [b[1][0], b[1][1]]);
    proof.B_p = Pairing.G1Point(b_p[0], b_p[1]);
    proof.C = Pairing.G1Point(c[0], c[1]);
    proof.C_p = Pairing.G1Point(c_p[0], c_p[1]);
    proof.H = Pairing.G1Point(h[0], h[1]);
    proof.K = Pairing.G1Point(k[0], k[1]);
    uint[] memory inputValues = new uint[](input.length);
    for(uint i = 0; i < input.length; i++){
      inputValues[i] = input[i];
    }
    if (verify(inputValues, proof) == 0) {
      emit Verified("Transaction successfully verified.");
      return true;
    } else {
      return false;
    }
  }
}