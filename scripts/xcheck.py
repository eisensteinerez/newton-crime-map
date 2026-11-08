import json,glob,collections,sys
d=json.load(open('crimesAll.json'))
daily=collections.defaultdict(list)
for r in d:
    if r['date'].endswith('2023'): daily[r['date'][:5]].append(r)
W=[]
for f in sorted(glob.glob('/home/user/newton-crime-map/data/raw_logs/*.txt')):
    for l in open(f):
        l=l.strip()
        if not l: continue
        dt,num,st,t=l.split('|'); md,hm=dt.split(); m,dd=md.split('/')
        W.append((f"{int(m):02d}/{int(dd):02d}",hm.zfill(5),''.join(c for c in num if c.isdigit()),st.upper(),t))
found=tm=sm=nm=0; bad=[]
for md,hm,num,st,t in W:
    hit=[r for r in daily.get(md,[]) if r['time'][:5]==hm]
    if not hit: bad.append(('MISSING',md,hm,num,st,t)); continue
    found+=1; h=next((r for r in hit if r['type']==t),hit[0])
    tm+=h['type']==t; sm+=h['street']==st; nm+=h['num']==num
    if h['street']!=st or h['num']!=num: bad.append(('DIFF',md,hm,num,st,'->',h['num'],h['street']))
wd={w[0] for w in W}; wk={(w[0],w[1]) for w in W}
extra=[r for k in wd for r in daily.get(k,[]) if (r['date'][:5],r['time'][:5]) not in wk]
print(f'weekly {len(W)} found {found} ({found/len(W):.1%}) type ok {tm} street ok {sm} ({sm/found:.1%}) number ok {nm} ({nm/found:.1%}); daily extras {len(extra)}')
if len(sys.argv)>1:
    for b in bad[:60]: print(b)
    for r in extra: print('EXTRA',r)
