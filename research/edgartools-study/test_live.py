"""Sequential live SEC demonstration. Identity is supplied only by environment."""
import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'research/edgartools-eval-venv/lib/python3.12/site-packages'))
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    identity = os.environ.get('EDGAR_IDENTITY', '').strip()
    if not identity:
        raise SystemExit('EDGAR_IDENTITY is required')
    out = Path(__file__).parent / ('live-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    out.mkdir()
    params = StdioServerParameters(command=sys.executable,
        args=[str(Path(__file__).with_name('run_mcp.py'))], env={'EDGAR_IDENTITY': identity})
    calls = []
    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            async def call(name, args):
                print('Calling ' + name, flush=True)
                try:
                    result = await asyncio.wait_for(session.call_tool(name, args), timeout=150)
                    raw = result.model_dump(mode='json')
                    parsed = [json.loads(x.text) for x in result.content if x.type == 'text']
                    record = {'tool': name, 'arguments': args, 'retrieved_at': datetime.now(timezone.utc).isoformat(),
                              'raw_mcp': raw, 'parsed': parsed}
                except Exception as exc:
                    record = {'tool': name, 'arguments': args, 'error': type(exc).__name__ + ': ' + str(exc)}
                calls.append(record)
                (out / (str(len(calls)) + '-' + name + '.json')).write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
                print(json.dumps(record, ensure_ascii=False)[:22000], flush=True)
                return record.get('parsed', [{}])[0]
            company = await call('edgar_company', {'identifier': 'NVDA', 'include': ['profile','financials','filings'], 'periods': 3, 'period': 'quarterly'})
            # If access is blocked or throttled, retain the failure and stop.
            if company.get('success'):
                filing = await call('edgar_filing', {'identifier':'NVDA','form':'10-Q','detail':'standard'})
                if filing.get('success'):
                    data = filing.get('data', {})
                    accession = data.get('accession_number')
                    args = {'sections':['mda']}
                    if accession:
                        args['accession_number'] = accession
                    else:
                        args.update(identifier='NVDA', form='10-Q')
                    await call('edgar_read', args)
    manifest = {'scope':'live SEC MCP calls; unmodified tool responses', 'directory':str(out), 'call_count':len(calls)}
    (out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(manifest, ensure_ascii=False), flush=True)

if __name__ == '__main__':
    asyncio.run(main())
