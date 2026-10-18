#!/usr/bin/env python3
"""Builds activity.svg from a GitHub user's contribution calendar.
Usage: GITHUB_TOKEN=... python scripts/generate_activity.py Kabir2007 activity.svg
       python scripts/generate_activity.py Kabir2007 out.svg --demo | --empty
"""
import sys, os, json, random, datetime as dt, urllib.request

user, out = sys.argv[1], sys.argv[2]
mode = sys.argv[3] if len(sys.argv) > 3 else ''

def fetch():
    q = 'query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}'
    req = urllib.request.Request('https://api.github.com/graphql',
        data=json.dumps({'query': q, 'variables': {'u': user}}).encode(),
        headers={'Authorization': 'bearer ' + os.environ['GITHUB_TOKEN'], 'Content-Type': 'application/json', 'User-Agent': 'activity-svg'})
    r = json.load(urllib.request.urlopen(req))
    return [[(d['date'], d['contributionCount']) for d in w['contributionDays']]
            for w in r['data']['user']['contributionsCollection']['contributionCalendar']['weeks']]

def synthetic(zero):
    random.seed(7); end = dt.date.today(); start = end - dt.timedelta(days=370)
    start -= dt.timedelta(days=(start.weekday() + 1) % 7)
    weeks, d = [], start
    while d <= end:
        w = []
        for _ in range(7):
            n = 0 if (zero or d > end) else max(0, int(random.gauss(2, 3))) * (random.random() > .45)
            w.append((d.isoformat(), n)); d += dt.timedelta(days=1)
        weeks.append(w)
    return weeks

weeks = synthetic(mode == '--empty') if mode in ('--demo', '--empty') else fetch()
days = [x for w in weeks for x in w]
today = dt.date.today().isoformat()
days = [x for x in days if x[0] <= today]
total = sum(n for _, n in days)
longest = cur = 0
for _, n in days:
    cur = cur + 1 if n else 0; longest = max(longest, cur)
streak = 0
for _, n in reversed(days):
    if n: streak += 1
    elif streak or _ != today: break
best = max(days, key=lambda x: x[1]) if days else ('', 0)
wk = [sum(n for _, n in w) for w in weeks]
mx = max(max(n for _, n in days), 1)

A, A2 = '#f59e0b', '#fcd34d'
W, H = 1004, 372
GX, GY, CS, GAP = 44, 168, 14, 3.4
def level(n):
    if n == 0: return 0
    r = n / mx
    return 1 if r < .25 else 2 if r < .5 else 3 if r < .75 else 4
fills = ['#1c1917', '#78350f', '#b45309', '#f59e0b', '#fde68a']

s = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace">
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0c0a09"/><stop offset="1" stop-color="#14100c"/></linearGradient>
<linearGradient id="ar" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{A}" stop-opacity=".35"/><stop offset="1" stop-color="{A}" stop-opacity="0"/></linearGradient>
<clipPath id="reveal"><rect x="{GX}" y="60" width="0" height="100"><animate attributeName="width" from="0" to="{W-2*GX}" dur="5s" fill="freeze"/></rect></clipPath>
<style>
.c{{opacity:0;animation:pop .35s ease-out forwards}}
@keyframes pop{{0%{{opacity:0;transform:scale(.2)}}100%{{opacity:1;transform:scale(1)}}}}
.c{{transform-box:fill-box;transform-origin:center}}
.now{{animation:pulse 1.6s ease-in-out infinite}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.35}}}}
.cur{{animation:b 1s steps(1) infinite}}@keyframes b{{0%,49%{{opacity:1}}50%,100%{{opacity:0}}}}
</style>
</defs>
<rect width="{W}" height="{H}" rx="6" fill="url(#bg)"/>
<rect x=".75" y=".75" width="{W-1.5}" height="{H-1.5}" rx="6" fill="none" stroke="{A}" stroke-opacity=".35"/>
<rect width="6" height="{H}" fill="{A}"/>
<text x="{GX}" y="40" font-size="11" fill="{A}" letter-spacing="3">ACTIVITY TRACE</text>
<text x="{W-GX}" y="40" font-size="11" fill="#78716c" text-anchor="end">last 12 months · updated {today}</text>
<line x1="{GX}" y1="52" x2="{W-GX}" y2="52" stroke="#fff" stroke-opacity=".1"/>''']

# weekly trace
pw = (W - 2 * GX) / max(len(wk) - 1, 1); top, bot = 66, 148; wmx = max(max(wk), 1)
pts = [(GX + i * pw, bot - (v / wmx) * (bot - top)) for i, v in enumerate(wk)]
line = 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts)
s.append(f'<g clip-path="url(#reveal)"><path d="{line} L{pts[-1][0]:.1f} {bot} L{GX} {bot}Z" fill="url(#ar)"/><path d="{line}" fill="none" stroke="{A2}" stroke-width="1.6" stroke-linejoin="round"/></g>')
s.append(f'<line x1="{GX}" y1="{bot}" x2="{W-GX}" y2="{bot}" stroke="#fff" stroke-opacity=".08"/>')
lx, ly = pts[-1]
s.append(f'<circle class="now" cx="{lx:.1f}" cy="{ly:.1f}" r="4" fill="{A2}"/>')

# day grid, revealed oldest -> newest
months = ''
last_m = None
for ci, w in enumerate(weeks):
    x = GX + ci * (CS + GAP) * (W - 2 * GX) / (len(weeks) * (CS + GAP) - GAP)
for ci, w in enumerate(weeks):
    step = (W - 2 * GX + GAP) / len(weeks); x = GX + ci * step; cw = step - GAP
    m = w[0][0][5:7]
    if m != last_m and ci < len(weeks) - 2:
        s.append(f'<text x="{x:.1f}" y="{GY-8}" font-size="9.5" fill="#78716c">{dt.date.fromisoformat(w[0][0]).strftime("%b").upper()}</text>'); last_m = m
    for ri, (date, n) in enumerate(w):
        if date > today: continue
        delay = 0.4 + ci * 0.095 + ri * 0.012
        is_last = date == days[-1][0]
        s.append(f'<rect class="c{" now" if is_last else ""}" x="{x:.1f}" y="{GY+ri*(CS+GAP):.1f}" width="{cw:.1f}" height="{CS}" rx="2" fill="{fills[level(n)]}" style="animation-delay:{delay:.2f}s"><title>{date}: {n}</title></rect>')

# stats
sy = GY + 7 * (CS + GAP) + 26
stats = [('TOTAL', f'{total}'), ('CURRENT STREAK', f'{streak} d'), ('LONGEST STREAK', f'{longest} d'), ('BEST DAY', f'{best[1]}')]
for i, (k, v) in enumerate(stats):
    x = GX + i * 235
    s.append(f'<text x="{x}" y="{sy}" font-size="9.5" fill="#78716c" letter-spacing="1.5">{k}</text><text x="{x}" y="{sy+22}" font-size="20" font-weight="700" fill="{A2}">{v}</text>')
s.append(f'<text x="{W-GX}" y="{sy+22}" font-size="12" fill="{A}" text-anchor="end">&gt; latest<tspan class="cur">_</tspan></text>')
s.append('</svg>')
open(out, 'w').write('\n'.join(s)); print('wrote', out, total)
