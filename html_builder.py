"""Ensamblador HTML del reporte CAM — sin dependencias CDN externas."""
import json
from chart_gen import mes_label, mes_key

CSS = """
body{font-family:'Segoe UI',Tahoma,sans-serif;background:#f0f4ff;margin:0;padding:16px}
h1{margin:0;font-size:22px;color:#1a1a2e}
h2{margin:0 0 10px;font-size:15px;color:#1a1a2e}
h3{margin:0 0 8px;font-size:13px;color:#374151}
.subtitle{font-size:12px;color:#6b7280;margin:2px 0 0}
.header{background:#0053e2;color:#fff;padding:16px 20px;border-radius:12px;margin-bottom:16px;display:flex;align-items:center;gap:12px}
.header h1{color:#fff}
.badge{padding:3px 10px;border-radius:99px;font-size:11px;font-weight:700;display:inline-block}
.badge-es{background:#0053e2;color:#fff}
.badge-fds{background:#ffc220;color:#1a1a1a}
.card{background:#fff;border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,.07);padding:20px;margin-bottom:16px}
.tabs{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:16px}
.tab-btn{padding:8px 16px;border:1px solid #d1d5db;border-radius:8px;cursor:pointer;
  background:#fff;color:#374151;font-size:13px;font-weight:600;transition:all .15s}
.tab-btn.active{background:#0053e2;color:#fff;border-color:#0053e2}
.tab-pane{display:none}
.tab-pane.active{display:block}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.grid3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px}
img.chart{width:100%;height:auto;border-radius:8px;border:1px solid #f0f4ff}
table{width:100%;border-collapse:collapse;font-size:12px}
th{background:#0053e2;color:#fff;padding:8px 10px;text-align:left;white-space:nowrap}
td{padding:6px 10px;border-bottom:1px solid #f0f4ff}
tr:hover td{background:#f0f4ff}
.text-right{text-align:right}
.pill{display:inline-block;padding:2px 8px;border-radius:99px;font-size:11px;font-weight:600}
.delta-pos{color:#2a8703;font-weight:700}
.delta-neg{color:#ea1100;font-weight:700}
.delta-neu{color:#6b7280;font-weight:700}
.export-btn{background:#2a8703;color:#fff;border:none;padding:6px 14px;border-radius:6px;
  font-size:12px;font-weight:600;cursor:pointer;margin-left:8px}
.export-btn:hover{background:#1f6502}
.section-hdr{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}
.filters{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin-bottom:16px}
select{border:1px solid #d1d5db;border-radius:6px;padding:5px 9px;font-size:13px}
label{font-size:12px;font-weight:600;color:#374151}
::-webkit-scrollbar{height:6px;width:6px}
::-webkit-scrollbar-track{background:#f1f5f9}
::-webkit-scrollbar-thumb{background:#0053e2;border-radius:99px}
"""

JS = """
function showTab(id,btn){
  document.querySelectorAll('.tab-pane').forEach(t=>t.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b=>b.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  btn.classList.add('active');
}

function exportCSV(tableId,filename){
  const t=document.getElementById(tableId);
  if(!t) return;
  const rows=[...t.querySelectorAll('tr')];
  const csv=rows.map(r=>[...r.querySelectorAll('th,td')].map(c=>'"'+c.innerText.replace(/"/g,'""')+'"').join(',')).join('\\n');
  const a=document.createElement('a');
  a.href='data:text/csv;charset=utf-8,'+encodeURIComponent(csv);
  a.download=filename; a.click();
}

function showSection(sectionBase,chosen,prefix){
  document.querySelectorAll('.'+sectionBase).forEach(el=>el.style.display='none');
  const target=document.getElementById(prefix+chosen);
  if(target) target.style.display='';
}
"""


def img(b64, alt="chart"):
    return f'<img class="chart" src="data:image/png;base64,{b64}" alt="{alt}"/>'


