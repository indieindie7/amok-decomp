import sys, re, collections, bisect
# satctx.py <full_XLEM.c> <XLEMLAN1.BIN> <full_dos.c> <gn_dos.txt> <out_ctx> <out_slots> [funcinfo.tsv]
# Saturn globals = RAM targets of SH-2 literal-pool slots. Per target: users, up to 5 usage lines, and hints = the
# DOS-named globals that the same-named DOS twin functions use. out_slots: "0x<slot> 0x<target>" for labelling p_<name>.
full, binp, dosc, gnd, oc, os_ = sys.argv[1:7]
b = open(binp, 'rb').read()
# PTR_LAB_/PTR_FUN_: slots whose target Ghidra marked as a code label (data inside the binary on Scorcher LORT)
TOK = re.compile(r'\b_?(?:DAT|PTR_DAT|PTR_LAB|PTR_FUN)_([0-9a-f]{8})\b')
def target(v):
    o = v - 0x06004000
    if not (0 <= o <= len(b) - 4) or v % 4: return None
    p = int.from_bytes(b[o:o+4], 'big')
    if (0x06000000 <= p < 0x06100000 and not 0x06004000 <= p < 0x06004000 + len(b)) or 0x00200000 <= p < 0x00300000: return p
    if fbody is None: return None
    # [funcinfo.tsv] given (Scorcher LORT: the file spans high RAM, data/BSS inside it): data targets in the binary
    # that are no function body, and the cache-through mirror 0x2xxxxxxx of RAM (folded onto the cached address).
    if 0x20000000 <= p < 0x30000000: p -= 0x20000000
    if 0x06000000 <= p < 0x06100000 or 0x00200000 <= p < 0x00300000:
        i = bisect.bisect_right(fstart, p) - 1
        if i < 0 or p >= fbody[i]: return p
fbody = None
if len(sys.argv) > 7:
    fs = sorted((int(l.split()[1], 16), int(l.split()[4])) for l in open(sys.argv[7]) if l.startswith('F '))
    fstart = [a for a, n in fs]; fbody = [a + n for a, n in fs]
dn = {int(a, 16): n for a, n in (l.split() for l in open(gnd))}
dosuse = collections.defaultdict(list); fn = None
for l in open(dosc, encoding='utf-8', errors='replace'):
    m = re.match(r'// ==== (\S+) @', l)
    if m: fn = m.group(1); continue
    for a in TOK.findall(l):
        n = dn.get(int(a, 16))
        if fn and n and n not in dosuse[fn]: dosuse[fn].append(n)
users = collections.defaultdict(list); lines = collections.defaultdict(list); slots = {}; fn = None; incom = False
for l in open(full, encoding='utf-8', errors='replace'):
    m = re.match(r'// ==== (\S+) @', l)
    if m: fn = m.group(1); continue
    # strip comments like glscan (a "startswith('*')" skip also dropped real "*DAT_x = ..." stores)
    if incom:
        if '*/' not in l: continue
        incom = False; l = l.split('*/', 1)[1]
    l = re.sub(r'/\*.*?\*/', '', l)
    if '/*' in l: incom = True; l = l.split('/*', 1)[0]
    l = l.split('//', 1)[0]
    if fn is None: continue
    for a in set(TOK.findall(l)):
        v = int(a, 16); t = target(v)
        if t is None: continue
        slots[v] = t
        if fn not in users[t]:
            users[t].append(fn)
            if len(lines[t]) < 5: lines[t].append('  %s: %s' % (fn, re.sub(r'\b_?(?:DAT|PTR_DAT|PTR_LAB|PTR_FUN)_%08x\b' % v, '[T]', l.strip()[:170])))
with open(oc, 'w') as o:
    for t in sorted(users):
        hint = []
        for f in users[t][:3]:
            if dosuse.get(f): hint.append('%s->{%s}' % (f, ','.join(dosuse[f][:12])))
        o.write('0x%08x fns %d\n%s\n' % (t, len(users[t]), '\n'.join(lines[t])))
        if hint: o.write('  DOS twins use: ' + ' '.join(hint) + '\n')
with open(os_, 'w') as o:
    for s in sorted(slots): o.write('0x%08x 0x%08x\n' % (s, slots[s]))
print(len(users), 'targets', len(slots), 'slots')
