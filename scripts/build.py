import glob,json,os,sys,math
raw=sys.argv[1]; geo=json.load(open('geocache.json'))
CAT={'Theft':['LARCENY','LAR/SHOP','LAR/BIKE','LARCENY BY CHEC','LAR/ATMP'],
'Car crime':['B&E M/V','LAR/MV','LAR/MVPL','LAR/MVPT'],
'Burglary':['B&E PAST','B&E/PROG'],
'Fraud & scams':['FRAUD'],
'Vandalism':['VAND/PRP','VAND/CTY'],
'Assault & fights':['A&B','A&B PAST','A & B ARREST(S)','IND/A&B','ASSAULT-B','FGT/DISO','SHOTS/HD'],
'Harassment':['THREATS','HARASS'],
'Trespass & drugs':['TRESPASS','DRUGS']}
LBL={'LARCENY':'Larceny','LAR/SHOP':'Shoplifting','LAR/BIKE':'Bike theft','LARCENY BY CHEC':'Check larceny','LAR/ATMP':'Attempted larceny',
'B&E M/V':'Car break-in','LAR/MV':'Theft from car','LAR/MVPL':'Stolen plate','LAR/MVPT':'Stolen car parts','B&E PAST':'Break-in (past)','B&E/PROG':'Break-in (in progress)',
'FRAUD':'Fraud / scam','VAND/PRP':'Property vandalism','VAND/CTY':'City property vandalism','A&B':'Assault & battery','A&B PAST':'Assault & battery (past)',
'A & B ARREST(S)':'Assault & battery (arrest)','IND/A&B':'Indecent A&B','ASSAULT-B':'Assault','FGT/DISO':'Fight / disorderly','SHOTS/HD':'Shots heard',
'THREATS':'Threats','HARASS':'Harassment','TRESPASS':'Trespassing','DRUGS':'Drugs'}
t2c={t:c for c,ts in CAT.items() for t in ts}
V={'Auburndale':(42.3456,-71.2470),'Chestnut Hill':(42.3230,-71.1700),'Newton Centre':(42.3297,-71.1923),'Newton Corner':(42.3519,-71.1834),
'Newton Highlands':(42.3220,-71.2063),'Lower Falls':(42.3329,-71.2530),'Upper Falls':(42.3125,-71.2215),'Newtonville':(42.3507,-71.2084),
'Nonantum':(42.3627,-71.1990),'Oak Hill':(42.3080,-71.1820),'Thompsonville':(42.3170,-71.1880),'Waban':(42.3268,-71.2300),'West Newton':(42.3490,-71.2270)}
def village(lat,lon):
    return min(V,key=lambda k:(V[k][0]-lat)**2+((V[k][1]-lon)*0.74)**2)
rows=[];seen=set()
for f in sorted(glob.glob(raw+'/*.txt')):
    for line in open(f):
        line=line.strip()
        if not line: continue
        dt,num,st,t=line.split('|')
        md,hm=dt.split(); m,d=md.split('/'); h,mi=hm.split(':')
        n=''.join(c for c in num if c.isdigit())
        a=f"{n} {st}".strip()
        if a not in geo: continue
        k=(md,hm,a,t)
        if k in seen: continue
        seen.add(k)
        lat,lon=geo[a]
        blk=(f"{(int(n)//100)*100} block of " if n else "")+st.title()
        rows.append({'d':f"2023-{int(m):02d}-{int(d):02d}",'h':int(h),'m':int(mi),'t':LBL.get(t,t.title()),'c':t2c.get(t,'Other'),
          'loc':blk,'v':village(lat,lon),'lat':round(lat,4),'lon':round(lon,4)})
rows.sort(key=lambda r:(r['d'],r['h'],r['m']))
json.dump({'generated':'2026-11-07','source':'Newton Police Department weekly incident logs (newtonma.gov)','weeks':len(glob.glob(raw+'/*.txt')),'incidents':rows},open('data.json','w'),separators=(',',':'))
from collections import Counter
print(len(rows)); print(Counter(r['c'] for r in rows)); print(Counter(r['v'] for r in rows))
