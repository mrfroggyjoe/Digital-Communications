import random

def ISHFTC(n, d, N):  
    return ((n << d) % (1 << N)) | (n >> (N - d))

def ISHFTCC(n, d, N):
    return ISHFTC(n, N - d, N)

c = ISHFTC(7,7,8)
#print(bin(c))

B = 64

key = random.randint(0,2**B-1)
message = 202620252024


def encrypt(m,k):
    c = m
    shift = k.bit_count()
    for i in range(shift):
        c = ISHFTC(c,shift,B)
        c = c ^ k
        c = ISHFTC(c,shift,B)
        #print(c)
    return c

def decrypt(c,k):
    m = c
    shift = k.bit_count()
    for i in range(shift):
        m = ISHFTCC(m,shift,B)
        m = m ^ k
        m = ISHFTCC(m,shift,B)
        #print(m)
    return m


c = encrypt(message,key)
print("Transmitted Message: ",c)
print(f"{c:064b}")
print("Final Decrypted Message",decrypt(c,key))
print(f"{decrypt(c,key):064b}")