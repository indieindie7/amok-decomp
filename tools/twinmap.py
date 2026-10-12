# twinmap.py <funcinfo_src.tsv> <funcinfo_dst.tsv> <xalign_dst.txt> <out.txt> [srclabel]
# Propagates names from a fully named build (src) to its sibling Watcom build (dst)
# by function order between xalign anchors, verified by size, call count and strings.
import sys
def load(p):
    fs=[];cur=None
    for line in open(p,encoding="utf-8",errors="replace"):
        t=line.rstrip("\n").split(" ",1)
        if t[0]=="F":
            a,n,s,z=t[1].split(" ");cur=dict(addr=int(a,16),name=n,src=s,size=int(z),calls=[],strs=[]);fs.append(cur)
        elif t[0]=="C" and cur: cur["calls"].append(int(t[1].split(":")[-1],16))
        elif t[0]=="S" and cur: cur["strs"].append(t[1])
    fs.sort(key=lambda f:f["addr"]);return fs
src=load(sys.argv[1]);dst=load(sys.argv[2]);lab=sys.argv[5] if len(sys.argv)>5 else "src"
si={f["addr"]:i for i,f in enumerate(src)};di={f["addr"]:i for i,f in enumerate(dst)}
pairs={}  # dst index -> src index
for line in open(sys.argv[3]):
    t=line.split()
    if len(t)<5: continue
    d=int(t[0],16);s=int(t[4].split(":")[1],16)
    if d in di and s in si: pairs[di[d]]=si[s]
from collections import Counter
cs=Counter(f["name"] for f in src);cd=Counter(f["name"] for f in dst)
for i,f in enumerate(dst):
    n=f["name"]
    if n.startswith(("FUN_","fn_","s_")) or cd[n]!=1 or cs.get(n)!=1: continue
    j=next(k for k,g in enumerate(src) if g["name"]==n)
    pairs.setdefault(i,j)
print("anchors",len(pairs))
def ok(a,b):
    if len(a["calls"])!=len(b["calls"]): return False
    if a["size"]<8 or b["size"]<8: return False
    for ca,cb in zip(a["calls"],b["calls"]):
        if ca in di and cb in si and di[ca] in pairs and pairs[di[ca]]!=si[cb]: return False
    big=max(a["size"],b["size"]);
    if abs(a["size"]-b["size"])>max(8,big//5): return False
    sa=set(a["strs"]);sb=set(b["strs"])
    if sa and sb and sa!=sb: return False
    if (sa and not sb) or (sb and not sa): return False
    return True
def namecalls(f,fs,idx):
    return [fs[idx[c]]["name"] if c in idx else "?" for c in f["calls"]]
added=1;rounds=0
while added:
    added=0;rounds+=1
    keys=sorted(pairs)
    for k in keys:
        s=pairs[k]
        for step in (1,-1):
            d2=k+step;s2=s+step
            while 0<=d2<len(dst) and 0<=s2<len(src) and d2 not in pairs:
                if ok(dst[d2],src[s2]) and src[s2]["name"] and not src[s2]["name"].startswith("FUN_"):
                    pairs[d2]=s2;added+=1;d2+=step;s2+=step
                else: break
print("rounds",rounds,"pairs",len(pairs))
# mode 2: call-site propagation (same caller, same position, same call count, size within 50%)
added=1
while added:
    added=0
    for k in sorted(pairs):
        a=dst[k];b=src[pairs[k]]
        if len(a["calls"])!=len(b["calls"]): continue
        for ca,cb in zip(a["calls"],b["calls"]):
            if ca not in di or cb not in si: continue
            i=di[ca];j=si[cb]
            if i in pairs or j in pairs.values(): continue
            fa=dst[i];fb=src[j]
            if fb["name"].startswith("FUN_") or len(fa["calls"])!=len(fb["calls"]): continue
            if abs(fa["size"]-fb["size"])>max(fa["size"],fb["size"])//2: continue
            pairs[i]=j;added+=1
    print("callsite round added",added)
print("pairs after callsite",len(pairs))
used={}
with open(sys.argv[4],"w") as fh:
    for k in sorted(pairs):
        n=src[pairs[k]]["name"]
        if n in used: continue
        used[n]=1
        if dst[k]["name"]==n: continue
        fh.write(f"0x{dst[k]['addr']:08x} func {n} xalign {lab}:{src[pairs[k]]['addr']:08x} twinmap\n")
print("written",len(used))
