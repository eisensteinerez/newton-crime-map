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
# 2023 weekly logs
for f in sorted(glob.glob(sys.argv[1]+'/*.txt')):
    for line in open(f):
        line=line.strip()
        if not line: continue
        dt,num,st,t=line.split('|'); md,hm=dt.split(); m,d=md.split('/'); h,mi=hm.split(':')
        recs.append(dict(p='2023',d=f"2023-{int(m):02d}-{int(d):02d}",h=int(h),m=int(mi),num=''.join(c for c in num if c.isdigit()),st=st,t=t))
# OCR'd daily logs
for f in sys.argv[2:]:
    for r in json.load(open(f)):
        mo,da,yr=r['date'].split('/'); h,mi=r['time'].split(':')[:2]
        if int(h)>23 or int(mi)>59 or not (1<=int(mo)<=12 and 1<=int(da)<=31): continue
        recs.append(dict(p='2025',d=f"{yr}-{mo}-{da}",h=int(h),m=int(mi),num=r['num'],st=r['street'],t=r['type']))
need=sorted({f"{r['num']} {r['st']}".strip() for r in recs}-set(geo))
print('to geocode',len(need))
if need:
    buf=io.StringIO(); w=csv.writer(buf)
    for i,a in enumerate(need): w.writerow([i,a,'Newton','MA',''])
    open('/tmp/b2.csv','w').write(buf.getvalue())
    res=subprocess.run(['curl','-sS','--form','addressFile=@/tmp/b2.csv','--form','benchmark=Public_AR_Current','https://geocoding.geo.census.gov/geocoder/locations/addressbatch'],capture_output=True,text=True).stdout
    for row in csv.reader(io.StringIO(res)):
        if len(row)>5 and row[2]=='Match':
            lon,lat=map(float,row[5].split(','))
            if inb(lat,lon): geo[need[int(row[0])]]=[round(lat,6),round(lon,6)]
    miss=[a for a in need if a not in geo]; print('census missed',len(miss))
    for a in miss:
        for q in [a, re.sub(r'^\d+\s*','',a)]:
            if not q: continue
            u='https://nominatim.openstreetmap.org/search?'+urllib.parse.urlencode({'q':q+', Newton, Massachusetts','format':'json','limit':1,'viewbox':'-71.28,42.38,-71.14,42.27','bounded':1})
            time.sleep(1.2)
            try: d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'newton-crime-map/1.0 (personal project)'}),timeout=20))
            except Exception as e: d=[]
            if d: geo[a]=[round(float(d[0]['lat']),6),round(float(d[0]['lon']),6)]; break
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
per=[]
for pid,label,short in [('2025','Oct 2025 – Mar 2026','2025–26'),('2023','14 weeks of 2023','2023')]:
    ds=[r['d'] for r in rows if r['p']==pid]
    if ds: per.append({'id':pid,'label':label,'short':short,'start':min(ds),'end':max(ds)})
json.dump({'source':'Newton Police Department daily and weekly incident logs, published on newtonma.gov. Crimes only; medical calls, alarms, car crashes and patrols are left out.','periods':per,'incidents':rows},open('data2.json','w'),separators=(',',':'))
print(len(rows),Counter(r['p'] for r in rows),per)
