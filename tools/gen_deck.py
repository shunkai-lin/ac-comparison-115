# -*- coding: utf-8 -*-
import json, re, os, html, collections
HERE=os.path.dirname(os.path.abspath(__file__))
DATA=os.path.join(HERE,'ac_data.json')
OUT =os.path.join(os.path.dirname(HERE),'deck.html')
d=json.load(open(DATA,encoding='utf-8'))
MAKETIME='2026/07/10 09:12'
def esc(s): return html.escape(str(s)) if s is not None else ''
def num(v):
    if v in (None,''): return None
    if isinstance(v,(int,float)): return float(v)
    m=re.search(r'-?\d+(?:\.\d+)?',str(v).replace(',',''));return float(m.group()) if m else None
def money(v):
    n=num(v);return '—' if n is None else 'NT$ {:,}'.format(int(round(n)))
def feats(x):
    t=x['特色'] or '';out=[]
    if any(k in t for k in ['WiFi','Wi-Fi','wifi','智慧','APP','App','手機','語音','AI']): out.append('WiFi智慧')
    if any(k in t for k in ['自清','自動清','凍結洗淨','自體淨','霜效潔淨','洗淨']): out.append('自動清潔')
    if any(k in t for k in ['清淨','PM2.5','PM2','濾網','nanoe','Nanoe','等離子','光觸媒','過敏原']): out.append('空氣清淨')
    if any(k in t for k in ['抗菌','銀離子','防霉','抑菌']): out.append('抗菌防霉')
    if '除濕' in t: out.append('除濕')
    if any(k in t for k in ['防鏽','防腐','耐腐','耐蝕','防潮']): out.append('防鏽')
    if 'R32' in t or 'R-32' in t: out.append('R32冷媒')
    seen=set();r=[]
    for g in out:
        if g not in seen: seen.add(g);r.append(g)
    return r
def feat_str(x,n=3):
    fs=feats(x)[:n];return '、'.join(fs) if fs else '—'
def type_short(cat):
    cat=cat or '';heat='冷暖' if '冷暖' in cat else ('冷專' if '冷專' in cat else '')
    if '窗型' in cat:b='窗型'
    elif '一對多' in cat:b='一對多'
    elif '吊隱' in cat:b='吊隱'
    elif '一對一' in cat:b='分離式'
    elif '移動' in cat:b='移動式'
    else:b=cat
    return b+('・'+heat if heat else '')
BRAND_SHORT={'SAMPO 聲寶':'聲寶','HERAN 禾聯':'禾聯','TECO 東元':'東元','Tatung 大同':'大同',
             'Panasonic':'Panasonic','三菱電機':'三菱電機','HITACHI 日立':'日立','DAIKIN 大金':'大金','三菱重工':'三菱重工'}
def bshort(b): return BRAND_SHORT.get(b,b)
bt=collections.defaultdict(collections.Counter)
for x in d: bt[x['品牌']][x['細類']]+=1
brand_order=[b for b,_ in collections.Counter(x['品牌'] for x in d).most_common()]
def chunk(l,n): return [l[i:i+n] for i in range(0,len(l),n)]

WARNF='⚠ 僅供參考，商品規格／價格／贈品以中華電信系統實際受理與交貨為準，促銷價格會波動；圖片為示意，非實際外觀。　｜　製表 '+MAKETIME
def foot(): return '<div class="sfoot">%s</div>'%WARNF

def cover():
    stats=[('313','款上架機型'),('9','大品牌'),('2–10','KW 全涵蓋'),('2','種比較方式')]
    cards=''.join('<div class="stat"><div class="sn">%s</div><div class="sl">%s</div></div>'%(a,b) for a,b in stats)
    return '''<section class="slide cover">
<div class="c-tag">中華電信寬頻優惠專案</div>
<h1>115 年度智慧節能家電<br>空調專區 · 冷氣機型比較表</h1>
<div class="stats">%s</div>
<div class="c-warn">⚠ 本表僅供參考：商品規格、價格與贈品以中華電信系統實際受理與交貨為準；促銷價格會波動。圖片為示意圖，非實際外觀，僅供辨識機型類別參考。</div>
<div class="c-src">收錄範圍：空調專區「上架中」機型　｜　製表時間 %s　｜　資料來源：（公告版）115年度智慧節能家電資料總表</div>
</section>'''%(cards,MAKETIME)

