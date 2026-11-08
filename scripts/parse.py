import json,glob,re,collections,sys
CODES={'LARCENY':'LARCENY','LAR/SHOP':'LAR/SHOP','LAR/BIKE':'LAR/BIKE','LAR/MV':'LAR/MV','LAR/MVPL':'LAR/MVPL','LAR/MVPT':'LAR/MVPT','LAR/ATMP':'LAR/ATMP',
'B&E M/V':'B&E M/V','B&E PAST':'B&E PAST','B&E/PROG':'B&E/PROG','B&E/ATT':'B&E/ATT','FRAUD':'FRAUD','VAND/PRP':'VAND/PRP','VAND/CTY':'VAND/CTY',
'A&B':'A&B','A&B PAST':'A&B PAST','A&BARREST(S)':'A & B ARREST(S)','A&B/DW':'A&B/DW','IND/A&B':'IND/A&B','FGT/DISO':'FGT/DISO','SHOTS/HD':'SHOTS/HD',
'THREATS':'THREATS','HARASS':'HARASS','TRESPASS':'TRESPASS','DRUGS':'DRUGS','ROBBERY':'ROBBERY','STOLEN MV':'STOLEN MV','STAB/GUNSHOT':'STAB/GUNSHOT'}
FIX={'VANDICTY':'VAND/CTY','VANDIPRP':'VAND/PRP','VAND/PRF':'VAND/PRP','A8B':'A&B','A8B PAST':'A&B PAST','B&E MIV':'B&E M/V','B&EM/V':'B&E M/V','LARISHOP':'LAR/SHOP','LAR/SHOF':'LAR/SHOP','LARIMV':'LAR/MV','B&EIPROG':'B&E/PROG','FGTIDISO':'FGT/DISO','SHOTSIHD':'SHOTS/HD','SIAB/GUNSHOT':'STAB/GUNSHOT','B&E MV':'B&E M/V','LARIBIKE':'LAR/BIKE','LAR/BlKE':'LAR/BIKE','STAB GUNSHOT':'STAB/GUNSHOT','AB/GUNSHOT':'STAB/GUNSHOT','FGTI/DISO':'FGT/DISO','ERAUD':'FRAUD','FRAUO':'FRAUD','FGT/DISO/':'FGT/DISO'}
SUF={'ST','AVE','RD','PL','TER','CIR','DR','LA','LN','PK','PKWY','CT','WAY','SQ','HWY','PATH','BLVD','ROW'}
def ctype(t):
    t=re.sub(r'^[^A-Z0-9]+','',t.upper()).strip()
    t=re.sub(r'\s+',' ',t)
    if t.startswith('LARCENY BY'): return 'LARCENY BY CHEC'
    t=re.sub(r'-\s?[A-Z]?\d*[A-Z]?\d*$','',t).strip(' -')  # STAB/GUNSHOT-A
    t=FIX.get(t,t)
    return CODES.get(t)
def cstreet(s):
    s=re.sub(r'[^A-Z0-9 /\'&.-]','',s.upper()); s=re.sub(r'\s+',' ',s).strip(' .-')
    for suf in sorted(SUF,key=len,reverse=True):
        m=re.fullmatch(r'(.*[A-Z]{3,})('+suf+r')',s)
        if m and ' ' not in s: s=m.group(1)+' '+suf; break
    s=re.sub(r'\b([A-Z]{3,})(ST|AVE|RD)$',r'\1 \2',s) if not re.search(r' (ST|AVE|RD)$',s) else s
    w=s.split(' ')
    if len(w)>1 and w[0] in SUF: s=' '.join(w[1:]+w[:1])
    return s
import datetime,bisect
def split_merged(ty,num,st):
    # two log rows OCR'd onto one line: 'LAKE AVE WASHINGTON ST' / 'LARCENY 911HANGUP'. Recover the crime rows.
    w=re.sub(r'^[^A-Z0-9]+','',ty.upper()).split()
    best=None
    for n in (2,3):
        if len(w)<n: continue
        import itertools
        for cuts in itertools.combinations(range(1,len(w)),n-1):
            parts=[' '.join(w[a:b]) for a,b in zip((0,)+cuts,cuts+(len(w),))]
            codes=[ctype(p) for p in parts]; k=sum(1 for c in codes if c)
            if k and (best is None or k>best[0]): best=(k,codes)
    if not best: return []
    codes=best[1]; n=len(codes)
    sw=cstreet(st).split(); streets=[];cur=[]
    for t in sw:
        cur.append(t)
        if t in SUF: streets.append(' '.join(cur)); cur=[]
    if cur: streets.append(' '.join(cur))
    nums=[x for x in (num or '').split() if re.fullmatch(r'\d+',x)]
    out=[]
    for i,c in enumerate(codes):
        if not c or len(streets)!=n or streets[i] in SUF: continue
        out.append((c,nums[i] if len(nums)==n else '',streets[i],i))
    return out
