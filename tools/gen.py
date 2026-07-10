# -*- coding: utf-8 -*-
import json, html, re, os, collections

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'ac_data.json')          # tools/ac_data.json
OUTDIR = os.path.dirname(HERE)                       # repo 根目錄，輸出 index.html
os.makedirs(OUTDIR, exist_ok=True)
d = json.load(open(DATA, encoding='utf-8'))

MAKETIME = '2026/07/10 09:12'

def esc(s): return html.escape(str(s)) if s is not None else ''

def to_num(v):
    if v in (None, ''): return None
    if isinstance(v,(int,float)): return float(v)
    m = re.search(r'-?\d+(?:\.\d+)?', str(v).replace(',',''))
    return float(m.group()) if m else None

def money(v):
    n = to_num(v)
    if n is None: return '—'
    return 'NT$ {:,}'.format(int(round(n)))

# ---------- 功能標籤 ----------
def feats(x):
    t = x['特色'] or ''; cat = x['細類'] or ''
    tags = []
    if '冷暖' in cat: tags.append('冷暖兩用')
    elif '冷專' in cat: tags.append('僅冷氣')
    if any(k in t for k in ['WiFi','Wi-Fi','wifi','智慧','APP','App','手機','語音','ＡＩ','AI']): tags.append('WiFi智慧')
    if any(k in t for k in ['自清','自動清','凍結洗淨','自體淨','霜效潔淨','自動清潔','洗淨']): tags.append('自動清潔')
    if any(k in t for k in ['清淨','PM2.5','PM2','濾網','nanoe','Nanoe','等離子','光觸媒','過敏原']): tags.append('空氣清淨')
    if any(k in t for k in ['抗菌','銀離子','防霉','抑菌']): tags.append('抗菌防霉')
    if '除濕' in t: tags.append('單獨除濕')
    if any(k in t for k in ['防鏽','防腐','耐腐','耐蝕','防潮','耐候']): tags.append('防鏽耐蝕')
    if 'R32' in t or 'R-32' in t or 'R 32' in t: tags.append('R32環保冷媒')
    if '舒眠' in t: tags.append('舒眠')
    if any(k in t for k in ['靜音','低噪','安靜']): tags.append('靜音')
    # 去重保序
    seen=set(); out=[]
    for tg in tags:
        if tg not in seen: seen.add(tg); out.append(tg)
    return out

def tags_html(x):
    ts = feats(x)
    if not ts: return '<span class="notag">—</span>'
    return ''.join('<span class="tag">%s</span>' % esc(t) for t in ts)

def type_short(cat):
    cat = cat or ''
    heat = '冷暖' if '冷暖' in cat else ('冷專' if '冷專' in cat else '')
    if '窗型' in cat: base='窗型'
    elif '一對多' in cat: base='一對多'
    elif '吊隱' in cat: base='吊隱'
    elif '一對一' in cat: base='分離式'
    elif '移動' in cat: base='移動式'
    else: base=cat
    return base + ('・'+heat if heat else '')

# ---------- 向量示意圖 (黑白高對比線稿) ----------
def svg_split():
    return '''<svg viewBox="0 0 240 110" class="ac-svg" role="img" aria-label="壁掛分離式冷氣示意圖">
<rect x="8" y="18" width="120" height="34" rx="8" fill="#fff" stroke="#000" stroke-width="3"/>
<line x1="18" y1="44" x2="118" y2="44" stroke="#000" stroke-width="2"/>
<line x1="18" y1="48" x2="118" y2="48" stroke="#000" stroke-width="2"/>
<rect x="150" y="30" width="82" height="66" rx="6" fill="#fff" stroke="#000" stroke-width="3"/>
<circle cx="191" cy="63" r="24" fill="#fff" stroke="#000" stroke-width="3"/>
<path d="M191 63 L191 42 M191 63 L209 74 M191 63 L173 74" stroke="#000" stroke-width="3" fill="none"/>
<line x1="128" y1="40" x2="150" y2="55" stroke="#000" stroke-width="2.5"/>
<text x="60" y="70" font-size="12" text-anchor="middle" fill="#000">室內機</text>
<text x="191" y="107" font-size="12" text-anchor="middle" fill="#000">室外機</text>
</svg>'''