def legend():
    tags=[('冷暖 / 冷專','是否具暖氣功能'),('R32冷媒','R32 新式環保冷媒'),('WiFi智慧','手機App／語音操控'),
          ('自動清潔','自動清洗／防霉'),('空氣清淨','清淨濾網／PM2.5'),('抗菌防霉','抗菌銀離子／防霉'),
          ('除濕','可單獨除濕'),('防鏽','機體防鏽耐蝕')]
    rows=''.join('<tr><td class="lt"><span class="tag">%s</span></td><td>%s</td></tr>'%(esc(a),esc(b)) for a,b in tags)
    return '''<section class="slide legend">
<h2 class="lh">如何使用本比較表</h2>
<div class="lgrid">
 <div class="lcol">
   <div class="lsub t">兩種比較方式</div>
   <div class="mbox m1">① 同噸數（KW／坪數）跨品牌比較<br><span class="mi">先決定坪數，橫向比各品牌功能與價格。</span></div>
   <div class="mbox m2">② 同一廠商 2–10 KW 全系列<br><span class="mi">選定品牌，縱向依坪數挑機型。</span></div>
   <ul class="lnote"><li>深色表頭、粗體價格，黑白列印也清楚。</li><li>每頁皆有警語，以實際交貨為準。</li><li>互動篩選版見版本一（index.html）。</li></ul>
 </div>
 <div class="lcol">
   <div class="lsub n">功能標籤說明</div>
   <table class="ltab"><tr><th>標籤</th><th>說明</th></tr>%s</table>
 </div>
</div>
%s</section>'''%(rows,foot())

def divider(no,title,sub,cls):
    return '''<section class="slide divider %s">
<div class="dno">%s</div><div class="dwrap"><div class="dt">%s</div><div class="ds">%s</div></div>
</section>'''%(cls,no,esc(title),esc(sub))

def m1_slides():
    out=[divider('m1','比較方式一　同噸數跨品牌比較','依冷氣能力 KW（對應適用坪數）分級，將各品牌同級距機型並列，橫向比較功能與價格。','dv1')]
    BANDS=[('2.0–2.5 kW（約 3–5 坪）',1.9,2.59),('2.6–3.5 kW（約 5–7 坪）',2.6,3.59),
           ('3.6–4.5 kW（約 7–9 坪）',3.6,4.59),('4.6–5.9 kW（約 9–12 坪）',4.6,5.99),
           ('6.0–7.1 kW（約 12–15 坪）',6.0,7.19),('7.2–9.0 kW（約 15–20 坪）',7.2,9.09),
           ('9.1 kW 以上（約 20 坪以上）',9.1,9999)]
    for title,lo,hi in BANDS:
        items=[x for x in d if num(x['冷氣kW']) is not None and lo<=num(x['冷氣kW'])<=hi]
        items.sort(key=lambda x:(brand_order.index(x['品牌']) if x['品牌'] in brand_order else 99,num(x['冷氣kW']) or 0,num(x['優惠價']) or 0))
        parts=chunk(items,12)
        for pi,part in enumerate(parts):
            sfx='' if len(parts)==1 else '　(%d/%d)'%(pi+1,len(parts))
            head='<tr><th>品牌</th><th>型號</th><th>機型</th><th>冷氣<br>kW</th><th>能效</th><th>CSPF</th><th class="fl">主要功能</th><th>市價</th><th class="pr">寬頻優惠價</th></tr>'
            body=''
            for x in part:
                eff=x['能效等級'] or '—'
                body+=('<tr><td class="b">%s</td><td class="ml">%s</td><td>%s</td><td>%s</td>'
                       '<td class="eff">%s</td><td>%s</td><td class="fl">%s</td><td>%s</td><td class="pr">%s</td></tr>')%(
                    esc(bshort(x['品牌'])),esc(x['型號']),esc(type_short(x['細類'])),
                    (('%g'%num(x['冷氣kW'])) if num(x['冷氣kW']) is not None else '—'),
                    esc(eff),esc(x['CSPF'] or '—'),esc(feat_str(x)),money(x['市價']),money(x['優惠價']))
            out.append('<section class="slide data d1"><div class="dhead"><h3 class="ht t">%s%s</h3><span class="tagr">比較方式一・同噸數</span></div><table class="ct m1">%s%s</table>%s</section>'%(esc(title),sfx,head,body,foot()))
    return ''.join(out)

