#include <bits/stdc++.h>
using namespace std;

using U64 = unsigned long long;

static inline U64 set_bit(int sq) {
    return 1ULL << sq;
}

static U64 random_u64() {
    U64 u1 = ((U64)rand()) & 0xFFFF;
    U64 u2 = ((U64)rand()) & 0xFFFF;
    U64 u3 = ((U64)rand()) & 0xFFFF;
    U64 u4 = ((U64)rand()) & 0xFFFF;
    return u1 | (u2 << 16) | (u3 << 32) | (u4 << 48);
}

static U64 random_magic_candidate() {
    return random_u64() & random_u64() & random_u64();
}

// ============================================================
// Mask generation (rook / bishop)
// ============================================================

static U64 mask_rook(int sq) {
    U64 mask = 0ULL;
    int r = sq / 8;
    int f = sq % 8;

    for(int r2 = r + 1; r2 <= 6; r2++) mask |= set_bit(r2*8 + f);
    for(int r2 = r - 1; r2 >= 1; r2--) mask |= set_bit(r2*8 + f);
    for(int f2 = f + 1; f2 <= 6; f2++) mask |= set_bit(r*8 + f2);
    for(int f2 = f - 1; f2 >= 1; f2--) mask |= set_bit(r*8 + f2);

    return mask;
}

static U64 mask_bishop(int sq) {
    U64 mask = 0ULL;
    int r = sq / 8;
    int f = sq % 8;

    for(int r2=r+1, f2=f+1; r2<=6 && f2<=6; r2++, f2++) mask |= set_bit(r2*8 + f2);
    for(int r2=r+1, f2=f-1; r2<=6 && f2>=1; r2++, f2--) mask |= set_bit(r2*8 + f2);
    for(int r2=r-1, f2=f+1; r2>=1 && f2<=6; r2--, f2++) mask |= set_bit(r2*8 + f2);
    for(int r2=r-1, f2=f-1; r2>=1 && f2>=1; r2--, f2--) mask |= set_bit(r2*8 + f2);

    return mask;
}

static vector<int> bits_of(U64 mask) {
    vector<int> out;
    for(int i=0;i<64;i++) {
        if(mask & (1ULL << i)) out.push_back(i);
    }
    return out;
}

static U64 index_to_occupancy(int index, const vector<int> &bits) {
    U64 occ = 0ULL;
    for(size_t i=0; i<bits.size(); i++) {
        if(index & (1 << i))
            occ |= (1ULL << bits[i]);
    }
    return occ;
}

// ============================================================
// Sliding attack generation
// ============================================================

static U64 rook_attacks(int sq, U64 occ) {
    U64 attacks = 0ULL;
    int r = sq / 8, f = sq % 8;

    for(int r2=r+1;r2<8;r2++){
        int s = r2*8+f;
        attacks |= set_bit(s);
        if(occ & set_bit(s)) break;
    }
    for(int r2=r-1;r2>=0;r2--){
        int s = r2*8+f;
        attacks |= set_bit(s);
        if(occ & set_bit(s)) break;
    }
    for(int f2=f+1;f2<8;f2++){
        int s = r*8+f2;
        attacks |= set_bit(s);
        if(occ & set_bit(s)) break;
    }
    for(int f2=f-1;f2>=0;f2--){
        int s = r*8+f2;
        attacks |= set_bit(s);
        if(occ & set_bit(s)) break;
    }
    return attacks;
}

static U64 bishop_attacks(int sq, U64 occ) {
    U64 attacks = 0ULL;
    int r = sq / 8, f = sq % 8;

    for(int r2=r+1,f2=f+1; r2<8 && f2<8; r2++,f2++){
        int s=r2*8+f2;
        attacks |= set_bit(s);
        if(occ & set_bit(s)) break;
    }
    for(int r2=r+1,f2=f-1; r2<8 && f2>=0; r2++,f2--){
        int s=r2*8+f2;
        attacks |= set_bit(s);
        if(occ & set_bit(s)) break;
    }
    for(int r2=r-1,f2=f+1; r2>=0 && f2<8; r2--,f2++){
        int s=r2*8+f2;
        attacks |= set_bit(s);
        if(occ & set_bit(s)) break;
    }
    for(int r2=r-1,f2=f-1; r2>=0 && f2>=0; r2--,f2--){
        int s=r2*8+f2;
        attacks |= set_bit(s);
        if(occ & set_bit(s)) break;
    }
    return attacks;
}

// ============================================================
// Magic search
// ============================================================

static U64 find_magic(int sq, bool rook) {
    U64 mask = rook ? mask_rook(sq) : mask_bishop(sq);
    auto bits = bits_of(mask);
    int relevant_bits = bits.size();
    int occ_count = 1 << relevant_bits;

    vector<U64> occ(occ_count);
    vector<U64> attacks(occ_count);

    for(int i=0;i<occ_count;i++) {
        occ[i] = index_to_occupancy(i,bits);
        attacks[i] = rook ? rook_attacks(sq, occ[i]) : bishop_attacks(sq, occ[i]);
    }

    while(true) {
        U64 magic = random_magic_candidate();
        unordered_map<U64,U64> used;

        bool fail = false;
        for(int i=0;i<occ_count;i++) {
            U64 idx = (occ[i] * magic) >> (64 - relevant_bits);
            if(used.count(idx) && used[idx] != attacks[i]) {
                fail = true;
                break;
            }
            used[idx] = attacks[i];
        }
        if(!fail)
            return magic;
    }
}

// ============================================================
// Python output
// ============================================================

int main() {
    srand(time(NULL));

    vector<U64> rook_magics(64);
    vector<U64> bishop_magics(64);

    cout << "# Auto-generated magic numbers\n";
    cout << "ROOK_MAGICS = [\n";
    for(int sq=0; sq<64; sq++) {
        rook_magics[sq] = find_magic(sq, true);
        cout << "    0x" << hex << rook_magics[sq] << "," << endl;
    }
    cout << "]\n\n";

    cout << "BISHOP_MAGICS = [\n";
    for(int sq=0; sq<64; sq++) {
        bishop_magics[sq] = find_magic(sq, false);
        cout << "    0x" << hex << bishop_magics[sq] << "," << endl;
    }
    cout << "]\n";

    return 0;
}
