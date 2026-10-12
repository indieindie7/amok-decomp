import sys, re, collections, difflib
# glmap2.py <src.c> <dst.c> <out> [satbin]: map DAT_ globals between builds. For each twin function (same name in both
# dumps) the lines are normalised (globals -> G, hex/numbers -> N, locals -> V) and matched with difflib; in matching
# lines the globals are paired in order. Votes per (src,dst); keep 1:1 pairs with a clear majority.
# satbin: dst literal-pool slots (SH-2, base 0x06004000) are resolved to the RAM pointer they hold.
TOK = re.compile(r'\b_?(?:DAT|PTR_DAT)_([0-9a-f]{8})\b')
def norm(l):
    l = TOK.sub('G', l)
    l = re.sub(r'\b(?:[a-z]{1,3}Var\d+|param_\d+|local_[0-9a-f]+|in_\w+|unaff_\w+|extraout_\w+)\b', 'V', l)
    l = re.sub(r'\b(?:0x[0-9a-f]+|\d+)\b', 'N', l)
    l = re.sub(r'\((?:u?int|u?short|u?char|undefined\d?|byte|code|short|int|char)\s*\**\)', '', l)
    return re.sub(r'[\s*&()]+', '', l)
def load(path, blob=None):
    d = collections.defaultdict(list); fn = None
    for l in open(path, encoding='utf-8', errors='replace'):
        m = re.match(r'// ==== (\S+) @', l)
        if m: fn = m.group(1); continue
        if fn is None or l.lstrip().startswith(('/*', '*')): continue
        g = []
        for a in TOK.findall(l):
            v = int(a, 16)
            if blob is not None:
                o = v - 0x06004000
                if 0 <= o <= len(blob) - 4:
                    p = int.from_bytes(blob[o:o+4], 'big') if v % 2 == 0 else 0
                    v = p if (0x06000000 <= p < 0x06100000 and not 0x06004000 <= p < 0x06004000 + len(blob)) or 0x00200000 <= p < 0x00300000 else None
            g.append(v)
        if TOK.search(l): d[fn].append((norm(l), g))
    return d
blob = open(sys.argv[4], 'rb').read() if len(sys.argv) > 4 else None
src = load(sys.argv[1]); dst = load(sys.argv[2], blob)
votes = collections.Counter()
for f in src:
    if f not in dst: continue
    a = [x[0] for x in src[f]]; b = [x[0] for x in dst[f]]
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    for i, j, n in sm.get_matching_blocks():
        for k in range(n):
            ga, gb = src[f][i+k][1], dst[f][j+k][1]
            if len(ga) == len(gb):
                for x, y in zip(ga, gb):
                    if y is not None: votes[(x, y)] += 1
bys = collections.defaultdict(collections.Counter); byd = collections.defaultdict(collections.Counter)
for (x, y), n in votes.items(): bys[x][y] += n; byd[y][x] += n
out = []
for x, c in bys.items():
    y, n = c.most_common(1)[0]
    if n * 2 > sum(c.values()) and byd[y].most_common(1)[0][0] == x:
        out.append((x, y, n, sum(c.values())))
with open(sys.argv[3], 'w') as o:
    for x, y, n, t in sorted(out): o.write('0x%08x 0x%08x votes %d of %d\n' % (x, y, n, t))
print('mapped', len(out), 'of', len(bys), 'src globals; dst distinct', len(byd))