def build_sw_table(q1):
    """Tabla resumen semanal con boton export."""
    rows_html = []
    for r in q1[:600]:
        seg_c = '#0053e2' if r['segmento'] == 'Entre Semana' else '#ffc220'
        seg_t = '#fff'    if r['segmento'] == 'Entre Semana' else '#1a1a1a'
        seg_s = 'ES'      if r['segmento'] == 'Entre Semana' else 'FdS'
        ml = mes_label(r['ano'], r['mes'])
        rows_html.append(f"""<tr>
          <td>{ml}</td><td>SW{r['semana']}</td><td>{r['pais']}</td>
          <td><b>{r['competidor']}</b></td>
          <td><span class='pill' style='background:{seg_c};color:{seg_t}'>{seg_s}</span></td>
          <td>{r.get('dia_semana','')}</td>
          <td class='text-right'>{r['cnt_precio_normal']:,}</td>
          <td class='text-right'>{r['cnt_precio_oferta']:,}</td>
          <td class='text-right'>{r['cnt_mayoreo']:,}</td>
        </tr>""")
    body = '\n'.join(rows_html)
    return f"""
    <div class='section-hdr'>
      <h3>Tabla Resumen Semanal (primeros 600 registros)</h3>
      <button class='export-btn' onclick="exportCSV('tbl_sw','resumen_semanal.csv')">&#8595; Descargar CSV</button>
    </div>
    <div style='overflow-x:auto;max-height:380px'>
    <table id='tbl_sw'>
      <thead><tr>
        <th>Mes</th><th>Semana</th><th>Pais</th><th>Competidor</th>
        <th>Segmento</th><th>Dia</th>
        <th>Cnt Normal</th><th>Cnt Oferta</th><th>Cnt Mayoreo</th>
      </tr></thead>
      <tbody>{body}</tbody>
    </table></div>"""


def build_caida_table(q1):
    """Tabla: semanas con cero FdS por competidor."""
    from collections import defaultdict
    from chart_gen import mes_key as mk
    # Aggregate by pais+competidor+semana
    sw_data = defaultdict(lambda: {'es_n':0,'fds_n':0,'es_o':0,'fds_o':0,'es_m':0,'fds_m':0})
    semanas_por_comp = defaultdict(set)
    for r in q1:
        key = f"{r['pais']}||{r['competidor']}"
        sw  = f"{r['ano']}-{r['mes']}-{r['semana']}"
        semanas_por_comp[key].add(sw)
        d = sw_data[key + '||' + sw]
        if r['segmento'] == 'Entre Semana':
            d['es_n'] += r['cnt_precio_normal']; d['es_o'] += r['cnt_precio_oferta']; d['es_m'] += r['cnt_mayoreo']
        else:
            d['fds_n'] += r['cnt_precio_normal']; d['fds_o'] += r['cnt_precio_oferta']; d['fds_m'] += r['cnt_mayoreo']

    rows = []
    for pair, sws in sorted(semanas_por_comp.items()):
        pais, comp = pair.split('||')
        z_n = z_o = z_m = 0
        for sw in sws:
            d = sw_data[pair + '||' + sw]
            if d['fds_n'] == 0: z_n += 1
            if d['fds_o'] == 0: z_o += 1
            if d['fds_m'] == 0: z_m += 1
        total = len(sws)
        pct   = round(z_n / total * 100) if total else 0
        cls   = 'delta-neg' if pct > 70 else ('delta-neg' if pct > 30 else 'delta-pos')
        rows.append(f"""<tr>
          <td>{pais}</td><td><b>{comp}</b></td>
          <td class='text-right {"delta-neg" if z_n/total>0.5 else ""}'>{z_n} / {total}</td>
          <td class='text-right'>{z_o} / {total}</td>
          <td class='text-right'>{z_m} / {total}</td>
          <td class='text-right'>{total}</td>
          <td class='text-right {cls}'>{pct}%</td>
        </tr>""")
    body = '\n'.join(rows)
    return f"""
    <h3>Semanas con Cero Chequeos en Fin de Semana por Competidor</h3>
    <div style='overflow-x:auto;max-height:380px'>
    <table>
      <thead><tr>
        <th>Pais</th><th>Competidor</th>
        <th>Sem 0 FdS Normal</th><th>Sem 0 FdS Oferta</th><th>Sem 0 FdS Mayoreo</th>
        <th>Total Semanas</th><th>% sin FdS</th>
      </tr></thead>
      <tbody>{body}</tbody>
    </table></div>"""


