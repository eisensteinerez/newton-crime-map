import glob,csv,os,sys
raw=sys.argv[1]; seen={}
for f in sorted(glob.glob(raw+'/*.txt')):
    for line in open(f):
        line=line.strip()
        if not line: continue
        dt,num,st,t=line.split('|')
        num=''.join(c for c in num if c.isdigit())
        key=(num,st)
        seen[key]=1
w=csv.writer(open('batch.csv','w',newline=''))
for i,(n,s) in enumerate(seen):
    w.writerow([i, f"{n} {s}".strip(), 'Newton','MA',''])
print(len(seen))
