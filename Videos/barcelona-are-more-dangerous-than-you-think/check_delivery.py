from pathlib import Path
import re,urllib.parse
P=Path(__file__).resolve().parent
h=(P/'START_HERE.html').read_text(encoding='utf8')
refs=re.findall(r'(?:href|src)="([^"]+)"',h)
missing=[r for r in refs if not r.startswith(('http','#','$')) and not (P/urllib.parse.unquote(r)).exists()]
print('Missing static links:',missing)
assert not missing
print('Gallery:',re.search(r'for\(const i of .*?\)',h).group(0))
q=P/'final video/FINAL_QC.md'
t=q.read_text(encoding='utf-8-sig')
note='## Revised edition\n\nThe current master replaces all 33 tactical slots with 33 contextual animations. Audio is bit-identical to the approved original. Three new thumbnail designs are delivered in assets/thumbnail/v2. See REVISION_NOTES.md and revision_v2_qc.json for current evidence. The notes below describe the original delivery.\n\n'
if not t.startswith('## Revised edition'):q.write_text(note+t,encoding='utf8')
