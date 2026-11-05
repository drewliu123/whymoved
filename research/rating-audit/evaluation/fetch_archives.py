import urllib.request,tarfile,io,pathlib,concurrent.futures,json
R=pathlib.Path(__file__).resolve().parent
repos=[('gpleiss/temperature_scaling','ce1154ec7d5235eee046f28875c3dd8421f11d45'),('ai-prophet/cruxbench','c036b3cd94881dc9efba448b7c02594db1b408fd'),('theolivecode/WebDataLeakageAudit','02ad57569ebe963efdcf0c28de6a8543ae3b0a1e')]
def f(item):
 n,c=item;d=R/n.split('/')[-1];d.mkdir(exist_ok=True);u=f'https://codeload.github.com/{n}/tar.gz/{c}'
 try:
  b=urllib.request.urlopen(u,timeout=60).read();t=tarfile.open(fileobj=io.BytesIO(b),mode='r:gz');paths=[]
  for m in t.getmembers():
   p='/'.join(m.name.split('/')[1:])
   if m.isfile() and (p.endswith('.py') or p.lower() in ['readme.md','license','license.md','license.txt','requirements.txt','pyproject.toml']):
    (d/p.replace('/','__')).write_bytes(t.extractfile(m).read());paths.append(p)
  (d/'metadata.json').write_text(json.dumps({'repository':n,'commit':c,'url':u,'saved':paths},indent=2));print(n,paths)
 except Exception as e:print(n,str(e))
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:list(ex.map(f,repos))
