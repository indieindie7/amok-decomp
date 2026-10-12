import sys
def load(p):
    F={};cur=None
    for l in open(p,errors='replace'):
        t=l.split()
        if not t: continue
        if t[0]=='F':
            cur=t[1];F[cur]={'name':t[2],'size':int(t[4]) if len(t)>4 and t[4].isdigit() else 0,'callees':[],'strs':set()}
        elif t[0]=='C' and cur: F[cur]['callees'].append(t[1])
        elif t[0]=='S' and cur: F[cur]['strs'].add(' '.join(t[2:]))
    return F
W=load(sys.argv[1]);D=load(sys.argv[2])
for a in sys.argv[3:]:
    a=a.lower().replace('0x','').zfill(8)
    f=W[a];cal=[W[c]['name'] for c in f['callees'] if c in W]
    named=set(c for c in cal if not c.startswith('FUN_'))
    best=[]
    for da,df in D.items():
        if df['size']<f['size']*0.7 or df['size']>f['size']*1.3: continue
        dc=set(D[c]['name'] for c in df['callees'] if c in D)
        if not named and not dc: continue
        j=len(named&dc)/max(1,len(named|dc))
        cc=1-abs(len(df['callees'])-len(f['callees']))/max(1,len(f['callees']))
        best.append((round(j*0.7+cc*0.3,2),df['name'],da,df['size'],len(df['callees'])))
    best.sort(reverse=True)
    print(f"{a} {f['name']} size={f['size']} calls={len(f['callees'])} named={sorted(named)}")
    for b in best[:3]: print("   ",b)
