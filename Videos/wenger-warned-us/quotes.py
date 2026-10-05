import json, re
from pathlib import Path
P = Path(__file__).resolve().parent
norm = lambda w: re.sub(r"[^a-z0-9']", '', w.lower().replace('’', "'"))
def words(clip):
    d = json.loads((P/'assets'/'clips'/f'{clip}.words.json').read_text(encoding='utf-8'))
    return [(a, b, norm(w)) for s in d for a, b, w in s['w'] if norm(w)]
def find(ws, phrase, after=0):
    p = [norm(x) for x in phrase.split()]
    for i in range(len(ws) - len(p) + 1):
        if ws[i][0] >= after and all(ws[i + k][2] == p[k] for k in range(len(p))): return i, i + len(p) - 1
    raise KeyError(phrase)
def resolve(q):
    ws = words(q['clip']); i, _ = find(ws, q['from']); _, j = find(ws, q['to'], ws[i][0])
    return max(0, ws[i][0] - 0.12), ws[j][1] + 0.25, ' '.join(w[2] for w in ws[i:j + 1])
if __name__ == '__main__':
    tot = 0
    for q in json.loads((P/'script.json').read_text(encoding='utf-8')):
        if q['type'] != 'quote': continue
        a, b, t = resolve(q); tot += b - a
        print(f"{q['name']:18} {a:7.2f}-{b:7.2f} ({b-a:4.1f}s) {t}")
    print('total quote time', round(tot, 1))
