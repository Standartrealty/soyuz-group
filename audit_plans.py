# -*- coding: utf-8 -*-
import json,re,hashlib
from pathlib import Path
from inspect_source import parse
R=Path(__file__).parent;S=R/'source-content';data=json.loads((R/'data.json').read_text());issues=[]
for p in data:
 root=parse(S/('portfolio_'+p['id']+'.html'));byurl={x['imageSource']:x for x in p['plans'] if x['imageSource']};seen={(x['type'],float(x['area'].replace(',','.')),x['imageSource']) for x in p['plans']}
 for n in root.nodes():
  if 'wd-popup-element' not in n.a.get('class',''):continue
  t=' '.join(n.text().split());m=re.search(r'(\d).*?комнатная.*?Площадь\s*\(\s*м2\s*\)\s*(\d+(?:[.,]\d+)?)',t)
  imgs=list(dict.fromkeys(x.a.get('data-lazy-src',x.a.get('src')) for x in n.nodes() if x.tag=='img' and 'wd-gallery-image'in x.a.get('class','')))
  if not m or not imgs:continue
  u=imgs[0];key=(m.group(1),float(m.group(2).replace(',','.')),u)
  if key in seen:continue
  seen.add(key);base=byurl.get(u)
  if not base:continue
  x=dict(base);x.update({'id':p['id']+'-'+str(len(p['plans'])+1),'type':m.group(1),'name':m.group(1)+'-комнатная','area':m.group(2).replace('.',','),'originalPopup':n.a.get('id')});p['plans'].append(x)
 groups={}
 for x in p['plans']:
  if x['imageSource']:groups.setdefault(x['imageSource'],[]).append(x)
 for u,items in groups.items():
  if len(set((x['area'],x['type']) for x in items))<2:continue
  for x in items:
   # One original illustration assigned to different areas is not a verified apartment-specific scheme.
   x['image']=None;x['thumb']=None;x['note']='В исходнике одна схема назначена разным площадям. Точное изображение нужно уточнить.'
  issues.append({'project':p['name'],'imageSource':u,'variants':[{'area':x['area'],'type':x['type']} for x in items]})
 types=sorted(set(x['type'] for x in p['plans']));p['formats']=' / '.join('Студии' if t=='studio' else t+'-комнатные' for t in types);areas=[float(x['area'].replace(',','.')) for x in p['plans']];p['description']='«'+p['name']+'» — проект группы компаний «Союз». В каталоге представлены '+str(len(p['plans']))+' вариантов площадью от '+str(min(areas)).replace('.',',')+' до '+str(max(areas)).replace('.',',')+' м² по опубликованным карточкам компании. В галерее — материалы официальной страницы. Наличие, точные параметры и условия покупки уточняйте в отделе продаж.'
(R/'data.json').write_text(json.dumps(data,ensure_ascii=False));pp=[x for p in data for x in p['plans']];(R/'home-plans.json').write_text(json.dumps(pp,ensure_ascii=False));(S/'plan-discrepancies.json').write_text(json.dumps(issues,ensure_ascii=False,indent=2));print('Total',len(pp),'schemes',sum(bool(x['image']) for x in pp),'pending',sum(not x['image'] for x in pp))
p=R/'app.js';s=p.read_text().replace('В исходной карточке нет изображения','Точное изображение уточняется');p.write_text(s)
p=R/'index.html';s=p.read_text().replace('Площади приведены по материалам проектов.<br>Стоимость и наличие уточняйте в отделе продаж.','Площади приведены по материалам проектов.<br>Для карточек с расхождениями схема уточняется.<br>Стоимость и наличие — в отделе продаж.');p.write_text(s)
