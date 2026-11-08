import glob,json,sys,csv,io,time,urllib.request,urllib.parse,subprocess,os,re
from collections import Counter
geo=json.load(open('geocache.json'))
CAT={'Theft':['LARCENY','LAR/SHOP','LAR/BIKE','LARCENY BY CHEC','LAR/ATMP'],'Car crime':['B&E M/V','LAR/MV','LAR/MVPL','LAR/MVPT','STOLEN MV'],
'Burglary':['B&E PAST','B&E/PROG','B&E/ATT'],'Fraud & scams':['FRAUD'],'Vandalism':['VAND/PRP','VAND/CTY'],
'Assault & fights':['A&B','A&B PAST','A & B ARREST(S)','IND/A&B','ASSAULT-B','A&B/DW','FGT/DISO','SHOTS/HD','STAB/GUNSHOT','ROBBERY'],
'Harassment':['THREATS','HARASS'],'Trespass & drugs':['TRESPASS','DRUGS']}
LBL={'LARCENY':'Larceny','LAR/SHOP':'Shoplifting','LAR/BIKE':'Bike theft','LARCENY BY CHEC':'Check fraud larceny','LAR/ATMP':'Attempted larceny',
'B&E M/V':'Car break-in','LAR/MV':'Theft from car','LAR/MVPL':'Stolen plate','LAR/MVPT':'Stolen car parts','STOLEN MV':'Stolen car','B&E PAST':'Break-in','B&E/PROG':'Break-in in progress','B&E/ATT':'Attempted break-in',
'FRAUD':'Fraud / scam','VAND/PRP':'Vandalism','VAND/CTY':'Vandalism, city property','A&B':'Assault & battery','A&B PAST':'Assault & battery (reported)',
'A & B ARREST(S)':'Assault & battery, arrest','IND/A&B':'Indecent assault','ASSAULT-B':'Assault','A&B/DW':'Assault w/ dangerous weapon','FGT/DISO':'Fight / disorderly','SHOTS/HD':'Shots heard',
'STAB/GUNSHOT':'Stabbing / gunshot','ROBBERY':'Robbery','THREATS':'Threats','HARASS':'Harassment','TRESPASS':'Trespassing','DRUGS':'Drugs'}
t2c={t:c for c,ts in CAT.items() for t in ts}
V={'Auburndale':(42.3456,-71.2470),'Chestnut Hill':(42.3230,-71.1700),'Newton Centre':(42.3297,-71.1923),'Newton Corner':(42.3519,-71.1834),
'Newton Highlands':(42.3220,-71.2063),'Lower Falls':(42.3329,-71.2530),'Upper Falls':(42.3125,-71.2215),'Newtonville':(42.3507,-71.2084),
'Nonantum':(42.3627,-71.1990),'Oak Hill':(42.3080,-71.1820),'Thompsonville':(42.3170,-71.1880),'Waban':(42.3268,-71.2300),'West Newton':(42.3490,-71.2270)}
village=lambda lat,lon:min(V,key=lambda k:(V[k][0]-lat)**2+((V[k][1]-lon)*0.74)**2)
inb=lambda lat,lon:42.27<lat<42.38 and -71.28<lon<-71.14
recs=[]
# OCR'd daily logs (all years)
for f in sys.argv[2:]:
    for r in json.load(open(f)):
        mo,da,yr=r['date'].split('/'); h,mi=r['time'].split(':')[:2]
        if int(h)>23 or int(mi)>59 or not (1<=int(mo)<=12 and 1<=int(da)<=31): continue
        recs.append(dict(p=yr,d=f"{yr}-{mo}-{da}",h=int(h),m=int(mi),num=r['num'],st=r['street'],t=r['type']))
daily_days={r['d'] for r in recs}
# 2023 weekly logs fill only dates the daily logs don't cover
wk=0
for f in sorted(glob.glob(sys.argv[1]+'/*.txt')):
    for line in open(f):
        line=line.strip()
        if not line: continue
        dt,num,st,t=line.split('|'); md,hm=dt.split(); m,d=md.split('/'); h,mi=hm.split(':')
        dd=f"2023-{int(m):02d}-{int(d):02d}"
        if dd in daily_days: continue
        wk+=1; recs.append(dict(p='2023',d=dd,h=int(h),m=int(mi),num=''.join(c for c in num if c.isdigit()),st=st,t=t))
