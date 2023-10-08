from random import randint
from numpy import fix, log, meshgrid, sqrt, floor, bitwise_xor, empty, uint8
from scipy.stats import entropy
from collections import Counter
from math import log2
from sys import argv
from cv2 import imread, cvtColor, COLOR_BGR2GRAY
from imageio.v2 import imread as imread_v2
from imageio.v2 import imwrite as imwrite_v2
from os import remove

def convertTo1d(tab2d):
    tab1d = []
    x = tab2d.shape[0]**2
    for j in range(0, tab2d.shape[0]):
        for i in range(0, tab2d.shape[1]):
            tab1d.append(tab2d[j][i])
            x -= 1
        if(x <= 0):
            break
    return tab1d

def getGcd(x, y):
    while(y):
        x, y = y, x % y
    return x

def getRsa(p, q):
    phi_of_n = (p - 1) * (q - 1)
    e = randint(2, phi_of_n)
    while(getGcd(e, phi_of_n) != 1):
        e = randint(2, phi_of_n)
    d = pow(e, -1) % phi_of_n
    return e, d

def RSA(p, q):
    n = p*q

    e, d = getRsa(p, q)

    x01 = randint(0, 1000)
    x02 = randint(0, 1000)
    x03 = randint(0, 1000)
    x04 = randint(0, 1000)

    y01 = x01 + x02
    y02 = x02 + x03
    y03 = x03 + x04
    y04 = x01 + x04

    c01 = pow(y01, e) % n
    c02 = pow(y02, e) % n
    c03 = pow(y03, e) % n
    c04 = pow(y04, e) % n

    return fix(x01+sqrt(log(c01+y01))), fix(x02+sqrt(log(c02+y02))), fix(x03+sqrt(log(c03+y03))), fix(x04+sqrt(log(c04+y04)))

def generalizedArnoldMap(a, b, P):
    N = P.shape[0]
    M = P.shape[1]

    x, y = meshgrid(range(N), range(M))
    X = (x+b*y) % N
    Y = (a*x+y*(a*b+1)) % M
    P = P[X, Y]
    C = P
    return C

def generateChaoticSequences(P, p=1619 ,q=1621):
    a1, b1, a2, b2 = RSA(p, q)
    s = generalizedArnoldMap(int(a1), int(b1), P)
    r = generalizedArnoldMap(int(a2), int(b2), P)
    S = P.ravel()
    R = P.ravel()
    for i in range(0, s.shape[0]):
        for j in range(0, s.shape[1]):
            S[i+j] = ((floor((s[i][j]+100)*(10**14))) % 256)

    for i in range(0, r.shape[0]):
        for j in range(0, r.shape[1]):
            R[i+j] = ((floor((r[i][j]+100)*(10**14))) % 256)
    return S, R

def obtainImageA(P, S):
    P = P.ravel()
    A = P.ravel()
    for i in range(0, A.size-1):
        A[i] = 0
    A[0] = bitwise_xor(P[0], S[0])

    for i in range(1, A.size-1):
        A[i] = bitwise_xor(A[i-1], bitwise_xor(P[i], S[i]))

    return A

def scrambling(S,A):
    S=S.reshape(A.shape[0],A.shape[1])
    
    X=empty(A.shape[0])
    for i in range(0,A.shape[0]):
        X[i]=S[i][0]
    X.sort()

    Y=empty(A.shape[1])
    for i in range(0,A.shape[1]):
        Y[i]=S[0][i]
    Y.sort()

    F=bitwise_xor(A,S)

    B=empty([A.shape[0],A.shape[1]])
    for i in range(0,A.shape[0]):
        x = X[i].astype(int) if X[i].astype(int) < A.shape[0] else A.shape[0]-1
        for j in range(0,A.shape[1]):
            y = Y[j].astype(int) if Y[j].astype(int) < A.shape[1] else A.shape[1]-1
            B[x][y] = F[i][j]

    return B

def obtainImageC(B, R):
    N = B.shape[0]
    M = B.shape[1]
    B = B.ravel()
    C = empty((B.size))

    C[0] = (B[0]+R[0]) % 255

    for i in range(1, B.size):
        C[i] = (C[i-1]+B[i]+R[i]) % 256
    C = C.reshape(N, M)
    return C

def encryption(imageToEncrypt):
    p = 1619
    q = 1621
    S, R = generateChaoticSequences(imageToEncrypt.copy(), p, q)
    A = obtainImageA(imageToEncrypt.copy(), S)
    B = scrambling(S, A.reshape(
        imageToEncrypt.shape[0], imageToEncrypt.shape[1]))
    C = obtainImageC(B, R)
    return C

def getRandom(source):
    C = encryption(source.copy())

    imwrite_v2('resultFromGeneratorTemp.png', C.astype(uint8))
    temp = imread_v2('resultFromGeneratorTemp.png')
    remove('resultFromGeneratorTemp.png')
    if(entropy(temp) < 7.999):
        C = encryption(temp.copy())
    imwrite_v2('resultFromGenerator.png', C.astype(uint8))



if __name__ == "__main__":
    sourceGenerator = imread(argv[1])
    sourceGenerator = cvtColor(sourceGenerator, COLOR_BGR2GRAY)
    getRandom(sourceGenerator)
