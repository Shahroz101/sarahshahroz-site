"""prep2.py <prefix> <slug> <source.html>  -> <prefix>_parsed.json, <prefix>_name_map.json, images, sheets, text dump"""
import re, json, os, subprocess, html, sys
from PIL import Image, ImageDraw
S=os.path.dirname(os.path.abspath(__file__))
prefix, slug, src = sys.argv[1:4]
s=open(os.path.expanduser(src),encoding="utf-8").read()
LOCAL=f"/Users/shahrozburhan/Desktop/Websites/Dwelling Dream Blog/uploads/blog/2026/11/{prefix}"
OUT=f"/Users/shahrozburhan/Desktop/Websites/Sarah Shahroz/images/articles/{slug}"
figs=re.findall(r'<figure[^>]*><img src="([^"]+)" alt="([^"]*)".*?<a href="https://www.pinterest.com/pin/(\d+)/?">Photo via Pinterest — ([^<]+)</a>',s,re.S)
def slugify(t): return re.sub(r'[^a-z0-9]+','-',html.unescape(t).lower()).strip('-')[:60].strip('-')
parsed=[];names={};used=set()
for i,(img,alt,pin,label) in enumerate(figs,1):
    parsed.append({"num":i,"image":img,"pin":pin,"products":[],"recipe":None,"label":label})
    n=slugify(label)
    if n in used or n=="hero": n=f"{n}-{i}"
    used.add(n); names[str(i)]=n
json.dump(parsed,open(f"{S}/{prefix}_parsed.json","w"),indent=1)
json.dump(names,open(f"{S}/{prefix}_name_map.json","w"),indent=1)
os.makedirs(OUT,exist_ok=True)
for i,(img,*_) in enumerate(figs,1):
    f=f"{LOCAL}/{prefix}-idea{i}.jpg"
    if not os.path.exists(f): print("MISSING",f); continue
    subprocess.run(["sips","-Z","1600","-s","format","jpeg","-s","formatOptions","78",f,"--out",f"{OUT}/{names[str(i)]}.jpg"],capture_output=True)
W,H,cols=300,420,6
for sh,a in enumerate(range(1,len(figs)+1,12),1):
    idx=list(range(a,min(a+12,len(figs)+1)))
    rows=(len(idx)+cols-1)//cols
    im=Image.new("RGB",(W*cols,H*rows),"white"); d=ImageDraw.Draw(im)
    for k,i in enumerate(idx):
        p=Image.open(f"{OUT}/{names[str(i)]}.jpg").convert("RGB"); p.thumbnail((W-8,H-8))
        x=(k%cols)*W;y=(k//cols)*H; im.paste(p,(x+4,y+4)); d.rectangle([x+4,y+4,x+50,y+34],fill="black"); d.text((x+10,y+10),str(i),fill="white")
    im.save(f"{S}/{prefix}_sheet{sh}.jpg",quality=68)
body=re.sub(r'<figure.*?</figure>','[FIG]',s,flags=re.S)
body=re.sub(r'<h2[^>]*>(?:<strong>)?(.*?)(?:</strong>)?</h2>',r'\n## \1\n',body)
body=re.sub(r'</li>','\n',body); body=re.sub(r'</p>','\n',body)
body=re.sub(r'<style.*?</style>','',body,flags=re.S); body=re.sub(r'<[^>]+>','',body)
open(f"{S}/{prefix}_text.txt","w").write(html.unescape(re.sub(r'\n{3,}','\n\n',body)))
print(prefix,len(figs),"images; sheets",(len(figs)+11)//12)
