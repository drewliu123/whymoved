# Independent correctness/security review — 2026-10-31

Result: **blocking findings remain**. This report records reproduced defects, not a release approval. Product code was not edited and nothing was published. The sole requested persistent write is this report.

## Scope and evidence

Reviewed `/Users/frankzhang/Desktop/投研助手/scripts/{sources,check_claims,research_plan,render_report,research_run}.py`, the research SKILL and linked source/evidence/report contracts, and the associated tests. Inspected `evidence/rebuild-20261031/baseline.zip` directly with Python `zipfile` (no extraction or archived code execution). `sources.py`, `research_plan.py`, `render_report.py`, and `research_run.py` are additions relative to that baseline. The legacy `check_claim` function is AST-identical to the baseline.

Executed `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests`: exit **0**, **92 tests passed**, 4.464 seconds. Tests and targeted probes ran locally without retrieval or credentials; temporary CLI inputs were confined to a temporary directory and removed. Existing tests passing does not cover the defects below.

Concurrent owner edits occurred during review. Latest inspected SHA-256 values:

| File | SHA-256 |
|---|---|
| scripts/sources.py | b28cd46a7b4691d26e78468cc24ab5a5c014c86ace6ac948e839593756b0890f |
| scripts/check_claims.py | af08a61a139a956418aa39c001c63f3c02167daa4bbcdb0116d4045192c6c530 |
| scripts/research_plan.py | d6bc0f8b8323c49eef07c42d2d3be60f9443b3a7e2233aaaa987a81ba195ef41 |
| scripts/render_report.py | deb12dffeef79bdfad9b80442bd05d6685f780b8fcb1edb8cfb56ff16887c859 |
| scripts/research_run.py | 078f5598a5943fd3d00fb57e83925dd4bebf37334b732cf898fdce6af7d6ac33 |
| skills/research/SKILL.md | ae155bb61470e8bf9166a1517364ca8a78222cd7fd3fa680177b7f6f4625061a |

The 92-test run preceded the latest renderer/archive owner edits; it must not be represented as testing their final versions. Line references below refer to the inspected snapshots and may move.

## Verified findings

### F1 — High / blocking: a caller-supplied canonical URL bypasses the same-document independence guard

Locations: `scripts/sources.py:154–156`; `scripts/check_claims.py:130–135`, `190–209`.

`validate_sources` checks only that `canonical_url` has the same hostname as `url`. `_strict_claim` trusts this value instead of also tracking the normalized actual URL. Two fragments with the **same actual URL** can provide different same-host canonical paths and different origin IDs. A fact supported only by these two T2 fragments then passes as independently corroborated. This directly contradicts the explicit same-document guard and its existing regression test; that test omits the canonical override.

Reproduction, run from any trusted directory:

```python
import sys
from pathlib import Path
root = Path('/Users/frankzhang/Desktop/投研助手')
sys.path[:0] = [str(root/'scripts'), str(root/'tests')]
from test_sources import candidate, document
from test_evidence_v2 import claim, ledger
from check_claims import validate_ledger
s = document(
    candidate(url='https://example.com/article', canonical_url='https://example.com/a'),
    candidate('S2', url='https://example.com/article', canonical_url='https://example.com/b'),
)
print(validate_ledger(ledger(claim(sources=[{'source_id':'S1'}, {'source_id':'S2'}])), s))
```

Observed: `{'passed': True, 'total': 1, 'failures': {}}`.

Expected: reject the alleged two-origin corroboration. Track the canonicalized original URL as well as any accepted canonical alias; an unverified alias cannot manufacture document independence. This is an evidence-integrity bypass, not a claim that the validator can establish real-world source truth.

### F2 — Medium / blocking: price claims can attach unqualified evidence alongside one qualified source

Location: `scripts/check_claims.py:144–150`, `215–218`, `248–252`, `278–283`.

The per-reference loop accepts `market_quote`/`survey` evidence at T2 if its self-declared `supports` matches. The price branch filters to T0/T1 and checks only the filtered set; it does not reject the remaining resolved references. Thus a valid official quote lets a T2 quote without any `market_quote` metadata pass as support for the same price claim. This violates the stated T0/T1-only price qualification and hides missing quote identity/time fields on the attached T2 source. The existing T3/T4 piggyback checks do not cover T2 prices. The same filtering pattern exists for consensus: T0 survey references fall outside its qualified T1/T2 set and escape survey metadata checks when a valid T1 source is present; the concrete executed reproduction below establishes the price case.

Reproduction using the imports from F1:

