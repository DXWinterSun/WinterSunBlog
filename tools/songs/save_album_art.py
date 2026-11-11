#!/usr/bin/env python3
"""Download verified original album artwork into images/ and update the record wall."""
import json, re, urllib.request, urllib.parse, pathlib, io
from PIL import Image
ROOT=pathlib.Path(__file__).resolve().parents[2]
P=ROOT/"_data/songs.json"
data=json.loads(P.read_text())
TARGETS={
"get-rollin":("Nickelback","Get Rollin'","1641362574","us"),
"cant-love-cant-hurt":("Augustana","Can't Love, Can't Hurt","281556700","us"),
"a-different-light":("Sherwood","A Different Light","1050832256","us"),
"composure":("Waking Ashland","Composure","715569159","us"),
"the-way-it-was":("Parachute","The Way It Was","1440665176","us"),
"hui-dao-hai-yang":("逃跑计划","回到海洋","1858515737","us"),
"daylight":("Ron Pope","Daylight",None,"us"),
}
def get(url):
  request=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
  with urllib.request.urlopen(request,timeout=25) as response:return response.read()
def norm(s):return re.sub(r"[^\w]+","",s.lower())
fail=[]
for album in data["albums"]:
  aid=album["id"]
  if aid not in TARGETS:continue
  artist,title,apple_id,region=TARGETS[aid]
  try:
    if apple_id:
      url=f"https://itunes.apple.com/lookup?id={apple_id}&country={region}&entity=album"
    else:
      term=urllib.parse.quote(artist+" "+title)
      url=f"https://itunes.apple.com/search?term={term}&country={region}&entity=album&limit=100"
    entries=json.loads(get(url)).get("results",[])
    match=next((x for x in entries if x.get("wrapperType")=="collection" and norm(x.get("collectionName",""))==norm(title) and (norm(x.get("artistName",""))==norm(artist) or (aid=="hui-dao-hai-yang" and norm(x.get("artistName",""))==norm("Escape Plan")))),None)
    if not match:raise ValueError("No exact album/artist match")
    art=match["artworkUrl100"].replace("100x100bb","1200x1200bb").replace("100x100bf","1200x1200bf")
    img=Image.open(io.BytesIO(get(art))).convert("RGB")
    if img.width < 250 or img.height < 250:raise ValueError("Album image too small")
    cover=f"song-{aid}.jpg"
    img.save(ROOT/"images"/cover,format="JPEG",quality=90,optimize=True)
    album["cover"]=cover
    album.pop("cover_url",None)
    print("OK",artist,title,cover,img.size)
  except Exception as exc:
    fail.append((aid,str(exc)));print("ERROR",aid,exc)
P.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
if fail:print("UNRESOLVED",fail)
