#!/usr/bin/env python3
"""Check DVD archive assets, transcription, links and generated output."""
from pathlib import Path
from html.parser import HTMLParser
import json, subprocess, hashlib
ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'sam/pero/archive'
data=json.loads((D/'dvd-glossary.json').read_text())
class Doc(HTMLParser):
 def __init__(self): super().__init__();self.ids=[];self.links=[];self.images=[];self.parts=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  if tag=='a' and 'href' in a:self.links.append(a['href'])
  if tag=='img':self.images.append(a)
 def handle_data(self,s):self.parts.append(s)
p=Doc();p.feed((D/'index.html').read_text());plain='\n'.join(p.parts)
assert len(p.ids)==len(set(p.ids)),'Duplicate anchors'
assert len(data['terms'])==5 and len(data['pages'])==9
files=[]
for page in data['pages']:
 files.append(page['source_filename'])
 if 'duplicate_source_filename' in page:files.append(page['duplicate_source_filename'])
 for text in page.get('text',[]):assert text in plain,f'Missing original text: {page["key"]}'
 for sec in page.get('sections',[]):assert sec['text'] in plain
 for text in page['translation']:assert text in plain
assert len(files)==len(set(files))==10
for file in files:assert (D/'images'/file).is_file()
for image in p.images:assert image.get('alt') is not None
for href in p.links:
 if href.startswith('#'):assert href[1:] in p.ids,href
 elif href.startswith('/WinterSunBlog/'):
  path=ROOT/href[len('/WinterSunBlog/'):].split('#')[0]
  assert path.exists(),href
 elif '://' not in href:assert (D/href).exists(),href
entry=(ROOT/'sam/many-faces/index.html').read_text()
assert 'href="/WinterSunBlog/sam/pero/archive/"' in entry
assert 'c.id === "pero"' in entry
for f in ['index.html','dvd-transcription.txt']:
 before=(D/f).read_bytes();subprocess.run(['python3',str(ROOT/'tools/collinwood/render_archive.py')],check=True,stdout=subprocess.DEVNULL);assert (D/f).read_bytes()==before,'Generated file out of date'
assert not any(x in (D/'index.html').read_text() for x in ['libfile_','/workspace/','SOURCE_ORIGINAL_ID'])
print('PASS: 5 terms; all original paragraphs and translations; 10 image files; anchors, relative links, source labels and deterministic rendering.')