def svg_window():
    return '''<svg viewBox="0 0 240 110" class="ac-svg" role="img" aria-label="窗型冷氣示意圖">
<rect x="60" y="12" width="120" height="86" rx="4" fill="#fff" stroke="#000" stroke-width="3"/>
<line x1="120" y1="12" x2="120" y2="55" stroke="#000" stroke-width="2"/>
<rect x="72" y="55" width="96" height="34" rx="3" fill="#fff" stroke="#000" stroke-width="3"/>
<line x1="80" y1="63" x2="160" y2="63" stroke="#000" stroke-width="2"/>
<line x1="80" y1="70" x2="160" y2="70" stroke="#000" stroke-width="2"/>
<line x1="80" y1="77" x2="160" y2="77" stroke="#000" stroke-width="2"/>
<text x="120" y="105" font-size="12" text-anchor="middle" fill="#000">窗型一體機</text>
</svg>'''

def svg_multi():
    return '''<svg viewBox="0 0 240 110" class="ac-svg" role="img" aria-label="一對多冷氣示意圖">
<rect x="6" y="10" width="86" height="24" rx="6" fill="#fff" stroke="#000" stroke-width="3"/>
<line x1="14" y1="27" x2="84" y2="27" stroke="#000" stroke-width="2"/>
<rect x="6" y="72" width="86" height="24" rx="6" fill="#fff" stroke="#000" stroke-width="3"/>
<line x1="14" y1="89" x2="84" y2="89" stroke="#000" stroke-width="2"/>
<rect x="150" y="34" width="82" height="52" rx="6" fill="#fff" stroke="#000" stroke-width="3"/>
<circle cx="191" cy="60" r="20" fill="#fff" stroke="#000" stroke-width="3"/>
<path d="M191 60 L191 43 M191 60 L206 69 M191 60 L176 69" stroke="#000" stroke-width="3" fill="none"/>
<path d="M92 22 L150 50 M92 84 L150 66" stroke="#000" stroke-width="2.5" fill="none"/>
<text x="49" y="52" font-size="11" text-anchor="middle" fill="#000">多台室內機</text>
<text x="191" y="99" font-size="12" text-anchor="middle" fill="#000">1 台室外機</text>
</svg>'''

def brand_svg(dominant):
    if '窗型' in dominant: return svg_window()
    if '一對多' in dominant: return svg_multi()
    return svg_split()

# 各品牌主力機型
bt = collections.defaultdict(collections.Counter)
for x in d: bt[x['品牌']][x['細類']] += 1
brand_dom = {b: c.most_common(1)[0][0] for b,c in bt.items()}

# 品牌顯示順序 (依台數)
brand_order = [b for b,_ in collections.Counter(x['品牌'] for x in d).most_common()]

# ---------- 共用元件 ----------
WARN = ('⚠ 本表僅供參考：商品規格、價格與贈品以中華電信系統實際受理與交貨為準；'
        '促銷價格會波動。圖片為<strong>示意圖</strong>，非實際外觀，僅供辨識機型類別參考。')

def warn_banner():
    return '<div class="warn">%s</div>' % WARN

def legend_box():
    tag_desc = [
        ('冷暖兩用 / 僅冷氣','是否具備暖氣功能'),
        ('R32環保冷媒','使用 R32 新式環保冷媒'),
        ('WiFi智慧','可用手機App／語音／AI 操控'),
        ('自動清潔','自動清洗／防霉潔淨功能'),
        ('空氣清淨','含清淨濾網／PM2.5／奈米離子'),
        ('抗菌防霉','抗菌銀離子／防霉抑菌'),
        ('單獨除濕','可單獨除濕不吹冷'),
        ('防鏽耐蝕','機體強化防鏽耐腐蝕'),
        ('靜音 / 舒眠','低噪音／舒眠模式'),
    ]
    rows = ''.join('<tr><td class="lg-tag"><span class="tag">%s</span></td><td>%s</td></tr>'
                   % (esc(a.split(' / ')[0]) if ' / ' not in a else esc(a), esc(b)) for a,b in tag_desc)
    return '<table class="legend"><caption>功能標籤說明</caption>%s</table>' % rows

# ---------- 比較方式一：同 KW 級距 ----------
BANDS = [
    ('2.0–2.5 kW（約 3–5 坪）', 1.9, 2.59),
    ('2.6–3.5 kW（約 5–7 坪）', 2.6, 3.59),
    ('3.6–4.5 kW（約 7–9 坪）', 3.6, 4.59),
    ('4.6–5.9 kW（約 9–12 坪）', 4.6, 5.99),
    ('6.0–7.1 kW（約 12–15 坪）', 6.0, 7.19),
    ('7.2–9.0 kW（約 15–20 坪）', 7.2, 9.09),
    ('9.1 kW 以上（約 20 坪以上）', 9.1, 9999),
]

