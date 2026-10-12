import sys, re, collections
# satglob.py <gn_sat_*.txt...> <sat_slots.txt> <hand_XLEMLAN1.txt> <out>: Saturn globals file = the RAM target names
# + one p_<name> label per literal-pool slot that holds the target's address (extra slots of a target get _2, _3...).
*gns, slots, hand, out = sys.argv[1:]
names = {}
for f in gns:
    for l in open(f, encoding='utf-8'):
        p = l.split()
        if len(p) == 2: names[int(p[0], 16)] = p[1]
funcs = {l.split()[2] for l in open(hand, encoding='utf-8') if len(l.split()) > 2}
used = set(funcs); lines = []
def take(n):
    b, i = n, 2
    while n in used: n = '%s_%d' % (b, i); i += 1
    used.add(n); return n
for a in sorted(names):
    n = names[a] if names[a] not in funcs else names[a] + '_var'
    lines.append((a, take(n if n not in used else '%s_%04x' % (n, a & 0xffff))))
tn = dict(lines); miss = set()
for l in open(slots):
    s, t = (int(x, 16) for x in l.split())
    if t in tn: lines.append((s, take('p_' + tn[t])))
    else: miss.add(t)
with open(out, 'w', newline='\n') as o:
    for a, n in sorted(lines): o.write('0x%08x %s\n' % (a, n))
print('targets', len(names), 'labels', len(lines), 'slot targets without a name', len(miss))