def build_mom_table(q3):
    """Tabla deltas mes a mes con export CSV."""
    from collections import defaultdict
    agg = defaultdict(lambda: defaultdict(lambda: {'n':0,'o':0,'m':0}))
    for r in q3:
        k   = f"{r['pais']}||{r['competidor']}"
        seg = r['segmento']
        mk_val = mes_key(r['ano'], r['mes'])
        agg[k][mk_val]['n'] += r['cnt_precio_normal']
        agg[k][mk_val]['o'] += r['cnt_precio_oferta']
        agg[k][mk_val]['m'] += r['cnt_mayoreo']
        agg[k][mk_val]['mes_label'] = mes_label(r['ano'], r['mes'])
        agg[k][mk_val]['seg'] = seg

    # Rebuild per-segment
    seg_agg = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {'n':0,'o':0,'m':0,'label':''})))
    for r in q3:
        k   = f"{r['pais']}||{r['competidor']}"
        seg = r['segmento']
        mk_val = mes_key(r['ano'], r['mes'])
        seg_agg[k][seg][mk_val]['n'] += r['cnt_precio_normal']
        seg_agg[k][seg][mk_val]['o'] += r['cnt_precio_oferta']
        seg_agg[k][seg][mk_val]['m'] += r['cnt_mayoreo']
        seg_agg[k][seg][mk_val]['label'] = mes_label(r['ano'], r['mes'])

    rows = []
    for pair in sorted(seg_agg.keys()):
        pais, comp = pair.split('||')
        for seg in ['Entre Semana','Fin de Semana']:
            if seg not in seg_agg[pair]: continue
            mks   = sorted(seg_agg[pair][seg].keys())
            prev  = None
            seg_c = '#0053e2' if seg == 'Entre Semana' else '#ffc220'
            seg_t = '#fff'    if seg == 'Entre Semana' else '#1a1a1a'
            seg_s = 'ES'      if seg == 'Entre Semana' else 'FdS'
            for mk_val in mks:
                d   = seg_agg[pair][seg][mk_val]
                lbl = d['label']
                def delta(cur, prv):
                    if prv is None or prv == 0: return '&mdash;', 'delta-neu'
                    pct = round((cur - prv) / prv * 100)
                    return (f'+{pct}%' if pct >= 0 else f'{pct}%'), ('delta-pos' if pct > 0 else 'delta-neg' if pct < 0 else 'delta-neu')
                dn, cn = delta(d['n'], prev['n'] if prev else None)
                do_, co = delta(d['o'], prev['o'] if prev else None)
                dm, cm = delta(d['m'], prev['m'] if prev else None)
                rows.append(f"""<tr>
                  <td>{pais}</td><td><b>{comp}</b></td><td>{lbl}</td>
                  <td><span class='pill' style='background:{seg_c};color:{seg_t}'>{seg_s}</span></td>
                  <td class='text-right'>{d['n']:,}</td><td class='text-right {cn}'>{dn}</td>
                  <td class='text-right'>{d['o']:,}</td><td class='text-right {co}'>{do_}</td>
                  <td class='text-right'>{d['m']:,}</td><td class='text-right {cm}'>{dm}</td>
                </tr>""")
                prev = d
    body = '\n'.join(rows)
    return f"""
    <div class='section-hdr'>
      <h3>Tabla Deltas Mes a Mes</h3>
      <button class='export-btn' onclick="exportCSV('tbl_mom','deltas_mom.csv')">&#8595; Descargar CSV</button>
    </div>
    <div style='overflow-x:auto;max-height:400px'>
    <table id='tbl_mom'>
      <thead><tr>
        <th>Pais</th><th>Competidor</th><th>Mes</th><th>Seg</th>
        <th>Cnt Normal</th><th>&#916; Normal</th>
        <th>Cnt Oferta</th><th>&#916; Oferta</th>
        <th>Cnt Mayoreo</th><th>&#916; Mayoreo</th>
      </tr></thead>
      <tbody>{body}</tbody>
    </table></div>"""


