from __future__ import print_function
import unittest
from binascii import hexlify, unhexlify
from .ed25519_oop import SigningKey, VerifyingKey

class KnownAnswerTests(unittest.TestCase):
    def test_all(self):
        # kat-ed25519.txt comes from "sign.input" on ed25519.cr.yp.to . The
        # btco-python ed25519.py in the same distribution uses a very
        # different key format than the one used by NaCl.
        lines = list(open("btco25519/kat-ed25519.txt"))
        for i,line in enumerate(lines):
            if not i%50: print("%d/%d" % (i, len(lines)))
            x = line.split(":")
            A,B,C,D = [unhexlify(i) for i in x[:4]]
            # A[:32] is the 32 byte seed (the entropy input to H())
            # A[32:] == B == the public point (pubkey)
            # C is the message
            # D is 64 bytes of signature (R+S) prepended to the message

            seed = A[:32]
            vk_s = B
            # the NaCl signature is R+S, which happens to be the same as ours
            msg = C
            sig = D[:64] # R+S
            # note that R depends only upon the second half of H(seed). S
            # depends upon both the first half (the exponent) and the second
            # half

            #if len(msg) % 16 == 1:
            #    print "msg len = %d" % len(msg), time.time()

            sk = SigningKey(seed)
            vk = sk.get_verifying_key()
            self.failUnlessEqual(vk.to_bytes(), vk_s)
            vk2 = VerifyingKey(vk_s)
            self.failUnlessEqual(vk2, vk) # objects should compare equal
            self.failUnlessEqual(vk2.to_bytes(), vk_s)
            newsig = sk.sign(msg) # R+S
            self.failUnlessEqual(hexlify(newsig), hexlify(sig)) # deterministic sigs
            self.failUnlessEqual(vk.verify(sig, msg), None) # no exception


if __name__ == '__main__':
    unittest.main()
