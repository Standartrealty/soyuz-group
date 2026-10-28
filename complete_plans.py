# -*- coding: utf-8 -*-
import json,re,hashlib
from pathlib import Path
from PIL import Image
from inspect_source import parse
R=Path(__file__).parent;S=R/'source-content';cat=json.loads((S/'catalog.json').read_text());lookup={x['url']:R/x['local'] for x in cat['assets'] if 'local'in x};data=json.loads((R/'data.json').read_text());usage=json.loads((S/'usage-manifest.json').read_text())
def save(u,thumb=False):
 if not u:return None
 im=Image.open(lookup[u]);im.thumbnail((520,520) if thumb else (1600,1600));name=hashlib.sha256(u.encode()).hexdigest()[:14]+('-thumb' if thumb else '')+'.webp';im.save(R/'assets'/name,'WEBP',quality=85);usage.append({'source':u,'local':'assets/'+name});return '/assets/'+name
for p in data:
 if p['plans']:continue
 r=parse(S/('portfolio_'+p['id']+'.html'));anchors={n.a['href'].lstrip('#'):n for n in r.nodes() if n.tag=='a' and 'wd-open-popup'in n.a.get('class','')};seen=set()
 for n in r.nodes():
  if 'wd-popup-element' not in n.a.get('class',''):continue
  t=' '.join(n.text().split());m=re.search(r'(\d).*?комнатная.*?Площадь\s*\(\s*м2\s*\)\s*(\d+(?:[.,]\d+)?)',t)
  if not m:continue
  a=anchors.get(n.a.get('id'));imgs=[x.a.get('data-lazy-src',x.a.get('src')) for x in a.nodes() if x.tag=='img'] if a else [];u=next((u for u in imgs if u in lookup),None)
  if u and u in seen:continue
  if u:seen.add(u)
  kind='studio' if a and 'студия'in a.text() else m.group(1);area=m.group(2).replace('.',',');p['plans'].append({'id':p['id']+'-'+str(len(p['plans'])+1),'projectId':p['id'],'project':p['name'],'city':'Каспийск','type':kind,'name':'Студия' if kind=='studio' else kind+'-комнатная','area':area,'image':save(u),'thumb':save(u,True),'source':p['source'],'imageSource':u,'originalPopup':n.a.get('id'),'note':None if u else 'Изображение этой планировки в исходной карточке не опубликовано.'})
(R/'data.json').write_text(json.dumps(data,ensure_ascii=False));allplans=[x for p in data for x in p['plans']];(R/'home-plans.json').write_text(json.dumps(allplans,ensure_ascii=False));(S/'usage-manifest.json').write_text(json.dumps(usage,ensure_ascii=False,indent=2));print('Plans',len(allplans),'with images',sum(bool(p['image']) for p in allplans))
p=R/'app.js';s=p.read_text();old='<button class="home-plan-image" data-image="${p.image}"';s=s.replace(old,'${p.image?`<button class="home-plan-image" data-image="${p.image}"');s=s.replace('<span class="plan-zoom" aria-hidden="true">↗</span></button><h3>','<span class="plan-zoom" aria-hidden="true">↗</span></button>`:`<div class="home-plan-image plan-unavailable"><span>Схема уточняется<br><small>В исходной карточке нет изображения</small></span></div>`}<h3>');p.write_text(s)
p=R/'style.css';p.write_text(p.read_text()+'\n.plan-unavailable{display:grid;place-items:center;padding:20px;text-align:center;background:#efefe9;color:#777b70;font-size:17px}.plan-unavailable small{display:block;font-size:11px;margin-top:10px}\n')