def method1_table(items):
    head = ('<thead><tr><th>品牌</th><th>產品名稱／型號</th><th>機型</th><th class="num">冷氣<br>kW</th>'
            '<th>能效</th><th class="num">CSPF</th><th class="feat">主要功能</th>'
            '<th class="num">市價</th><th class="num price">寬頻優惠價</th><th>產地／保固</th></tr></thead>')
    body = ''
    for x in items:
        prod = '<span class="pname">%s</span><br><span class="model">型號：%s</span>' % (
            esc(x['產品名稱']), esc(x['型號']))
        warranty = '%s／壓縮機%s' % (esc(x['全機保固'] or '—'), esc(x['壓縮機保固'] or '—'))
        body += ('<tr><td class="brand">%s</td><td class="prod">%s</td><td>%s</td>'
                 '<td class="num">%s</td><td class="eff">%s</td><td class="num">%s</td>'
                 '<td class="feat">%s</td><td class="num">%s</td><td class="num price">%s</td>'
                 '<td class="small">%s<br>%s</td></tr>') % (
            esc(x['品牌']), prod, esc(type_short(x['細類'])),
            esc(x['冷氣kW'] or '—'), esc(x['能效等級'] or '—'), esc(x['CSPF'] or '—'),
            tags_html(x), money(x['市價']), money(x['優惠價']),
            esc(x['產地'] or '—'), warranty)
    return '<table class="cmp">%s<tbody>%s</tbody></table>' % (head, body)

def build_method1():
    out = ['<h2 class="mtitle">比較方式一　同噸數（KW／坪數）跨品牌比較</h2>',
           '<p class="mdesc">依冷氣能力 KW（對應適用坪數）分級，將各品牌同級距機型並列，方便比較<strong>功能與價格</strong>。同一級距內依品牌、價格排序。</p>']
    for title, lo, hi in BANDS:
        items = [x for x in d if (to_num(x['冷氣kW']) is not None and lo <= to_num(x['冷氣kW']) <= hi)]
        if not items: continue
        items.sort(key=lambda x: (brand_order.index(x['品牌']) if x['品牌'] in brand_order else 99,
                                  to_num(x['冷氣kW']) or 0, to_num(x['優惠價']) or 0))
        out.append('<section class="page">')
        out.append(warn_banner())
        out.append('<h3 class="band">%s　<span class="cnt">共 %d 款</span></h3>' % (esc(title), len(items)))
        out.append(method1_table(items))
        out.append(page_footer('比較方式一・同噸數比較'))
        out.append('</section>')
    return '\n'.join(out)

# ---------- 比較方式二：同一廠商 2–10KW ----------
def method2_table(items):
    head = ('<thead><tr><th>型號</th><th>機型</th><th class="num">冷氣<br>kW</th><th class="num">暖氣<br>kW</th>'
            '<th>能效</th><th class="num">CSPF</th><th class="feat">主要功能</th>'
            '<th class="num">市價</th><th class="num price">寬頻優惠價</th></tr></thead>')
    body = ''
    for x in items:
        model = '<span class="pname">%s</span><br><span class="model">%s</span>' % (
            esc(x['型號']), esc(x['產品名稱']))
        body += ('<tr><td class="prod">%s</td><td>%s</td><td class="num">%s</td><td class="num">%s</td>'
                 '<td class="eff">%s</td><td class="num">%s</td><td class="feat">%s</td>'
                 '<td class="num">%s</td><td class="num price">%s</td></tr>') % (
            model, esc(type_short(x['細類'])), esc(x['冷氣kW'] or '—'), esc(x['暖氣kW'] or '—'),
            esc(x['能效等級'] or '—'), esc(x['CSPF'] or '—'), tags_html(x),
            money(x['市價']), money(x['優惠價']))
    return '<table class="cmp">%s<tbody>%s</tbody></table>' % (head, body)

