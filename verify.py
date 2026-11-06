"""Verify the 4-bit encryption/decryption circuit.

Re-creates both truth tables from the minimised Boolean equations used in the
circuits, checks them against the specification tables, and confirms that
decryption exactly reverses encryption for all 16 inputs.

Usage:
    python verify.py              # run all checks
    python verify.py --markdown   # also print the truth tables as Markdown
"""

import sys
from itertools import product

# Specification truth tables (input nibble -> output nibble), from the project brief.
ENCRYPTION_SPEC = {
    "0000": "0001", "0001": "1000", "0010": "0111", "0011": "1110",
    "0100": "1101", "0101": "0100", "0110": "0011", "0111": "1010",
    "1000": "1001", "1001": "0000", "1010": "1111", "1011": "0110",
    "1100": "0101", "1101": "1100", "1110": "1011", "1111": "0010",
}
DECRYPTION_SPEC = {cipher: plain for plain, cipher in ENCRYPTION_SPEC.items()}


def NOT(x):
    return 1 - x


def encrypt(A, B, C, D):
    """Minimised SOP equations from the K-maps (as built with NAND gates)."""
    W = ((NOT(A) & NOT(B) & D) | (A & NOT(B) & NOT(D)) | (NOT(A) & C & D)
         | (A & C & NOT(D)) | (NOT(A) & B & NOT(C) & NOT(D)) | (A & B & NOT(C) & D))
    X = (B & NOT(C)) | (NOT(B) & C)
    Y = C
    Z = NOT(D)
    return W, X, Y, Z


def decrypt(W, X, Y, Z):
    """Minimised SOP equations from the K-maps (as built with NAND gates)."""
    A = ((W & Y & Z) | (NOT(W) & Y & NOT(Z)) | (NOT(W) & NOT(X) & NOT(Z))
         | (W & X & NOT(Y) & NOT(Z)) | (NOT(W) & X & NOT(Y) & Z) | (W & NOT(X) & Z))
    B = (NOT(X) & Y) | (X & NOT(Y))
    C = Y
    D = NOT(Z)
    return A, B, C, D


def bits(n):
    return "".join(map(str, n))


def main():
    inputs = list(product([0, 1], repeat=4))
    checks = {
        "Encryption equations match the specification":
            all(bits(encrypt(*i)) == ENCRYPTION_SPEC[bits(i)] for i in inputs),
        "Decryption equations match the specification":
            all(bits(decrypt(*i)) == DECRYPTION_SPEC[bits(i)] for i in inputs),
        "Encryption is one-to-one (16 distinct outputs)":
            len({encrypt(*i) for i in inputs}) == 16,
        "decrypt(encrypt(x)) == x for all 16 inputs":
            all(decrypt(*encrypt(*i)) == i for i in inputs),
        "XOR form: W = A ^ D ^ (B & ~C)":
            all(encrypt(*i)[0] == i[0] ^ i[3] ^ (i[1] & NOT(i[2])) for i in inputs),
        "XOR form: A = W ^ ~Z ^ (X & ~Y)":
            all(decrypt(*i)[0] == i[0] ^ NOT(i[3]) ^ (i[1] & NOT(i[2])) for i in inputs),
    }

    for name, ok in checks.items():
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")

    if "--markdown" in sys.argv:
        print("\n| A B C D | → | W X Y Z | hex |")
        print("|:-------:|:-:|:-------:|:---:|")
        for i in inputs:
            o = encrypt(*i)
            print(f"| {' '.join(map(str, i))} | → | {' '.join(map(str, o))} "
                  f"| {int(bits(i), 2):X} → {int(bits(o), 2):X} |")

    sys.exit(0 if all(checks.values()) else 1)


if __name__ == "__main__":
    main()
