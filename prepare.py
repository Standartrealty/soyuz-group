# -*- coding: utf-8 -*-
import json,re,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageOps
from inspect_source import parse
R=Path(__file__).parent;S=R/'source-content';A=R/'assets';cat=json.loads((S/'catalog.json').read_text());lookup={x['url']:R/x['local'] for x in cat['assets'] if 'local'in x};usage=[]
def save(u,name=None,width=1500):
 if u not in lookup:return None
 try:
  im=Image.open(lookup[u]);im.thumbnail((width,width));p=A/((name or hashlib.sha256(u.encode()).hexdigest()[:14])+'.webp');im.save(p,'WEBP',quality=85);usage.append({'source':u,'local':'assets/'+p.name});return '/assets/'+p.name
 except:return None
def src(n):return n.a.get('data-lazy-src',n.a.get('src',''))
def gallery(n):return list(dict.fromkeys(src(x) for x in n.nodes() if x.tag=='img' and 'wd-gallery-image'in x.a.get('class','') and src(x) in lookup))
specs=[('zhk-dostoyanie','Достояние'),('pzhsk-uyutnyy-dom','Уютный дом'),('zhk-admiral','Адмирал'),('zhk-nash-dom','Наш дом'),('zhk-ogni-stroy','Огни-Строй'),('zhk-semeynyy','Семейный'),('zhk-kaspiyskiy','Каспийский'),('pzhsk-kapital-siti','Капитал-сити')]
projects=[];plans=[];conflicts=[]
for slug,name in specs:
 root=parse(S/('portfolio_'+slug+'.html'));gs=[n for n in root.nodes() if 'wd-images-gallery'in n.a.get('class','')];photos=gallery(gs[0]);photos=[u for u in photos if u in lookup];images=[save(u,slug+'-photo-'+str(i)) for i,u in enumerate(photos)];images=[u for u in images if u];seen=set();pp=[]
 for n in root.nodes():
  if 'wd-popup-element' not in n.a.get('class',''):continue
  t=' '.join(n.text().split());m=re.search(r'(\d).*?комнатная.*?Площадь\s*\(\s*м2\s*\)\s*(\d+(?:[.,]\d+)?)',t)
  imgs=gallery(n)
  if not m or not imgs:continue
  u=imgs[0]
  if u in seen:continue
  seen.add(u);kind=m.group(1);area=m.group(2).replace('.',',');kind='studio' if 'stud' in u or 'студи' in t.lower() else kind;label='Студия' if kind=='studio' else kind+'-комнатная';img=save(u,width=1600);thumb=save(u,hashlib.sha256(u.encode()).hexdigest()[:14]+'-thumb',520)
  if not img:continue
  p={'id':slug+'-'+str(len(pp)+1),'projectId':slug,'project':name,'city':'Каспийск','type':kind,'name':label,'area':area,'image':img,'thumb':thumb,'source':'https://soyuz05.ru/portfolio/'+slug+'/','imageSource':u,'originalPopup':n.a.get('id')};pp.append(p);plans.append(p)
 docs=[]
 for n in root.nodes():
  u=n.a.get('href','');t=' '.join(n.text().split())
  if n.tag=='a' and t and ('Собрание'in t or 'разрешение'in t.lower()) and u.startswith(('http','/wp-')):docs.append({'name':t,'url':u.replace('http://soyuz05.ru','https://soyuz05.ru')})
 projects.append({'id':slug,'name':name,'city':'Каспийск','status':'Проект компании','image':images[0] if images else None,'gallery':images,'plans':pp,'description':'Жилой проект группы компаний «Союз». На странице проекта представлены фотографии, архитектурные визуализации, планировочные решения и материалы для участников кооператива.','address':'Уточните расположение в офисе продаж','year':'Уточняется в офисе продаж','installment':'На период строительства','deposit':'Индивидуальные условия','documents':docs,'source':'https://soyuz05.ru/portfolio/'+slug+'/'})
(R/'data.json').write_text(json.dumps(projects,ensure_ascii=False));(R/'home-plans.json').write_text(json.dumps(plans,ensure_ascii=False));(R/'completed.json').write_text('[]')
save(next(x['url'] for x in cat['assets'] if x['url'].endswith('vapvapv-1.png')),'logo',500)
# Covers are actual first images of each official project gallery.
im=Image.open(R/projects[0]['image'].lstrip('/'));im.save(A/'hero.webp','WEBP',quality=88)
im=Image.open(R/projects[6]['image'].lstrip('/'));im.save(A/'selection.webp','WEBP',quality=88)
docroot=parse(S/'dokumenty.html');docs=[]
for n in docroot.nodes():
 if n.tag=='a' and n.a.get('href') in lookup and n.a['href'].lower().endswith(('.jpg','.png','.pdf')):docs.append({'image':save(n.a['href'],width=1800),'source':n.a['href']})
(R/'documents.json').write_text(json.dumps(docs,ensure_ascii=False))
(S/'usage-manifest.json').write_text(json.dumps(usage,ensure_ascii=False,indent=2))
# Contact sheet for visual selection.
out=Image.new('RGB',(1200,((len(projects)+3)//4)*290),'white');d=ImageDraw.Draw(out)
for i,p in enumerate(projects):
 im=Image.open(R/p['image'].lstrip('/')).convert('RGB');im=ImageOps.contain(im,(290,250));x=(i%4)*300;y=(i//4)*290;out.paste(im,(x,y));d.text((x+5,y+255),p['id'],fill='black')
out.save(R/'covers-review.jpg')
print('PROJECTS',len(projects),'PLANS',len(plans),'DOCS',len(docs),'ASSETS',len(list(A.iterdir())))
