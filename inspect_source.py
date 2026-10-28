from html.parser import HTMLParser
from pathlib import Path
class Node:
 def __init__(self,tag,a):self.tag=tag;self.a=dict(a);self.children=[]
 def text(self):return ' '.join(x if isinstance(x,str) else x.text() for x in self.children)
 def nodes(self):
  yield self
  for x in self.children:
   if isinstance(x,Node):yield from x.nodes()
class Parser(HTMLParser):
 def __init__(self):super().__init__();self.root=Node('root',[]);self.stack=[self.root]
 def handle_starttag(self,t,a):
  n=Node(t,a);self.stack[-1].children.append(n)
  if t not in ['img','input','meta','link','br','hr','source','wbr','area','embed']:self.stack.append(n)
 def handle_endtag(self,t):
  for i in range(len(self.stack)-1,0,-1):
   if self.stack[i].tag==t:self.stack=self.stack[:i];break
 def handle_data(self,d):self.stack[-1].children.append(d)
def parse(path):p=Parser();p.feed(Path(path).read_text());return p.root
if __name__=='__main__':
 for slug in ['dynasty','vesna','moscow']:
  print(slug)
  root=parse('source-content/projects_'+slug+'.html')
  for n in root.nodes():
   if 'tn-group' in n.a.get('class',''):
    txt=n.text().strip();imgs=[a.a.get('data-original',a.a.get('src','')) for a in n.nodes() if a.tag=='img']
    if 'м²' in txt and len(txt)<100 and imgs:print(repr(txt),imgs)
