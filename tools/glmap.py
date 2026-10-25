import sys, re, collections
# glmap.py <src.c> <dst.c> <out> [satbin]: map DAT_ globals between builds through twin functions (same name in both dumps).
# Per function, the ordered list of distinct DAT_ refs; equal-length lists are zipped; votes per (src,dst).
# With satbin (XLEMLAN1.BIN, base 0x06004000) dst DAT_ literal-pool slots are resolved to the pointer they hold.
def load(path, satbin=None):
    d = {}; fn = None
    blob = open(satbin, 'rb').read() if satbin else None
    for l in open(path, encoding='utf-8', errors='replace'):
        m = re.match(r'// ==== (\S+) @', l)
        if m: fn = m.group(1); d.setdefault(fn, []); continue
        if fn is None: continue
        for a in re.findall(r'\b_?(?:DAT|PTR_DAT)_([0-9a-f]{8})\b', l):
            v = int(a, 16)
            if blob is not None:
                o = v - 0x06004000
                if 0 <= o <= len(blob) - 4 and v % 4 == 0:
                    p = int.from_bytes(blob[o:o+4], 'big')
                    if not (0x06004000 <= p < 0x06004000 + len(blob)) and (0x06000000 <= p < 0x06100000 or 0x00200000 <= p < 0x00300000 or 0x25000000 <= p < 0x26000000):
                        v = p
                    else: continue
                else: continue
            if v not in d[fn]: d[fn].append(v)
    return d
src = load(sys.argv[1]); dst = load(sys.argv[2], sys.argv[4] if len(sys.argv) > 4 else None)
votes = collections.Counter()
for f in src:
    if f in dst and len(src[f]) == len(dst[f]) and src[f]:
        for a, b in zip(src[f], dst[f]): votes[(a, b)] += 1
best = {}
for (a, b), n in votes.most_common():
    if a not in best: best[a] = (b, n)
taken = collections.Counter(b for b, n in best.values())
with open(sys.argv[3], 'w') as o:
    k = 0
    for a in sorted(best):
        b, n = best[a]
        tot = sum(v for (x, y), v in votes.items() if x == a)
        if taken[b] == 1 and n * 2 > tot:
            o.write('0x%08x 0x%08x votes %d of %d\n' % (a, b, n, tot)); k += 1
print('mapped', k, 'of', len(best), 'src addresses with votes')