def build_method2():
    out = ['<h2 class="mtitle">比較方式二　同一廠商 2–10 KW 全系列比較</h2>',
           '<p class="mdesc">以品牌為單位，列出該廠商 2–10 KW 各機型的<strong>功能與價格</strong>，依冷氣能力由小到大排序，方便選定品牌後挑坪數。</p>']
    for b in brand_order:
        items = [x for x in d if x['品牌']==b]
        items.sort(key=lambda x: (to_num(x['冷氣kW']) or 0, to_num(x['優惠價']) or 0))
        out.append('<section class="page">')
        out.append(warn_banner())
        out.append('<div class="brand-head">')
        out.append('<div class="brand-photo">%s<div class="photo-cap">%s 代表機型示意圖<br><span class="ref">（示意圖，僅供參考）</span></div></div>' % (
            brand_svg(brand_dom.get(b,'')), esc(b)))
        out.append('<div class="brand-title"><h3>%s</h3><p class="btype">主力機型：%s　｜　本表 %d 款</p></div>' % (
            esc(b), esc(type_short(brand_dom.get(b,''))), len(items)))
        out.append('</div>')
        out.append(method2_table(items))
        out.append(page_footer('比較方式二・'+b))
        out.append('</section>')
    return '\n'.join(out)

def page_footer(sec):
    return ('<div class="pfoot"><span class="fwarn">⚠ 以中華電信系統實際受理與交貨為準；'
            '圖片為示意圖僅供參考</span>　｜　115 年度智慧節能家電・空調專區　｜　%s　｜　製表 %s</div>'
            ) % (esc(sec), MAKETIME)

# ---------- 封面／說明頁 ----------
def cover():
    total = len(d)
    brands = len(brand_order)
    blist = '、'.join(b for b in brand_order)
    return '''<section class="page cover">
%s
<h1>115 年度<br>智慧節能家電 · 空調專區<br>冷氣機型比較表</h1>
<p class="sub">中華電信寬頻優惠專案　｜　僅列「上架中」機型　共 %d 款　%d 大品牌</p>
<p class="brands">%s</p>
<div class="cover-svgs">
  <div>%s<div class="photo-cap">壁掛分離式</div></div>
  <div>%s<div class="photo-cap">窗型一體機</div></div>
  <div>%s<div class="photo-cap">一對多</div></div>
</div>
<div class="cover-two">
  <div class="ctile"><h4>比較方式一</h4><p>同噸數（KW／坪數）跨品牌比較<br>—— 決定坪數，橫向比品牌功能與價格</p></div>
  <div class="ctile"><h4>比較方式二</h4><p>同一廠商 2–10KW 全系列比較<br>—— 選定品牌，縱向挑坪數</p></div>
</div>
%s
<p class="madeat">製表時間：%s　｜　資料來源：（公告版）115年度智慧節能家電資料總表</p>
%s
</section>''' % (warn_banner(), total, brands, esc(blist),
                 svg_split(), svg_window(), svg_multi(),
                 legend_box(), MAKETIME, page_footer('封面・說明'))

