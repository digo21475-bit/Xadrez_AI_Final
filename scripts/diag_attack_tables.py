# diag_attack_tables.py
U64 = (1<<64) - 1
FILE_A = 0x0101010101010101
FILE_H = 0x8080808080808080

def bruteforce_pawn_attacks():
    white = [0]*64
    black = [0]*64
    for sq in range(64):
        f = sq & 7
        r = sq >> 3
        w = 0
        if r < 7:
            if f > 0: w |= 1 << ((r+1)*8 + (f-1))
            if f < 7: w |= 1 << ((r+1)*8 + (f+1))
        b = 0
        if r > 0:
            if f > 0: b |= 1 << ((r-1)*8 + (f-1))
            if f < 7: b |= 1 << ((r-1)*8 + (f+1))
        white[sq] = w & U64
        black[sq] = b & U64
    return white, black

def mask_pawn_attacks():
    white = [0]*64
    black = [0]*64
    for sq in range(64):
        bb = 1 << sq
        # Correct masks for A1=0 convention:
        w = ((bb << 7) & ~FILE_H) | ((bb << 9) & ~FILE_A)
        b = ((bb >> 9) & ~FILE_H) | ((bb >> 7) & ~FILE_A)
        white[sq] = w & U64
        black[sq] = b & U64
    return white, black

def popcount(x): return bin(x).count("1")

Wb, Bb = bruteforce_pawn_attacks()
Wm, Bm = mask_pawn_attacks()

mismatch = []
for i in range(64):
    if Wb[i] != Wm[i] or Bb[i] != Bm[i]:
        mismatch.append((i, Wb[i], Wm[i], Bb[i], Bm[i]))

print("Total bruteforce white popcount:", sum(popcount(x) for x in Wb))
print("Total mask white popcount:",      sum(popcount(x) for x in Wm))
print("Total bruteforce black popcount:", sum(popcount(x) for x in Bb))
print("Total mask black popcount:",      sum(popcount(x) for x in Bm))
print("Mismatches count:", len(mismatch))
if mismatch:
    print("First mismatches (sq, brutew, maskw, bruteb, maskb):")
    for t in mismatch[:10]:
        print(t)
