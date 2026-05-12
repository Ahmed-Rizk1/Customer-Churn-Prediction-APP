import sys, math, random, time

# Extended Euclidean Algorithm
def egcd(a, b):
    if a == 0: return b, 0, 1
    g, y, x = egcd(b % a, a)
    return g, x - (b // a) * y, y

# Modular Inverse
def modinv(a, m):
    g, x, y = egcd(a, m)
    if g != 1: raise Exception("No modular inverse")
    return x % m

# Generate RSA public and private keys
def gen_rsa_keys(p, q):
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 3
    while math.gcd(e, phi) != 1: e += 2
    d = modinv(e, phi)
    return (e, n), (d, n)

# RSA Encrypt
def rsa_enc(m, pub):
    e, n = pub
    return pow(m, e, n)

# RSA Decrypt
def rsa_dec(c, priv):
    d, n = priv
    return pow(c, d, n)

if __name__ == "__main__":
    print("# === Q1: RSA ===")
    pub, priv = gen_rsa_keys(61, 53)
    msg = 65
    ct = rsa_enc(msg, pub)
    dec_msg = rsa_dec(ct, priv)
    print(f"Original: {msg}, Encrypted: {ct}, Decrypted: {dec_msg}")
    print("SUCCESS" if msg == dec_msg else "FAILURE")
