import sys, re, collections
# glctx.py <full.c> <gl.txt> <out> [maxlines]: per global, up to N usage lines (one per function) for naming agents.
mx = int(sys.argv[4]) if len(sys.argv) > 4 else 5
want = {}
for l in open(sys.argv[2]):
    want[int(l.split()[0], 16)] = l.strip()
lines = collections.defaultdict(list); seen = collections.defaultdict(set); fn = None
for l in open(sys.argv[1], encoding='utf-8', errors='replace'):
    m = re.match(r'// ==== (\S+) @', l)
    if m: fn = m.group(1); continue
    if fn is None or l.startswith('/*') or l.startswith('   '): 
        if not (fn and 'DAT_' in l and not l.lstrip().startswith(('/*','*'))): continue
    for a in set(re.findall(r'\b_?(?:DAT|PTR_DAT|PTR_LAB|PTR_FUN)_([0-9a-f]{8})\b', l)):
        v = int(a, 16)
        if v in want and fn not in seen[v] and len(lines[v]) < mx:
            seen[v].add(fn); lines[v].append('  %s: %s' % (fn, l.strip()[:180]))
with open(sys.argv[3], 'w') as o:
    for v in sorted(want):
        o.write(want[v].split(':')[0] + '\n' + '\n'.join(lines[v]) + '\n')