# ---------- CSS ----------
CSS = '''
:root{ --line:#000; --hdr:#111; --zebra:#eef0f2; --band:#000; }
*{ box-sizing:border-box; }
html,body{ margin:0; padding:0; background:#f4f4f4; color:#000;
  font-family:"Microsoft JhengHei","Noto Sans TC","PingFang TC","Heiti TC",sans-serif;
  font-size:15px; line-height:1.5; }
.page{ background:#fff; width:410mm; min-height:287mm; margin:8mm auto; padding:12mm 12mm 18mm;
  position:relative; box-shadow:0 1px 6px rgba(0,0,0,.25); }
.warn{ border:3px solid #000; background:#fff; padding:8px 12px; font-size:15px; font-weight:700;
  line-height:1.45; margin-bottom:10px; }
.warn strong{ text-decoration:underline; }
.mtitle{ font-size:30px; text-align:center; margin:26px auto 4px; letter-spacing:1px; }
.mdesc{ text-align:center; font-size:17px; margin:0 auto 8px; }
h3.band{ font-size:24px; background:#000; color:#fff; padding:7px 14px; margin:6px 0 0; border-radius:2px; }
h3.band .cnt{ font-size:17px; font-weight:400; }
table.cmp{ width:100%; border-collapse:collapse; margin:0 0 6px; font-size:15px; }
table.cmp th,table.cmp td{ border:1.4px solid #000; padding:6px 7px; vertical-align:middle; }
table.cmp th{ background:#111; color:#fff; font-size:15.5px; font-weight:700; text-align:center; }
table.cmp tbody{}
table.cmp tbody tr:nth-child(even) td{ background:var(--zebra); }
td.num,th.num{ text-align:center; white-space:nowrap; }
td.brand{ font-weight:800; font-size:16px; white-space:nowrap; }
.pname{ font-weight:700; font-size:15.5px; }
.model{ font-size:13px; color:#000; }
td.prod{ min-width:230px; }
.price{ font-weight:800; font-size:17px; }
th.price{ font-size:15.5px; }
td.eff{ font-weight:700; text-align:center; }
.feat{ min-width:210px; }
.tag{ display:inline-block; border:1.6px solid #000; border-radius:4px; padding:1px 6px; margin:2px 3px 2px 0;
  font-size:13px; font-weight:700; white-space:nowrap; background:#fff; }
.notag{ color:#000; }
.small{ font-size:12.5px; }
.pfoot{ position:absolute; left:12mm; right:12mm; bottom:8mm; border-top:1.5px solid #000;
  padding-top:4px; font-size:12px; text-align:center; }
.pfoot .fwarn{ font-weight:800; }
/* 封面 */
.cover{ text-align:center; }
.cover h1{ font-size:52px; line-height:1.25; margin:40px 0 10px; letter-spacing:2px; }
.cover .sub{ font-size:22px; font-weight:700; margin:6px 0; }
.cover .brands{ font-size:18px; margin:4px 0 18px; }
.cover-svgs{ display:flex; justify-content:center; gap:40px; margin:14px 0 8px; }
.cover-svgs .ac-svg{ width:220px; height:100px; }
.cover-two{ display:flex; justify-content:center; gap:30px; margin:18px auto; max-width:900px; }
.ctile{ border:2.5px solid #000; padding:12px 18px; width:44%; }
.ctile h4{ margin:0 0 6px; font-size:22px; }
.ctile p{ margin:0; font-size:16px; }
.madeat{ font-size:14px; margin-top:16px; }
.ac-svg{ width:200px; height:92px; }
.photo-cap{ font-size:14px; font-weight:700; margin-top:2px; }
.ref{ font-weight:400; font-size:12px; }
/* legend */
table.legend{ border-collapse:collapse; margin:14px auto; font-size:15px; width:70%; }
table.legend caption{ font-size:20px; font-weight:800; padding:6px; }
table.legend td{ border:1.4px solid #000; padding:6px 10px; }
td.lg-tag{ width:170px; text-align:center; }
/* 品牌頁表頭 */
.brand-head{ display:flex; align-items:center; gap:26px; border:2.5px solid #000; padding:10px 16px; margin:6px 0 8px; }
.brand-photo{ text-align:center; }
.brand-photo .ac-svg{ width:230px; height:104px; }
.brand-title h3{ font-size:34px; margin:0; }
.btype{ font-size:18px; margin:6px 0 0; font-weight:700; }
.mtitle+.mdesc{ margin-bottom:16px; }
/* 列印 */
@page{ size:A3 landscape; margin:8mm; }
@media print{
  html,body{ background:#fff; font-size:12.5px; }
  .page{ width:auto; min-height:auto; margin:0; padding:0 0 14mm; box-shadow:none;
    page-break-after:always; break-after:page; }
  .page:last-child{ page-break-after:auto; }
  table.cmp{ font-size:12px; }
  table.cmp th,table.cmp td{ padding:4px 5px; }
  table.cmp tr{ page-break-inside:avoid; }
  .tag{ font-size:11px; }
  .price{ font-size:14px; }
  .warn{ font-size:12.5px; }
  .pfoot{ position:fixed; left:0; right:0; bottom:0; background:#fff; padding:3px 4mm 2px;
    font-size:11px; }
  .cover h1{ font-size:44px; }
  thead{ display:table-header-group; }
}
'''

# ---------- 組裝 ----------
body = cover() + build_method1() + build_method2()
html_doc = '''<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>115年度冷氣機型比較表・空調專區</title>
<style>%s</style>
</head>
<body>
%s
</body>
</html>''' % (CSS, body)

open(os.path.join(OUTDIR,'index.html'),'w',encoding='utf-8').write(html_doc)
print('OK 產生', os.path.join(OUTDIR,'index.html'), '大小', len(html_doc))
print('方式一級距數 / 方式二品牌數:', sum(1 for t,l,h in BANDS if any(to_num(x['冷氣kW']) is not None and l<=to_num(x['冷氣kW'])<=h for x in d)), '/', len(brand_order))