out=[];bad=collections.Counter();tot=0;merged=0;stc=collections.Counter();adc=collections.Counter();allrows=[]
for f in [x for g in sys.argv[1].split('|') for x in sorted(glob.glob(g))]:
    for inc,date,tm,num,st,ty,p in json.load(open(f)):
        tot+=1
        if re.fullmatch(r'\d\d/\d\d/\d{4}',date):
            try: allrows.append((len(allrows),datetime.date(int(date[6:]),int(date[:2]),int(date[3:5]))))
            except ValueError: pass
        pos=len(allrows)-1
        stc[cstreet(st)]+=1
        _t=re.sub(r'[=,.:;]',' ',(num or '')+' '+st).split(); _n=[t for t in _t if re.fullmatch(r'\d{1,5}',t)]
        if _n: adc[(_n[0],cstreet(' '.join(t for t in _t if re.search(r'[A-Za-z]',t))))]+=1
        c=ctype(ty)
        if not c and re.fullmatch(r'\d\d/\d\d/\d{4}',date) and re.fullmatch(r'\d\d:\d\d(:\d\d)?',tm):
            for c2,n2,s2,i2 in split_merged(ty,num,st):
                merged+=1; out.append({'pos':pos,'inc':inc+('' if i2==0 else '.%d'%i2),'date':date,'time':tm,'num':n2,'street':s2,'type':c2})
            if split_merged(ty,num,st): continue
        if not c:
            if any(k in ty for k in ['LAR','FRAUD','B&E','VAND','A&B','HARASS','THREAT','TRESP','DRUG','FGT','SHOT']): bad[ty]+=1
            continue
        if not re.fullmatch(r'\d\d/\d\d/\d{4}',date) or not re.fullmatch(r'\d\d:\d\d(:\d\d)?',tm): bad['date:'+date+' '+tm]+=1; continue
        # some pages split the address columns in the wrong place ('WASHINGTON 227.' | 'ST'), so rebuild the address from both columns
        toks=re.sub(r'[=,.:;]',' ',(num or '')+' '+st).split()
        nums=[t for t in toks if re.fullmatch(r'\d{1,5}',t)]; words=[t for t in toks if re.search(r'[A-Za-z]',t)]
        n=nums[0] if nums else ''
        out.append({'pos':pos,'inc':inc,'date':date,'time':tm,'num':n,'street':cstreet(' '.join(words)),'type':c})
# date sanity: the logs are printed in time order, so a crime's date must match the rows around it
fixed=dropped=0; chk=[]; dbg=[]
for r in out:
    i=r['pos']; nb=[d for a,d in allrows[max(0,i-6):i+7] if a!=i]
    try: d=datetime.date(int(r['date'][6:]),int(r['date'][:2]),int(r['date'][3:5]))
    except ValueError: dropped+=1; continue
    med=sorted(nb)[len(nb)//2] if nb else d
    if abs((d-med).days)>1:
        if nb and max(nb)-min(nb)<=datetime.timedelta(days=2): r['date']=med.strftime('%m/%d/%Y'); fixed+=1
        else: dropped+=1; dbg.append((r['inc'],r['date'],sorted(nb)[0].isoformat() if nb else None,sorted(nb)[-1].isoformat() if nb else None)); continue
    r.pop('pos'); chk.append(r)
out=chk
print('date fixed from neighbours',fixed,'dropped',dropped)
if len(sys.argv)>3: [print(x) for x in dbg[:40]]
# street spelling: snap OCR typos to streets that appear often in the full logs (all call types)
import difflib
vocab=[k for k,n in stc.items() if n>=8 and len(k)>4 and k.split()[-1] in SUF]
vs=set(vocab); snapped=nostreet=0; memo={}
for r in out:
    st=r['street']
    if st in vs: continue
    if re.search(r'MONWEA|MMONW|NWEALT|MONWEATT|COMMONW',st): r['street']=st='COMMONWEALTH AVE'
    elif re.search(r'POND',st) and not re.search(r'POND (ST|RD|AVE)',st): r['street']=st='HAMMOND POND PKWY'
    if st in vs: continue
    if st not in memo:
        m=difflib.get_close_matches(st,vocab,1,0.8)
        memo[st]=m[0] if m else None
    if memo[st]: r['street']=memo[st]; snapped+=1
    elif len(re.sub(r'[^A-Z]','',st.replace(' ST','').replace(' RD','').replace(' AVE','')))<4: r['street']=''; nostreet+=1
print('vocab',len(vocab),'streets snapped',snapped,'unusable street',nostreet)
out=[r for r in out if r['street']]
# Newton house numbers stop around 2500. A 4-digit number starting with 4 is almost always a misread leading 1 (4199 CENTRE ST = 1199).
numfix=0
for r in out:
    n=r['num']
    if len(n)==4 and n[0]=='4': r['num']='1'+n[1:]; numfix+=1
    elif len(n)>=5 or (len(n)==4 and int(n)>2600): r['num']=''; numfix+=1
print('house numbers fixed',numfix)

# dedupe: same incident read twice (files overlap on boundary days) or same row twice
best={}
for r in out:
    k=(r['inc'].split('.')[0]+r['inc'][8:],r['date'],r['time'][:5],r['type'])
    q=(r['street'] in vs, bool(r['num']), len(r['street']))
    if k not in best or q>best[k][0]: best[k]=(q,r)
out=[v[1] for v in best.values()]; out.sort(key=lambda r:(r['date'][6:],r['date'],r['time']))
seen=set();uniq=[]
for r in out:
    k=(r['date'],r['time'][:5],r['street'],r['type'])  # not by incident no.: OCR sometimes misreads it, which would wrongly merge two crimes
    if k in seen: continue
    seen.add(k); uniq.append(r)
json.dump(uniq,open(sys.argv[2],'w'))
print('recovered from merged lines',merged);print('rows',tot,'crimes',len(uniq)); print(collections.Counter(r['type'] for r in uniq).most_common()); print('unparsed',sum(bad.values()),bad.most_common(8))
print(collections.Counter(r['street'] for r in uniq).most_common(15))
