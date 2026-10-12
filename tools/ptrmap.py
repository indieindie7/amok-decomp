import sys,struct
exe=open('AMOKWIN95.exe','rb').read(); dos=open('../pc/amokdos.bin.bin','rb').read()
DELTA=0x7b4d4  # win95 file offset + DELTA = DOS data address (type table 0x4b998 <-> 0xc6e6c)
def names(p):
    n={}
    for l in open(p):
        t=l.split()
        if t and t[0]=='F': n[int(t[1],16)]=t[2]
    return n
W=names('funcinfo_AMOKWIN95.exe.tsv'); D=names('funcinfo_amokdos.bin.tsv')
lo,hi=int(sys.argv[1],16),int(sys.argv[2],16)
prop={}
for off in range(int(sys.argv[3],16),int(sys.argv[4],16),4):
    v=struct.unpack_from('<I',exe,off)[0]
    if not (lo<=v<hi) or v not in W: continue
    da=off+DELTA; do=da-0x10000
    if do<0 or do+4>len(dos): continue
    dv=struct.unpack_from('<I',dos,do)[0]
    dn=D.get(dv)
    prop.setdefault(v,[]).append((hex(off),hex(da),hex(dv),dn))
for v in sorted(prop):
    ns=set(p[3] for p in prop[v])
    flag='' if len(ns)==1 and None not in ns else ' CONFLICT'
    print(hex(v),W[v],sorted(str(n) for n in ns),len(prop[v]),flag)
