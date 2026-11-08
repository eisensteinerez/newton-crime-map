import sys,subprocess,re,json,os,tempfile,csv,io
from PIL import Image
pdf,first,last,cfg,out=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),sys.argv[4],sys.argv[5]
C={'2026':(1000,1450,1890),'2025':(900,1370,1810)}.get(cfg,(1000,1450,1890))
def tsv(img,extra=[]):
    r=subprocess.run(['tesseract',img,'-','--psm','6']+extra+['tsv'],capture_output=True,text=True).stdout
    ws=[]
    for row in csv.reader(io.StringIO(r),delimiter='\t',quoting=csv.QUOTE_NONE):
        if len(row)<12 or row[0]=='level': continue
        if row[11].strip() and float(row[10])>=0: ws.append((int(row[6]),int(row[7]),row[11].strip()))
    return ws
res=[]
td=tempfile.mkdtemp()
for p in range(first,last+1):
    base=f'{td}/p'
    subprocess.run(['pdftoppm','-r','300','-gray','-f',str(p),'-l',str(p),'-png','-singlefile',pdf,base])
    img=base+'.png'
    ws=tsv(img)
    fx=sorted(x for x,y,t in ws if x>1350 and re.fullmatch(r'\d{8}',t))
    if fx:
        F=fx[len(fx)//2]; C=(F-893-15,F-437-15,F-15)
    incs=sorted([(y,t) for x,y,t in ws if x<300 and re.fullmatch(r'2[0-6]\d{6}',t)])
    im=Image.open(img); im.crop((340,0,600,im.size[1])).save(td+'/d.png')
    ds=sorted([(y,t) for x,y,t in tsv(td+'/d.png',['-c','tessedit_char_whitelist=0123456789/:'])])
    for i,(y,inc) in enumerate(incs):
        lo=y-45; hi=(incs[i+1][0]-45) if i+1<len(incs) else y+120
        band=[(x,yy,t) for x,yy,t in ws if lo<=yy<hi]
        dd=[t for yy,t in ds if lo<=yy<hi]
        date=next((t for t in dd if re.fullmatch(r'\d\d/\d\d/\d{4}',t)),'')
        tm=next((t for t in dd if re.fullmatch(r'\d\d:\d\d(:\d\d)?',t)),'')
        num=' '.join(t for x,yy,t in sorted(band,key=lambda w:(w[1],w[0])) if 550<=x<C[0])
        st=' '.join(t for x,yy,t in sorted(band,key=lambda w:(w[1],w[0])) if C[0]<=x<C[1])
        ty=' '.join(t for x,yy,t in sorted(band,key=lambda w:(w[1],w[0])) if C[1]<=x<C[2])
        res.append([inc,date,tm,num,st,ty,p])
with open(out,'w') as f: json.dump(res,f)
