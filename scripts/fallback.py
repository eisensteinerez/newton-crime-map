import csv,json,time,urllib.request,urllib.parse
rows=list(csv.reader(open('batch.csv')))
addr={r[0]:r[1] for r in rows}
out={}
for r in csv.reader(open('geo.csv')):
    if len(r)>5 and r[2]=='Match':
        lon,lat=map(float,r[5].split(','))
        out[addr[r[0]]]=[round(lat,6),round(lon,6)]
def inb(lat,lon): return 42.27<lat<42.38 and -71.28<lon<-71.14
miss=[a for a in addr.values() if a not in out or not inb(*out[a])]
print('fallback',len(miss))
for a in miss:
    q=a.replace(' ST',' STREET')+', Newton, MA'
    u='https://nominatim.openstreetmap.org/search?'+urllib.parse.urlencode({'q':a+', Newton, Massachusetts','format':'json','limit':1,'viewbox':'-71.28,42.38,-71.14,42.27','bounded':1})
    try:
        d=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'newton-crime-map/1.0 (personal project)'}),timeout=20))
        if d: out[a]=[round(float(d[0]['lat']),6),round(float(d[0]['lon']),6)]
        else:
            st=' '.join(w for w in a.split() if not w.isdigit())
            u2='https://nominatim.openstreetmap.org/search?'+urllib.parse.urlencode({'q':st+', Newton, Massachusetts','format':'json','limit':1,'viewbox':'-71.28,42.38,-71.14,42.27','bounded':1})
            time.sleep(3)
            d=json.load(urllib.request.urlopen(urllib.request.Request(u2,headers={'User-Agent':'newton-crime-map/1.0 (personal project)'}),timeout=20))
            if d: out[a]=[round(float(d[0]['lat']),6),round(float(d[0]['lon']),6)]; print('street-level',a)
            else: print('FAIL',a)
    except Exception as e: print('ERR',a,e)
    time.sleep(3)
json.dump(out,open('geocache.json','w'))
print('total',len(out),'of',len(addr))