def build_cat_table(q5):
    """Tabla ES vs FdS por categoria y mes."""
    from collections import defaultdict
    agg = defaultdict(lambda: {'es_n':0,'fds_n':0,'es_o':0,'fds_o':0,'es_m':0,'fds_m':0,'label':''})
    for r in q5:
        cat = str(r.get('categoria',''))
        if cat in ('SIN CANASTO','','3','1','nan'): continue
        k = f"{r['pais']}||{r['competidor']}||{cat}||{r['ano']}-{r['mes']}"
        mk_val = mes_key(r['ano'], r['mes'])
        agg[k]['label'] = mes_label(r['ano'], r['mes'])
        agg[k]['pais']  = r['pais']
        agg[k]['comp']  = r['competidor']
        agg[k]['cat']   = cat
        agg[k]['mk']    = mk_val
        if r['segmento'] == 'Entre Semana':
            agg[k]['es_n'] += r['cnt_precio_normal']; agg[k]['es_o'] += r['cnt_precio_oferta']; agg[k]['es_m'] += r['cnt_mayoreo']
        else:
            agg[k]['fds_n'] += r['cnt_precio_normal']; agg[k]['fds_o'] += r['cnt_precio_oferta']; agg[k]['fds_m'] += r['cnt_mayoreo']

    sorted_items = sorted(agg.items(), key=lambda x: (x[1]['pais'], x[1]['comp'], x[1]['cat'], x[1]['mk']))
    rows = []
    for _, d in sorted_items[:500]:
        rows.append(f"""<tr>
          <td>{d['pais']}</td><td class='text-xs'>{d['comp']}</td>
          <td><span class='pill' style='background:#dbeafe;color:#1d4ed8'>{d['cat']}</span></td>
          <td>{d['label']}</td>
          <td class='text-right'>{d['es_n']:,}</td><td class='text-right'>{d['fds_n']:,}</td>
          <td class='text-right'>{d['es_o']:,}</td><td class='text-right'>{d['fds_o']:,}</td>
          <td class='text-right'>{d['es_m']:,}</td><td class='text-right'>{d['fds_m']:,}</td>
        </tr>""")
    body = '\n'.join(rows)
    return f"""
    <h3>Tabla: ES vs FdS por Categoria y Mes</h3>
    <div style='overflow-x:auto;max-height:380px'>
    <table>
      <thead><tr>
        <th>Pais</th><th>Competidor</th><th>Categoria</th><th>Mes</th>
        <th>ES Normal</th><th>FdS Normal</th>
        <th>ES Oferta</th><th>FdS Oferta</th>
        <th>ES Mayoreo</th><th>FdS Mayoreo</th>
      </tr></thead>
      <tbody>{body}</tbody>
    </table></div>"""


def build_html(charts, tables):
    """Ensambla el HTML final con todos los charts y tablas."""
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>Analisis de Precios CAM - Entre Semana vs Fines de Semana</title>
  <style>{CSS}</style>
</head>
<body>

<!-- HEADER -->
<div class="header">
  <span style="font-size:28px">&#128202;</span>
  <div>
    <h1>Analisis de Precios CAM</h1>
    <p class="subtitle" style="color:#c7d7ff">Entre Semana (Lun&ndash;Jue) vs Fines de Semana (Vie&ndash;Dom) &middot; Ago 2025 &ndash; Mar 2026</p>
  </div>
  <div style="margin-left:auto;display:flex;gap:8px;align-items:center">
    <span class="badge badge-es">Entre Semana</span>
    <span class="badge badge-fds">Fin de Semana</span>
  </div>
</div>

<!-- TABS -->
<div class="tabs">
  <button class="tab-btn active" onclick="showTab('t1',this)">1&#65039;&#8419; Conteos Semanal</button>
  <button class="tab-btn" onclick="showTab('t2',this)">2&#65039;&#8419; Tendencia Diaria</button>
  <button class="tab-btn" onclick="showTab('t3',this)">3&#65039;&#8419; Mes/Pais/Comp</button>
  <button class="tab-btn" onclick="showTab('t4',this)">4&#65039;&#8419; Caida FdS</button>
  <button class="tab-btn" onclick="showTab('t5',this)">5&#65039;&#8419; Deltas MoM</button>
  <button class="tab-btn" onclick="showTab('t6',this)">6&#65039;&#8419; Tendencias Competidor</button>
  <button class="tab-btn" onclick="showTab('t7',this)">7&#65039;&#8419; Categorias por Pais</button>
</div>

<!-- TAB 1 -->
<div id="t1" class="tab-pane active">
  <div class="card">
    <h2>&#128198; Precio Normal por Semana &mdash; Entre Semana vs Fin de Semana</h2>
    {img(charts['sw_normal'])}
  </div>
  <div class="grid2">
    <div class="card">
      <h2>&#127991;&#65039; Precio Oferta por Semana</h2>
      {img(charts['sw_oferta'])}
    </div>
    <div class="card">
      <h2>&#128218; Precio Mayoreo por Semana</h2>
      {img(charts['sw_mayoreo'])}
    </div>
  </div>
  <div class="card">{tables['sw']}</div>
</div>

