# -*- coding: utf-8 -*-
import concurrent.futures,hashlib,json,re,subprocess,html
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin,urlparse,urlunparse,quote,unquote
ROOT=Path(__file__).parent/'source-content';ROOT.mkdir(exist_ok=True);BASE='https://soyuz05.ru/'
EXT=('.jpg','.jpeg','.png','.svg','.webp','.gif','.mp4','.webm','.pdf','.ico')
def clean(u):
 u=html.unescape(u).replace('\\/','/');p=urlparse(urljoin(BASE,u));return urlunparse((p.scheme,p.netloc,quote(unquote(p.path),safe='/@:+'),p.params,p.query,''))
def fetch(u):return subprocess.check_output(['curl','-fLsS','--max-time','35',clean(u)],stderr=subprocess.DEVNULL)
class Extract(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.text=[];self.links=[];self.assets=set();self.skip=0
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t in ('script','style'):self.skip+=1
  if t=='a' and a.get('href'):self.links.append(a['href'])
  for k in ('src','data-src','data-lazy-src','data-original','poster','href'):
   u=a.get(k,'')
   if urlparse(u).path.lower().endswith(EXT):self.assets.add(clean(u))
  for k in ('srcset','data-srcset','data-lazy-srcset'):
   for z in a.get(k,'').split(','):
    if z.strip():self.assets.add(clean(z.strip().split()[0]))
  if t in ('p','div','h1','h2','h3','li','br') and not self.skip:self.text.append('\n')
 def handle_endtag(self,t):
  if t in ('script','style'):self.skip=max(0,self.skip-1)
  if t in ('p','div','h1','h2','h3','li') and not self.skip:self.text.append('\n')
 def handle_data(self,d):
  if not self.skip:self.text.append(d)
queue=[BASE,BASE+'robots.txt',BASE+'sitemap.xml'];visited=set();records=[];assets={}
def page(u):
 try:
  raw=fetch(u);p=urlparse(u);name=unquote(p.path).strip('/').replace('/','_') or 'home';name=name if name.endswith(('.txt','.xml')) else name+'.html';target=ROOT/name;target.write_bytes(raw);decoded=raw.decode('utf-8','replace');rec={'url':u,'local':str(target.relative_to(ROOT.parent))};links=[]
  if name.endswith('.xml'):links=re.findall(r'<loc>(.*?)</loc>',decoded)
  elif name.endswith('.html'):
   x=Extract();x.feed(decoded);target.with_suffix('.txt').write_text('\n\n'.join(' '.join(t.split()) for t in ''.join(x.text).splitlines() if t.strip()));links=x.links;rec['links']=links
   for a in x.assets:assets.setdefault(a,[]).append(u)
   for a in re.findall(r'https?://[^\s\x22\x27<>\\)]+\.(?:jpg|jpeg|png|svg|webp|mp4|webm|pdf)',html.unescape(decoded).replace('\\/','/')):assets.setdefault(clean(a),[]).append(u)
  return rec,links
 except Exception as e:return {'url':u,'error':str(e)},[]
while queue:
 batch=[]
 while queue and len(batch)<6:
  u=clean(queue.pop(0));p=urlparse(u)
  if u in visited or p.netloc not in ('soyuz05.ru','www.soyuz05.ru'):continue
  if p.query or p.path.startswith(('/wp-json','/wp-admin','/feed','/wp-content')) or p.path.endswith(EXT):continue
  visited.add(u);batch.append(u)
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
  for rec,links in pool.map(page,batch):
   records.append(rec);print('PAGE',rec['url'],'ERROR' if 'error'in rec else '',flush=True)
   for link in links:
    u=clean(urljoin(rec['url'],link))
    if u not in visited:queue.append(u)
(ROOT/'assets').mkdir(exist_ok=True)
def save(item):
 u,sources=item;ext=Path(urlparse(u).path).suffix.lower();p=ROOT/'assets'/(hashlib.sha256(u.encode()).hexdigest()[:18]+ext)
 if ext not in EXT:return {'url':u,'sources':sources,'status':'link only'}
 try:
  if not p.exists():p.write_bytes(fetch(u))
  return {'url':u,'local':str(p.relative_to(ROOT.parent)),'sources':sorted(set(sources)),'bytes':p.stat().st_size}
 except Exception as e:return {'url':u,'sources':sources,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:media=list(pool.map(save,assets.items()))
(ROOT/'catalog.json').write_text(json.dumps({'pages':records,'assets':media},ensure_ascii=False,indent=2));print('DONE',len(records),'pages',len(media),'assets',sum('local'in x for x in media),'saved',flush=True)
