import urllib.request,pathlib,concurrent.futures,io,re,json
from pypdf import PdfReader
ROOT=pathlib.Path(__file__).resolve().parent
sources={'temporal':'https://aclanthology.org/2026.acl-short.65.pdf','pitfalls':'https://arxiv.org/pdf/2506.00723','proper-scores':'https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jasa.pdf','calibration':'https://arxiv.org/pdf/1706.04599','cruxbench':'https://arxiv.org/pdf/2609.35879','forecastbench-paper':'https://arxiv.org/pdf/2409.19839','finsaber-paper':'https://arxiv.org/pdf/2505.07078'}
def task(item):
 k,u=item
 try:
  data=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=60).read()
  (ROOT/(k+'.pdf')).write_bytes(data)
  reader=PdfReader(io.BytesIO(data)); text='\n\n'.join(f'--- PAGE {i+1} ---\n'+(p.extract_text() or '') for i,p in enumerate(reader.pages))
  (ROOT/(k+'.txt')).write_text(text)
  (ROOT/(k+'-source.json')).write_text(json.dumps({'url':u,'pages':len(reader.pages),'bytes':len(data)},indent=2))
  return k,len(reader.pages),len(text)
 except Exception as e:return k,str(e)
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
 for result in ex.map(task,sources.items()):print(result,flush=True)
