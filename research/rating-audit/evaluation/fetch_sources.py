"""Read-only upstream evidence collection; never executes fetched code."""
import urllib.request, json, pathlib, concurrent.futures, re
ROOT=pathlib.Path(__file__).resolve().parent
HEADERS={'User-Agent':'static-research-audit','Accept':'application/vnd.github+json'}
def get(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers=HEADERS),timeout=60) as r:return r.read()
def repo(name):
    d=ROOT/name.split('/')[-1];d.mkdir(exist_ok=True)
    info=json.loads(get('https://api.github.com/repos/'+name));branch=info['default_branch']
    commit=json.loads(get(f'https://api.github.com/repos/{name}/commits/{branch}'))['sha']
    tree=json.loads(get(f'https://api.github.com/repos/{name}/git/trees/{commit}?recursive=1'))
    (d/'metadata.json').write_text(json.dumps({'repository':name,'commit':commit,'info':info,'tree':tree},indent=2))
    paths=[x['path'] for x in tree['tree'] if x['type']=='blob']
    print(name,commit,'\n'+'\n'.join(paths),flush=True)
    for p in paths:
        if p.lower() in ['readme.md','license','license.txt','license.md','pyproject.toml','requirements.txt']:
            try:(d/p.replace('/','__')).write_bytes(get(f'https://raw.githubusercontent.com/{name}/{commit}/{p}'))
            except Exception as e: print('ERR',p,str(e))
    return name,commit
if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        list(ex.map(repo,['forecastingresearch/forecastbench','waylonli/FINSABER','VectorInstitute/agentic-forecasting']))