print('weekly-only rows',wk)
need=sorted({f"{r['num']} {r['st']}".strip() for r in recs}-set(geo))
print('to geocode',len(need))
if need:
    for c0 in range(0,len(need),1500):
        buf=io.StringIO(); w=csv.writer(buf)
        for i in range(c0,min(len(need),c0+1500)):
            a=need[i]
            if re.match(r'^\d',a): w.writerow([i,a,'Newton','MA',''])
        open('b3.csv','w').write(buf.getvalue())
        res=subprocess.run(['curl','-sS','-m','900','--form','addressFile=@b3.csv','--form','benchmark=Public_AR_Current','https://geocoding.geo.census.gov/geocoder/locations/addressbatch'],capture_output=True,text=True).stdout
        for row in csv.reader(io.StringIO(res)):
            if len(row)>5 and row[2]=='Match':
                lon,lat=map(float,row[5].split(','))
                if inb(lat,lon): geo[need[int(row[0])]]=[round(lat,6),round(lon,6)]
        print('census chunk',c0,len(geo),flush=True); json.dump(geo,open('geocache.json','w'))
    miss=[a for a in need if a not in geo]; print('census missed',len(miss))
    json.dump(geo,open('geocache.json','w'))
    # fill misses from the nearest known house number on the same street, else one street-level lookup per street
    def split(a):
        m=re.match(r'^(\d+)\s+(.*)$',a); return (int(m.group(1)),m.group(2)) if m else (None,a)
    bystreet={}
    for k,v in geo.items():
        n,st=split(k)
        if n is not None and k in geo: bystreet.setdefault(st,[]).append((n,v))
    streetq={}; interp=0
    for a in miss:
        n,st=split(a); pts=sorted(bystreet.get(st,[]))
        if pts and n is not None:
            lo=[p for p in pts if p[0]<=n]; hi=[p for p in pts if p[0]>=n]
            if lo and hi and hi[0][0]!=lo[-1][0]:
                f=(n-lo[-1][0])/(hi[0][0]-lo[-1][0]); A,B=lo[-1][1],hi[0][1]
                geo[a]=[round(A[0]+(B[0]-A[0])*f,6),round(A[1]+(B[1]-A[1])*f,6)]
            else: geo[a]=(lo[-1] if lo else hi[0])[1]
            interp+=1; continue
        streetq.setdefault(st,[]).append(a)
    print('placed from same-street neighbours',interp,'streets needing lookup',len(streetq))
    for st,addrs in streetq.items():
        if st in geo: 
            for a in addrs: geo[a]=geo[st]
            continue
        u='https://nominatim.openstreetmap.org/search?'+urllib.parse.urlencode({'q':st+', Newton, Massachusetts','format':'json','limit':1,'viewbox':'-71.28,42.38,-71.14,42.27','bounded':1})
        time.sleep(1.2)
        try: d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'newton-crime-map/1.0 (personal project)'}),timeout=20))
        except Exception as e: d=[]
        if d:
            geo[st]=[round(float(d[0]['lat']),6),round(float(d[0]['lon']),6)]
            for a in addrs: geo[a]=geo[st]
    json.dump(geo,open('geocache.json','w'))
rows=[];seen=set()
for r in recs:
    a=f"{r['num']} {r['st']}".strip()
    if a not in geo: continue
    k=(r['d'],r['h'],r['m'],a,r['t'])
    if k in seen: continue
    seen.add(k); lat,lon=geo[a]
    n=r['num']; blk=(f"{(int(n)//100)*100} block of " if n and int(n)>=100 else "")+r['st'].title()
    rows.append({'p':r['p'],'d':r['d'],'h':r['h'],'m':r['m'],'t':LBL.get(r['t'],r['t'].title()),'c':t2c.get(r['t'],'Other'),'loc':blk,'v':village(lat,lon),'lat':round(lat,4),'lon':round(lon,4)})
rows=[r for r in rows if r['c']!='Other']
rows.sort(key=lambda r:(r['d'],r['h'],r['m']))
import datetime
MN='Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split()
alld=sorted({r['d'] for r in rows}); per=[{'id':'all','label':f"{alld[0][:4]} – {alld[-1][:4]}",'short':'All','start':alld[0],'end':alld[-1],'days':len(alld)}]
gaps=[]
for y in sorted({r['p'] for r in rows}):
    ds=sorted({r['d'] for r in rows if r['p']==y})
    mc=Counter(int(d[5:7]) for d in ds); months={m for m,k in mc.items() if k>=5}; lo,hi=min(months),max(months)
    miss=[m for m in range(1,13) if m not in months]
    # human note: missing months, or partial coverage at ends
    def rng(ms):
        out=[];k=0
        while k<len(ms):
            a=ms[k]
            while k+1<len(ms) and ms[k+1]==ms[k]+1: k+=1
            out.append(MN[a-1] if a==ms[k] else MN[a-1]+'–'+MN[ms[k]-1]); k+=1
        return out
    note=[]
    inner=[m for m in miss if lo<m<hi]
    if lo>1: note.append('from '+MN[lo-1])
    if hi<12: note.append('through '+datetime.date.fromisoformat(ds[-1]).strftime('%b %-d'))
    if inner: note.append('no logs '+', '.join(rng(inner)))
    for m in inner: gaps.append(f"{MN[m-1]} {y}")
    per.append({'id':y,'label':y,'short':y,'start':f"{y}-01-01" if lo==1 else ds[0],'end':ds[-1] if hi<12 else f"{y}-12-31",'days':len(ds),'note':'; '.join(note)})
gapNote=('Missing months: '+', '.join(gaps)+'. The city never posted logs for these, so they show as empty. ' if gaps else '')+'Rates are per week of logs we have, so partial years compare fairly.'
json.dump({'source':'Newton Police Department daily and weekly incident logs, published on newtonma.gov. Crimes only; medical calls, alarms, car crashes and patrols are left out.','periods':per,'gapNote':gapNote,'incidents':rows},open('data3.json','w'),separators=(',',':'))
print(len(rows),sorted(Counter(r['p'] for r in rows).items()));[print(p) for p in per]
