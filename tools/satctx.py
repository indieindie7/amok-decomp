import sys, re, collections
# satctx.py <full_XLEM.c> <XLEMLAN1.BIN> <full_dos.c> <gn_dos.txt> <out_ctx> <out_slots>
# Saturn globals = RAM targets of SH-2 literal-pool slots. Per target: users, up to 5 usage lines, and hints = the
# DOS-named globals that the same-named DOS twin functions use. out_slots: "0x<slot> 0x<target>" for labelling p_<name>.
full, binp, dosc, gnd, oc, os_ = sys.argv[1:7]
b = open(binp, 'rb').read()
TOK = re.compile(r'\b_?(?:DAT|PTR_DAT)_([0-9a-f]{8})\b')
def target(v):
    o = v - 0x06004000
    if not (0 <= o <= len(b) - 4) or v % 4: return None
    p = int.from_bytes(b[o:o+4], 'big')
    if (0x06000000 <= p < 0x06100000 and not 0x06004000 <= p < 0x06004000 + len(b)) or 0x00200000 <= p < 0x00300000: return p
dn = {int(a, 16): n for a, n in (l.split() for l in open(gnd))}
dosuse = collections.defaultdict(list); fn = None
for l in open(dosc, encoding='utf-8', errors='replace'):
    m = re.match(r'// ==== (\S+) @', l)
    if m: fn = m.group(1); continue
    for a in TOK.findall(l):
        n = dn.get(int(a, 16))
        if fn and n and n not in dosuse[fn]: dosuse[fn].append(n)
users = collections.defaultdict(list); lines = collections.defaultdict(list); slots = {}; fn = None
for l in open(full, encoding='utf-8', errors='replace'):
    m = re.match(r'// ==== (\S+) @', l)
    if m: fn = m.group(1); continue
    if fn is None or l.lstrip().startswith(('/*', '*')): continue
    for a in set(TOK.findall(l)):
        v = int(a, 16); t = target(v)
        if t is None: continue
        slots[v] = t
        if fn not in users[t]:
            users[t].append(fn)
            if len(lines[t]) < 5: lines[t].append('  %s: %s' % (fn, l.strip()[:170].replace('DAT_%08x' % v, '[T]')))
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
