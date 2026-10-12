import sys, re, collections
# weakctx.py <full.c> <globals.txt> <out> [prefix]: context for weak global names (address suffix or unk) after the names
# are applied: up to 5 usage lines (one per function), the global shown as [T]; prefix = also match <prefix><name>(_N) labels
# (Saturn pool slots p_<name>).
src, gl, out = sys.argv[1:4]; pre = sys.argv[4] if len(sys.argv) > 4 else None
weak = []
for l in open(gl, encoding='utf-8'):
    a, n = l.split()
    if n.startswith('p_'): continue
    if re.search(r'_[0-9a-f]{4}$', n) or 'unk' in n: weak.append((a, n))
use = collections.defaultdict(dict)
pats = {n: re.compile(r'\b_?(?:%s)?%s(?:_\d+)?\b' % (re.escape(pre) if pre else '', re.escape(n))) for a, n in weak}
fn = None; incom = False
for l in open(src, encoding='utf-8', errors='replace'):
    m = re.match(r'// ==== (\S+) @', l)
    if m: fn = m.group(1); continue
    s = l.strip()
    if incom:
        if '*/' in s: incom = False
        continue
    if s.startswith('/*'):
        incom = '*/' not in s; continue
    if fn is None: continue
    for a, n in weak:
        u = use[n]
        if fn not in u and len(u) < 5 and n in l and pats[n].search(l): u[fn] = pats[n].sub('[T]', s)[:200]
with open(out, 'w', newline='\n') as o:
    for a, n in weak:
        o.write('%s %s\n' % (a, n))
        for f, s in use[n].items(): o.write('  %s: %s\n' % (f, s))
print(len(weak), 'weak;', sum(1 for a, n in weak if not use[n]), 'with no use found')