def m2_slides():
    out=[divider('m2','比較方式二　同一廠商全系列','以品牌為單位，列出該廠商 2–10 KW 各機型，依冷氣能力由小到大，選定品牌後挑坪數。','dv2')]
    for b in brand_order:
        items=[x for x in d if x['品牌']==b]
        items.sort(key=lambda x:(num(x['冷氣kW']) or 0,num(x['優惠價']) or 0))
        parts=chunk(items,12)
        for pi,part in enumerate(parts):
            sfx='' if len(parts)==1 else '　(%d/%d)'%(pi+1,len(parts))
            head='<tr><th>型號</th><th>機型</th><th>冷氣<br>kW</th><th>暖氣<br>kW</th><th>能效</th><th>CSPF</th><th class="fl">主要功能</th><th>市價</th><th class="pr">寬頻優惠價</th></tr>'
            body=''
            for x in part:
                body+=('<tr><td class="ml">%s</td><td>%s</td><td>%s</td><td>%s</td>'
                       '<td class="eff">%s</td><td>%s</td><td class="fl">%s</td><td>%s</td><td class="pr">%s</td></tr>')%(
                    esc(x['型號']),esc(type_short(x['細類'])),
                    (('%g'%num(x['冷氣kW'])) if num(x['冷氣kW']) is not None else '—'),
                    (('%g'%num(x['暖氣kW'])) if num(x['暖氣kW']) is not None else '—'),
                    esc(x['能效等級'] or '—'),esc(x['CSPF'] or '—'),esc(feat_str(x)),money(x['市價']),money(x['優惠價']))
            out.append('<section class="slide data d2"><div class="dhead"><span class="chip">%s</span><span class="bmeta">主力機型：%s%s</span><span class="tagr">比較方式二・同廠商</span></div><table class="ct m2">%s%s</table>%s</section>'%(esc(b),esc(type_short(bt[b].most_common(1)[0][0])),sfx,head,body,foot()))
    return ''.join(out)

NAV='<div class="vernav"><a href="index.html">📊 版本一：互動篩選表</a><a class="cur">📑 版本二：簡報式</a><span class="vnhint">（此列僅螢幕顯示，列印時隱藏）</span></div>'