```python
s1 = candidate(tier='T0', supports=['price'], evidence_kind='market_quote', market_quote={
    'quoted_at':'2026-10-31T12:00:00Z', 'instrument':'ABC', 'outcome':'ABC share',
    'direction':'buy', 'value':50, 'unit':'USD', 'quote_type':'indicative'})
s2 = candidate('S2', tier='T2', supports=['price'], evidence_kind='market_quote')
c = claim(ctype='price', price_kind='indicative', sources=[{'source_id':'S1'}, {'source_id':'S2'}])
print(validate_ledger(ledger(c), document(s1, s2)))
```

Observed: `{'passed': True, 'total': 1, 'failures': {}}`.

Expected: every source attached as support for a price claim must satisfy its qualification; reject S2 or keep it as unreferenced background. Do not merely count the presence of one valid source.

### F3 — Medium / blocking: accepted non-inference `basis` can crash both renderers and prevent archive

Locations: `scripts/check_claims.py:290–293`; `scripts/render_report.py:369`, `442`.

Only inference claims validate `basis`. The renderer unconditionally joins `basis` on every claim. A fact with `basis=[{}]` passes both strict ledger and report validation, then crashes rendering with TypeError. `basis=None` has the same structural mismatch. This makes a successful validation insufficient to render or archive otherwise valid inputs.

Reproduction:

```python
import sys
from pathlib import Path
root = Path('/Users/frankzhang/Desktop/投研助手')
sys.path[:0] = [str(root/'scripts'), str(root/'tests')]
from test_reports import documents
from render_report import validate_report, render_html, render_markdown
r, l, s = documents()
l['claims'][0]['basis'] = [{}]
print(validate_report(r, l, s))
render_html(r, l, s)  # render_markdown fails identically
```

Observed validation: `[]`.
Observed rendering: `TypeError: sequence item 0: expected str instance, dict found`.

Reconfirmed after the latest renderer edits. Expected: structural rejection with a useful validation message, or ignore irrelevant basis fields consistently; never claim this input is renderable and then fail at string joining.

### F4 — Medium: malformed imported engine identity raises an uncaught exception instead of a compatibility error

Location: `scripts/sources.py:355–358` (also source-item identity handling at 309–311).

Before validating the ranked row's source and item identity, the importer uses them as a dictionary key. Valid JSON with a list/object identity crashes instead of producing the advertised `last30days compatibility error`. Existing malformed-import tests cover missing fields but not wrong identity types.

Reproduction:

```python
# imports/root setup as in F1
from test_sources import raw_report
from sources import import_last30days
raw = raw_report()
raw['ranked_candidates'][0]['source'] = []
import_last30days(raw)
```

Observed: `TypeError: unhashable type: 'list'` at `original = items.get((row.get('source'), row.get('item_id')))`. The same raw JSON was passed to `sources.py import-last30days INPUT --out OUTPUT`: exit **1**, empty stdout, Python traceback on stderr, no structured compatibility explanation. The CLI catches ValueError but not this TypeError; its declared compatibility-error path exits 2.

Expected: validate source/item identifier types before dictionary lookup and raise the normal compatibility error. This is a robustness failure at an external-data boundary, not code execution.

### F5 — Low: large valid JSON integers crash finite-number validation

Location: `scripts/check_claims.py:235`, `238` (and the corresponding finite-value helper in `render_report.py:246–247`).

Python permits arbitrary-size JSON integer values; `math.isfinite` converts them to float and can raise OverflowError. The strict validator and CLI do not catch it. A finite-number check should reject out-of-range values with a normal diagnostic rather than terminate without JSON output.

Reproduction: use the valid price source/claim from F2, set `s1['market_quote']['value'] = 10**1000`, then run `validate_ledger(ledger(claim(ctype='price', price_kind='indicative')), document(s1))`.

Observed: `OverflowError: int too large to convert to float`.
The corresponding `check_claims.py CLAIMS --sources SOURCES --json` invocation exited **1**, emitted no stdout JSON, and ended with that traceback. This is a 1001-digit integer accepted by the normal JSON parser, without `NaN`/`Infinity` or deeply nested input.

## Reviewed limits and non-findings

