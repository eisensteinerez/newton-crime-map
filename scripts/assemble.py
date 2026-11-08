import sys
N=sys.argv[1]; t=open('template3.html').read()
t=t.replace('/*__MAPLIBRE_CSS__*/',open(N+'/ml/package/dist/maplibre-gl.css').read())
t=t.replace('/*__DATA__*/null',open('data3.json').read()).replace('/*__BOUNDARY__*/null',open('newton.geojson').read())
open('index3.html','w').write(t); print(len(t))
