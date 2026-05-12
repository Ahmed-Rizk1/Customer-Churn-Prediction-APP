import sys, math, random, time

SBOX_AES = list(bytes.fromhex("637c777bf26b6fc53001672bfed7ab76ca82c97dfa5947f0add4a2af9ca472c0b7fd9326363ff7cc34a5e5f171d8311504c723c31896059a071280e2eb27b27509832c1a1b6e5aa0523bd6b329e32f8453d100ed20fcb15b6acbbe394a4c58cfd0efaafb434d338545f9027f503c9fa851a3408f929d38f5bcb6da2110fff3d2cd0c13ec5f974417c4a77e3d645d197360814fdc222a908846eeb814de5e0bdb10a0323a0a4906245cc2d3ac629195e479e7c8376d8dd54ea96c56f4ea657aae08ba78252e1ca6b4c6e8dd741f4bbd8b8a703eb5664803f60e613557b986c11d9e"))
INV_SBOX_AES = [0]*256
for i, v in enumerate(SBOX_AES): INV_SBOX_AES[v] = i
RCON = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x36]

def sub_bytes(state, inv=False):
    box = INV_SBOX_AES if inv else SBOX_AES
    for i in range(16): state[i] = box[state[i]]

def shift_rows(s, inv=False):
    if not inv:
        s[1], s[5], s[9], s[13] = s[5], s[9], s[13], s[1]
        s[2], s[6], s[10], s[14] = s[10], s[14], s[2], s[6]
        s[3], s[7], s[11], s[15] = s[15], s[3], s[7], s[11]
    else:
        s[1], s[5], s[9], s[13] = s[13], s[1], s[5], s[9]
        s[2], s[6], s[10], s[14] = s[10], s[14], s[2], s[6]
        s[3], s[7], s[11], s[15] = s[7], s[11], s[15], s[3]

def gmul(a, b):
    p = 0
    for _ in range(8):
        if b & 1: p ^= a
        hi = a & 0x80
        a = (a << 1) & 0xFF
        if hi: a ^= 0x1B
        b >>= 1
    return p

def mix_single(col, inv=False):
    c0, c1, c2, c3 = col
    if not inv:
        col[0] = gmul(2, c0) ^ gmul(3, c1) ^ c2 ^ c3
        col[1] = c0 ^ gmul(2, c1) ^ gmul(3, c2) ^ c3
        col[2] = c0 ^ c1 ^ gmul(2, c2) ^ gmul(3, c3)
        col[3] = gmul(3, c0) ^ c1 ^ c2 ^ gmul(2, c3)
    else:
        col[0] = gmul(14, c0) ^ gmul(11, c1) ^ gmul(13, c2) ^ gmul(9, c3)
        col[1] = gmul(9, c0) ^ gmul(14, c1) ^ gmul(11, c2) ^ gmul(13, c3)
        col[2] = gmul(13, c0) ^ gmul(9, c1) ^ gmul(14, c2) ^ gmul(11, c3)
        col[3] = gmul(11, c0) ^ gmul(13, c1) ^ gmul(9, c2) ^ gmul(14, c3)

def mix_columns(s, inv=False):
    for i in range(4):
        col = [s[i*4], s[i*4+1], s[i*4+2], s[i*4+3]]
        mix_single(col, inv)
        s[i*4], s[i*4+1], s[i*4+2], s[i*4+3] = col

def add_round_key(s, k):
    for i in range(16): s[i] ^= k[i]

def key_expansion(key):
    keys = list(key)
    for i in range(16, 176, 4):
        temp = keys[i-4:i]
        if i % 16 == 0:
            temp = [temp[1], temp[2], temp[3], temp[0]]
            temp = [SBOX_AES[b] for b in temp]
            temp[0] ^= RCON[i//16 - 1]
        keys.extend([keys[i-16+j] ^ temp[j] for j in range(4)])
    return [keys[i:i+16] for i in range(0, 176, 16)]

def aes_encrypt(pt, key):
    keys = key_expansion(key)
    state = list(pt)
    add_round_key(state, keys[0])
    for r in range(1, 10):
        sub_bytes(state)
        shift_rows(state)
        mix_columns(state)
        add_round_key(state, keys[r])
    sub_bytes(state)
    shift_rows(state)
    add_round_key(state, keys[10])
    return state

def aes_decrypt(ct, key):
    keys = key_expansion(key)
    state = list(ct)
    add_round_key(state, keys[10])
    shift_rows(state, inv=True)
    sub_bytes(state, inv=True)
    for r in range(9, 0, -1):
        add_round_key(state, keys[r])
        mix_columns(state, inv=True)
        shift_rows(state, inv=True)
        sub_bytes(state, inv=True)
    add_round_key(state, keys[0])
    return state

if __name__ == "__main__":
    print("\n# === Q3: AES-128 ===")
    aes_k = [0x2b,0x7e,0x15,0x16,0x28,0xae,0xd2,0xa6,0xab,0xf7,0x15,0x88,0x09,0xcf,0x4f,0x3c]
    aes_p = [0x32,0x43,0xf6,0xa8,0x88,0x5a,0x30,0x8d,0x31,0x31,0x98,0xa2,0xe0,0x37,0x07,0x34]
    aes_c = aes_encrypt(aes_p, aes_k)
    aes_d = aes_decrypt(aes_c, aes_k)
    print(f"PT:  {[hex(x) for x in aes_p]}")
    print(f"CT:  {[hex(x) for x in aes_c]}")
    print(f"DEC: {[hex(x) for x in aes_d]}")
    print("SUCCESS" if aes_p == aes_d else "FAILURE")