- Existing source tests cover semantic priority over engagement, retaining unranked raw pool entries, exact-fragment dedup, confirmed retransmissions, and topic-cluster non-dedup. No additional reproducible silent ranking-loss defect was established in this pass.
- Existing strict tests exercise cutoff dates, later retrieval/availability, unknown historical publication dates, origin families, attributed statements, survey scope and timing, and inference cycles. F1 is a concrete uncovered independence bypass. The validator still cannot verify the truth of user-supplied provenance annotations or source semantics.
- Existing literal-rendering tests verify malicious HTML strings remain text, one fixed script element, protocol-restricted links, and no injected image elements. I found no independently reproduced HTML/JavaScript injection in the inspected renderer. This is bounded evidence, not an exhaustive security certification; no browser execution was performed.
- Existing archive tests exercise no-overwrite, temporary staging cleanup, input/output symlinks, path traversal, tamper hashes, parent tampering, updates, and structured period/unit/scope changes. Latest owner changes visibly add strict schema2 archive enforcement, audit metadata, source identity fields in diffs, reservation-file listing handling, GFM table blocks, and embedded-source fallback. This pass does not claim end-to-end validation of those concurrent fixes. No race-condition or power-loss durability experiment was performed.
- Standalone schema1 compatibility was intentionally retained. `check_claim` AST matches the baseline, and the observed test run included legacy journal/forecast/author regressions. Legacy rendering being accepted with an explicit legacy warning is not reported as a defect; new archives now visibly require schema2.
- Review tooling limitation: invoking the available `code-review` skill unexpectedly used its forked execution mode. No Agent tool was called by this reviewer and no further delegation was requested. All findings F1–F5 above were reproduced directly by this reviewer; the skill output was not accepted as independent proof. This differs from the requested no-subagents execution constraint and is disclosed rather than hidden.

## Handoff

Fix F1–F4 before treating the rebuilt strict research pipeline as ready. F5 is a lower-priority input-diagnostic fix. Add focused regressions for the reproduced cases, then rerun the complete suite after owners finish edits. Final package/manifest consistency, live Last30Days retrieval, browser behavior, and a stable final-tree end-to-end archive/update run were not validated by this review.


## Post-fix verification — 2026-10-31T18:39:48Z

**Current blocking status: F1–F5 are resolved for the originally reproduced cases. No blocking finding from this report remains open at the hashes below.** The original observations and severity assignments above are retained as historical evidence; the opening result describes the initial review snapshot, and this dated verification supersedes it for current status. This is a focused fix verification, not an overall release approval.

As requested, rechecked only F1–F5 using one direct probe run after inspecting the latest finite-number guards. No full suite, broad review, product edit, retrieval, or publication was performed. CLI inputs lived in a temporary directory that was removed. SHA-256 values before and after the probe matched for all six reviewed files, so these results refer to one stable snapshot.

| Finding | Direct verification result | Current status |
|---|---|---|
| F1 canonical alias / false independent origins | Original identical-actual-URL, distinct-canonical-path T2 reproduction now returns passed=false with R2 independent origin-family error. | Resolved for reproduction |
| F2 T2 price piggyback | Original valid T0 quote plus T2 market_quote without metadata now returns passed=false: R3 every referenced price source must be a T0/T1 market_quote. | Resolved for reproduction |
| F3 malformed fact basis | Both basis=[{}] and basis=null return report validation errors, including claim basis must be a list of strings and strict R7 error. Both HTML and Markdown renderers raise ordinary ValueError before rendering instead of the previous TypeError. | Resolved for reproduction |
| F4 malformed engine source | source=[] now raises ValueError with last30days compatibility error: candidate source/item_id must be strings. CLI exits 2, no traceback, no output file created. | Resolved for reproduction |
| F5 huge JSON integer | market_quote.value=10**1000 now returns passed=false with R3 finite-number diagnostic. CLI exits 1 with valid JSON failure output and empty stderr. A report table cell containing the same integer produces an ordinary table rows validation error rather than OverflowError. | Resolved for reproduction |

Positive control: the unmodified valid report/ledger/sources fixture returns no report errors and renders both HTML and Markdown. The probe command exited 0, including assertions for every stated rejection and the positive control. The F2 consensus analogy in the original discussion was not a separately reproduced finding and was not independently retested; resolution here concerns the concrete price reproduction only.

Verified snapshot SHA-256:

| File | SHA-256 |
|---|---|
| scripts/sources.py | af515463667c7d5bc6f904c163acd424adf48c3c0b94990757a4b5e172bb0671 |
| scripts/check_claims.py | 13ad8ce4747c33800c640a727fc04038ae276b5bd01844b3483d0ef1907bbb1d |
| scripts/research_plan.py | d6bc0f8b8323c49eef07c42d2d3be60f9443b3a7e2233aaaa987a81ba195ef41 |
| scripts/render_report.py | 3bae4155341e63132d391e3fa850a2569174d7d15f202f3c26aa5323cd995994 |
| scripts/research_run.py | 078f5598a5943fd3d00fb57e83925dd4bebf37334b732cf898fdce6af7d6ac33 |
| skills/research/SKILL.md | 3e1a653b6d869b51e5a10c3ef72e62fa82709741877b37d0b27e7eb0aa7e9c4c |

Final full-suite and end-to-end verification remain with the coordinator. No claim is made that the earlier 92-test run exercised this final snapshot.
