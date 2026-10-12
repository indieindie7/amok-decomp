import sys, re
# wkmerge.py <globals.txt> <wn.txt> <hand.txt> <out>: put refined names (wn = "0x<addr> <name>") into a globals file.
# A new name that is taken (other global or function) gets _<last4hex>. Prints the rename count.
gl, wn, hand, out = sys.argv[1:]
rows = [l.split() for l in open(gl, encoding='utf-8') if l.strip()]
new = {}
for l in open(wn, encoding='utf-8'):
    p = l.split()
    if len(p) == 2 and re.fullmatch(r'[A-Za-z_]\w*', p[1]): new[p[0]] = p[1]
funcs = {l.split()[2] for l in open(hand, encoding='utf-8') if len(l.split()) > 2}
keep = {n for a, n in rows if new.get(a, n) == n}
used = set(funcs) | keep; ch = 0
for r in rows:
    if r[0] not in new or new[r[0]] == r[1]: continue
    n = new[r[0]]
    if n in used: n = '%s_%s' % (n, r[0][-4:])
    if n in used: used.add(r[1]); continue
    used.add(n); r[1] = n; ch += 1
with open(out, 'w', newline='\n') as o:
    for r in rows: o.write(' '.join(r) + '\n')
print('renamed', ch, 'of', len(new))