<!-- TAB 2 -->
<div id="t2" class="tab-pane">
  <div class="card">
    <h2>&#128200; Conteo por Dia de la Semana</h2>
    <div class="grid3">
      <div>
        <h3>Precio Normal</h3>
        {img(charts['day_normal'])}
      </div>
      <div>
        <h3>Precio Oferta</h3>
        {img(charts['day_oferta'])}
      </div>
      <div>
        <h3>Precio Mayoreo</h3>
        {img(charts['day_mayoreo'])}
      </div>
    </div>
  </div>
  <div class="card">
    <h2>&#129367;&#65039; Distribucion ES vs FdS (Precio Normal)</h2>
    <div style="max-width:400px;margin:auto">
      {img(charts['day_pie'])}
    </div>
  </div>
</div>

<!-- TAB 3 -->
<div id="t3" class="tab-pane">
  <div class="card">
    <h2>&#128197; Precio Normal por Mes &middot; Competidor (Top 10)</h2>
    {img(charts['mes_normal'])}
  </div>
  <div class="grid2">
    <div class="card">
      <h2>&#127991;&#65039; Precio Oferta por Mes</h2>
      {img(charts['mes_oferta'])}
    </div>
    <div class="card">
      <h2>&#128218; Precio Mayoreo por Mes</h2>
      {img(charts['mes_mayoreo'])}
    </div>
  </div>
</div>

<!-- TAB 4 -->
<div id="t4" class="tab-pane">
  <div class="card">
    <h2>&#9888;&#65039; Conteo FdS Precio Normal por Mes y Competidor (Top 15)</h2>
    <p class="subtitle" style="margin-bottom:10px">Una linea que baja o llega a cero = caida de cobertura en fines de semana</p>
    {img(charts['caida_normal'])}
  </div>
  <div class="grid2">
    <div class="card">
      <h2>&#127991;&#65039; Conteo FdS Oferta por Mes</h2>
      {img(charts['caida_oferta'])}
    </div>
    <div class="card">
      <h2>&#128218; Conteo FdS Mayoreo por Mes</h2>
      {img(charts['caida_mayoreo'])}
    </div>
  </div>
  <div class="card">{tables['caida']}</div>
</div>

<!-- TAB 5 -->
<div id="t5" class="tab-pane">
  <div class="card">
    <h2>&#128202; Evolucion Mensual Total (ES+FdS) &mdash; Precio Normal (Top 8 Competidores)</h2>
    {img(charts['mom_normal'])}
  </div>
  <div class="grid2">
    <div class="card">
      <h2>&#127991;&#65039; Evolucion Mensual Oferta</h2>
      {img(charts['mom_oferta'])}
    </div>
    <div class="card">
      <h2>&#128218; Evolucion Mensual Mayoreo</h2>
      {img(charts['mom_mayoreo'])}
    </div>
  </div>
  <div class="card">{tables['mom']}</div>
</div>

<!-- TAB 6 -->
<div id="t6" class="tab-pane">
  <div class="card">
    <h2>&#128200; Tendencia por Pais &mdash; Precio Normal &mdash; ES vs FdS</h2>
    {chr(10).join(f'<div style="margin-bottom:12px"><h3>{p}</h3>{img(charts["trend_" + p + "_es_normal"])}</div>' for p in charts.get('_paises', []) if 'trend_' + p + '_es_normal' in charts)}
  </div>
  <div class="card">
    <h2>&#127991;&#65039; Tendencia por Pais &mdash; Precio Oferta &mdash; FdS</h2>
    {chr(10).join(f'<div style="margin-bottom:12px"><h3>{p}</h3>{img(charts["trend_" + p + "_fds_oferta"])}</div>' for p in charts.get('_paises', []) if 'trend_' + p + '_fds_oferta' in charts)}
  </div>
</div>

<!-- TAB 7 -->
<div id="t7" class="tab-pane">
  <div class="card">
    <h2>&#128101; Distribucion de Categorias por Pais (Todos los meses, Normal)</h2>
    {img(charts['cat_pais_normal'])}
  </div>
  <div class="card">
    <h2>&#128200; Tendencia de Categorias por Mes &mdash; Precio Normal (Todos los Paises)</h2>
    {img(charts['cat_mes_todos_normal'])}
  </div>
  {chr(10).join(f'<div class="card"><h2>&#127759; {p} &mdash; Categorias por Mes (Normal)</h2>{img(charts["cat_" + p + "_normal"])}</div>' for p in charts.get('_paises', []) if 'cat_' + p + '_normal' in charts)}
  <div class="card">{tables['cat']}</div>
</div>

<script>{JS}</script>
</body>
</html>"""
