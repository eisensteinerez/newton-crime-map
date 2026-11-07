import json,glob,re,collections,sys
CODES={'LARCENY':'LARCENY','LAR/SHOP':'LAR/SHOP','LAR/BIKE':'LAR/BIKE','LAR/MV':'LAR/MV','LAR/MVPL':'LAR/MVPL','LAR/MVPT':'LAR/MVPT','LAR/ATMP':'LAR/ATMP',
'B&E M/V':'B&E M/V','B&E PAST':'B&E PAST','B&E/PROG':'B&E/PROG','B&E/ATT':'B&E/ATT','FRAUD':'FRAUD','VAND/PRP':'VAND/PRP','VAND/CTY':'VAND/CTY',
'A&B':'A&B','A&B PAST':'A&B PAST','A&BARREST(S)':'A & B ARREST(S)','A&B/DW':'A&B/DW','IND/A&B':'IND/A&B','FGT/DISO':'FGT/DISO','SHOTS/HD':'SHOTS/HD',
'THREATS':'THREATS','HARASS':'HARASS','TRESPASS':'TRESPASS','DRUGS':'DRUGS','ROBBERY':'ROBBERY','STOLEN MV':'STOLEN MV','STAB/GUNSHOT':'STAB/GUNSHOT'}
FIX={'VANDICTY':'VAND/CTY','VANDIPRP':'VAND/PRP','VAND/PRF':'VAND/PRP','A8B':'A&B','A8B PAST':'A&B PAST','B&E MIV':'B&E M/V','B&EM/V':'B&E M/V','LARISHOP':'LAR/SHOP','LAR/SHOF':'LAR/SHOP','LARIMV':'LAR/MV','B&EIPROG':'B&E/PROG','FGTIDISO':'FGT/DISO','SHOTSIHD':'SHOTS/HD','SIAB/GUNSHOT':'STAB/GUNSHOT'}
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
out=[];bad=collections.Counter();tot=0
for f in sorted(glob.glob(sys.argv[1])):
    for inc,date,tm,num,st,ty,p in json.load(open(f)):
        tot+=1
        c=ctype(ty)
        if not c:
            if any(k in ty for k in ['LAR','FRAUD','B&E','VAND','A&B','HARASS','THREAT','TRESP','DRUG','FGT','SHOT']): bad[ty]+=1
            continue
        if not re.fullmatch(r'\d\d/\d\d/\d{4}',date) or not re.fullmatch(r'\d\d:\d\d(:\d\d)?',tm): bad['date:'+date+' '+tm]+=1; continue
        n=re.sub(r'\D','',num.split(' ')[0]) if num else ''
        out.append({'inc':inc,'date':date,'time':tm,'num':n,'street':cstreet(st),'type':c})
seen=set();uniq=[]
for r in out:
    if r['inc'] in seen: continue
    seen.add(r['inc']); uniq.append(r)
json.dump(uniq,open(sys.argv[2],'w'))
print('rows',tot,'crimes',len(uniq)); print(collections.Counter(r['type'] for r in uniq).most_common()); print('unparsed',sum(bad.values()),bad.most_common(8))
print(collections.Counter(r['street'] for r in uniq).most_common(15))
