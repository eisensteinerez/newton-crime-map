import sys
N=sys.argv[1]; t=open('template2.html').read()
t=t.replace('/*__MAPLIBRE_CSS__*/',open(N+'/ml/package/dist/maplibre-gl.css').read())
t=t.replace('/*__DATA__*/null',open('data2.json').read()).replace('/*__BOUNDARY__*/null',open('newton.geojson').read())
open('index2.html','w').write(t); print(len(t))
