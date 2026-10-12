import sys, re, collections
# glscan.py <decomp.c> <out>: every DAT_/PTR_ global in a full CsDumpAll dump, ref count + user functions (in order of first use)
cnt = collections.Counter(); users = collections.defaultdict(list); fn = None
for l in open(sys.argv[1], encoding='utf-8', errors='replace'):
    m = re.match(r'// ==== (\S+) @', l)
    if m: fn = m.group(1); continue
    for a in re.findall(r'\b_?(?:DAT|PTR_DAT|PTR_LAB|PTR_FUN)_([0-9a-f]{8})\b', l):
        v = int(a, 16); cnt[v] += 1
        if fn not in users[v]: users[v].append(fn)
with open(sys.argv[2], 'w') as o:
    for v in sorted(cnt):
        u = users[v]
        o.write('0x%08x refs %d fns %d: %s\n' % (v, cnt[v], len(u), ' '.join(u[:8])))
print(len(cnt), 'addresses;', sum(1 for v in cnt if len(users[v]) >= 2), 'used by 2+ functions;', sum(cnt.values()), 'refs')
