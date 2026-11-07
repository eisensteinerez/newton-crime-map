import sys
N=sys.argv[1]
t=open('template.html').read()
lc=open(N+'/leaflet-1.9.4/package/dist/leaflet.css').read()
mc=open(N+'/leaflet.markercluster-1.5.3/package/dist/MarkerCluster.css').read()
t=t.replace('/*__LEAFLET_CSS__*/',lc).replace('/*__MC_CSS__*/',mc)
t=t.replace('/*__DATA__*/null',open('data.json').read()).replace('/*__BOUNDARY__*/null',open('newton.geojson').read())
open('index.html','w').write(t)
print(len(t))