CSS='''
*{box-sizing:border-box;margin:0;padding:0;-webkit-print-color-adjust:exact;print-color-adjust:exact;}
:root{--teal:#0E5C63;--plum:#6D2E46;--navy:#0B4F6C;--gold:#FCEFD6;--green:#E4F1E4;--ink:#1A1A1A;}
body{background:#e9edf0;font-family:"Microsoft JhengHei","Noto Sans TC","PingFang TC",sans-serif;color:var(--ink);}
.vernav{position:sticky;top:0;z-index:60;background:#fff;border-bottom:2px solid var(--teal);padding:8px 14px;display:flex;gap:10px;align-items:center;}
.vernav a{font-size:16px;font-weight:800;text-decoration:none;color:var(--teal);border:2px solid var(--teal);border-radius:6px;padding:5px 12px;}
.vernav a.cur{background:var(--teal);color:#fff;}
.vnhint{color:#888;font-size:13px;}
.slide{position:relative;width:1280px;height:720px;margin:18px auto;background:#fff;box-shadow:0 2px 10px rgba(0,0,0,.28);overflow:hidden;padding:30px 34px 44px;}
.sfoot{position:absolute;left:0;right:0;bottom:0;background:#fff;border-top:1.5px solid #999;color:#555;font-size:13px;text-align:center;padding:6px 10px;}
/* 封面 */
.cover{background:var(--navy);color:#fff;padding:64px 70px;}
.c-tag{font-size:24px;font-weight:800;color:#cfe6ee;margin-bottom:14px;}
.cover h1{font-size:58px;line-height:1.22;font-weight:900;margin-bottom:36px;}
.stats{display:flex;gap:20px;margin:10px 0 30px;}
.stat{flex:1;background:#12637f;border:1px solid #3E8CA8;border-radius:10px;padding:22px 10px;text-align:center;}
.stat .sn{font-size:46px;font-weight:900;}
.stat .sl{font-size:17px;font-weight:700;color:#cfe6ee;margin-top:4px;}
.c-warn{background:#fff;color:#000;font-weight:800;font-size:18px;line-height:1.4;border-radius:8px;padding:16px 20px;margin-bottom:16px;}
.c-src{font-size:15px;color:#b8d4de;}
/* 說明 */
.legend .lh{font-size:40px;font-weight:900;color:var(--navy);margin-bottom:14px;}
.lgrid{display:flex;gap:34px;}
.lcol{flex:1;}
.lsub{font-size:26px;font-weight:900;margin-bottom:12px;}
.lsub.t{color:var(--teal);}.lsub.n{color:var(--navy);}
.mbox{border-radius:8px;padding:16px 18px;font-size:20px;font-weight:800;margin-bottom:14px;line-height:1.35;}
.mbox .mi{font-size:16px;font-weight:500;}
.mbox.m1{background:#e9f3f4;border:2px solid var(--teal);}
.mbox.m2{background:#f3e9ee;border:2px solid var(--plum);}
.lnote{margin:16px 0 0 20px;font-size:17px;line-height:1.7;}
.ltab{width:100%;border-collapse:collapse;font-size:17px;}
.ltab th{background:var(--navy);color:#fff;padding:9px;font-size:18px;}
.ltab td{border:1.3px solid #666;padding:8px 10px;}
.ltab td.lt{width:180px;text-align:center;}
.ltab tr:nth-child(even) td{background:#eef4f5;}
.tag{display:inline-block;border:1.6px solid #000;border-radius:5px;padding:2px 8px;font-size:15px;font-weight:800;background:#fff;}
/* 分隔 */
.divider{color:#fff;display:flex;align-items:center;gap:40px;padding:0 80px;}
.divider.dv1{background:var(--teal);}.divider.dv2{background:var(--plum);}
.dno{font-size:170px;font-weight:900;line-height:1;opacity:.9;}
.dt{font-size:52px;font-weight:900;margin-bottom:18px;}
.ds{font-size:23px;line-height:1.5;max-width:640px;color:#eaf1f3;}
/* 資料頁 */
.dhead{display:flex;align-items:center;gap:16px;margin-bottom:12px;}
.ht{font-size:30px;font-weight:900;}
.ht.t{color:var(--teal);}
.chip{background:var(--plum);color:#fff;font-size:26px;font-weight:900;border-radius:22px;padding:6px 26px;}
.bmeta{font-size:19px;font-weight:800;color:#333;}
.tagr{margin-left:auto;font-size:15px;font-weight:800;color:#777;}
.ct{width:100%;border-collapse:collapse;font-size:17px;table-layout:fixed;}
.ct th,.ct td{border:1.3px solid #555;padding:7px 8px;text-align:center;vertical-align:middle;line-height:1.2;}
.ct th{color:#fff;font-size:17.5px;font-weight:800;}
.ct.m1 th{background:var(--teal);}
.ct.m2 th{background:var(--plum);}
.ct.m1 tbody tr:nth-child(even) td,.ct.m1 tr:nth-child(even) td{background:#eef4f5;}
.ct.m2 tr:nth-child(even) td{background:#f7eff2;}
.ct td.ml{text-align:left;font-weight:700;font-size:16px;word-break:break-all;}
.ct td.fl{text-align:left;font-size:16px;}
.ct td.b{font-weight:800;}
.ct td.eff{background:var(--green);font-weight:800;}
.ct td.pr,.ct th.pr{}
.ct td.pr{background:var(--gold);font-weight:900;font-size:18px;}
/* 欄寬 */
.ct.m1 col{}
.ct.m1 th:nth-child(1),.ct.m1 td:nth-child(1){width:8%;}
.ct.m1 th:nth-child(2),.ct.m1 td:nth-child(2){width:17%;}
.ct.m1 th:nth-child(3),.ct.m1 td:nth-child(3){width:11%;}
.ct.m1 th:nth-child(4),.ct.m1 td:nth-child(4){width:6%;}
.ct.m1 th:nth-child(5),.ct.m1 td:nth-child(5){width:8%;}
.ct.m1 th:nth-child(6),.ct.m1 td:nth-child(6){width:6%;}
.ct.m1 th:nth-child(7),.ct.m1 td:nth-child(7){width:22%;}
.ct.m1 th:nth-child(8),.ct.m1 td:nth-child(8){width:10%;}
.ct.m1 th:nth-child(9),.ct.m1 td:nth-child(9){width:12%;}
.ct.m2 th:nth-child(1),.ct.m2 td:nth-child(1){width:20%;}
.ct.m2 th:nth-child(2),.ct.m2 td:nth-child(2){width:11%;}
.ct.m2 th:nth-child(3),.ct.m2 td:nth-child(3){width:6%;}
.ct.m2 th:nth-child(4),.ct.m2 td:nth-child(4){width:6%;}
.ct.m2 th:nth-child(5),.ct.m2 td:nth-child(5){width:8%;}
.ct.m2 th:nth-child(6),.ct.m2 td:nth-child(6){width:6%;}
.ct.m2 th:nth-child(7),.ct.m2 td:nth-child(7){width:23%;}
.ct.m2 th:nth-child(8),.ct.m2 td:nth-child(8){width:10%;}
.ct.m2 th:nth-child(9),.ct.m2 td:nth-child(9){width:12%;}
/* 列印：A4 橫向，一張投影片一頁 */
@page{size:A4 landscape;margin:0;}
@media print{
  body{background:#fff;}
  .vernav{display:none!important;}
  .slide{width:29.7cm;height:20.85cm;margin:0;box-shadow:none;page-break-after:always;break-after:page;}
  .slide:last-child{page-break-after:auto;}
}
'''
html_doc='<!DOCTYPE html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>115年度冷氣機型比較・簡報式（版本二）</title><style>%s</style></head><body>%s%s%s%s%s</body></html>'%(
    CSS,NAV,cover(),legend(),m1_slides(),m2_slides())
open(OUT,'w',encoding='utf-8').write(html_doc)
print('OK deck',OUT,'size',len(html_doc))
