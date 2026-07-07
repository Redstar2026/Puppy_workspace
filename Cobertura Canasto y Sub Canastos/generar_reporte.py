"""Reporte Cobertura Canasto CAM 2026 - v3 desde cero.
Incluye: COLMENA, Chequeos Nielsen, sin MG Y TEXTIL, Clasificacion en %.
"""
import csv, json, os
from datetime import datetime
from collections import defaultdict

BASE    = r'C:\Users\shern22\Documents\puppy_workspace'
BQ      = os.path.join(BASE, 'bigquery_results')
CHARTJS = os.path.join(BQ, 'chartjs.min.js')
OUT     = os.path.join(BASE, 'Cobertura Canasto y Sub Canastos', 'reporte_cobertura_canasto.html')

def load_csv(path):
    with open(path, encoding='utf-8') as f:
        return list(csv.DictReader(f))

def load_chartjs():
    if os.path.exists(CHARTJS):
        with open(CHARTJS, encoding='utf-8') as f:
            return f.read()
    return "console.warn('Chart.js no disponible');"

def sj(obj):
    return json.dumps(obj, ensure_ascii=False).replace('</', '<\\/')

def fn(v):
    try:
        n = float(str(v).replace(',',''))
        if abs(n)>=1e9: return f'{n/1e9:,.2f}B'
        if abs(n)>=1e6: return f'{n/1e6:,.2f}M'
        if abs(n)>=1e3: return f'{n/1e3:,.1f}K'
        return f'{n:,.2f}'
    except: return str(v)

def uniq(data, field):
    seen,out=[],[]
    [out.append(r[field]) or seen.append(r[field]) for r in data if r.get(field) and r[field] not in seen]
    return sorted(out)

def sel(eid, vals, ph):
    o=''.join(f'<option value="{v}">{v}</option>' for v in vals)
    return f'<select id="{eid}"><option value="">{ph}</option>{o}</select>'

# --------------- Carga de datos ---------------
print("Cargando datos...", flush=True)

# Bloque A1/A3/CLAS
bloque = load_csv(os.path.join(BQ,'analisis-canasto-completo-colmena-nielsen-20260707-172202.csv'))
a1  = [r for r in bloque if r['BLOQUE']=='A1_PAIS']
a3o = [r for r in bloque if r['BLOQUE']=='A3_OPPS']
a3p = [r for r in bloque if r['BLOQUE']=='A3_PS']
a3  = [{**r,'SUB_CANASTO':'OPPS'} for r in a3o] + [{**r,'SUB_CANASTO':'PS'} for r in a3p]
clas_raw = [r for r in bloque if r['BLOQUE']=='CLAS_PAIS']

# A2 / A4 / A5+A6
a2  = load_csv(os.path.join(BQ,'cobertura-canasto-pais-formato-division-colmena-nielsen-20260707-172009.csv'))
a4  = load_csv(os.path.join(BQ,'analisis4-mp-ext-mp-int-colmena-20260707-172024.csv'))
a56 = load_csv(os.path.join(BASE,'analisis-5-6-chequeos-nielsen-cobertura.csv'))
a5  = [r for r in a56 if 'A5' in r.get('ANALISIS','')]
a6  = [r for r in a56 if 'A6' in r.get('ANALISIS','')]

# Pivot Clasificacion: {PAIS -> {TIER -> {vt,it}}}
TIERS  = ['TIER_1','TIER_2','TIER_3','SIN CLASIFICACION']
PAISES = ['CR','GT','HN','NI','SV']
cpiv   = {p:{t:{'vt':0.,'it':0} for t in TIERS} for p in PAISES}
for r in clas_raw:
    p,t = r['PAIS'], r['CLASIFICACION']
    if p in cpiv and t in cpiv[p]:
        cpiv[p][t]['vt'] = float(r['VENTAS_TOTALES'])
        cpiv[p][t]['it'] = int(r['ITEMS_TOTALES'])

# Formato total (ventas sumables)
fmap = defaultdict(lambda:{'vt':0.,'vc':0.})
for r in a2:
    fmap[r['FORMATO']]['vt'] += float(r['VENTAS_TOTALES'])
    fmap[r['FORMATO']]['vc'] += float(r['VENTAS_CANASTO'])
fmt_agg = sorted([{'FORMATO':k,'VT':round(v['vt'],2),'VC':round(v['vc'],2),
                   'PCT':round(v['vc']/v['vt']*100,2) if v['vt'] else 0}
                  for k,v in fmap.items()], key=lambda x:-x['PCT'])

# COLMENA por Pais (agregado desde a4)
col_pais = {}
for r in a4:
    if r['TIPO']!='COLMENA': continue
    p = r['PAIS']
    if p not in col_pais:
        col_pais[p]={'vt':0.,'vc':0.,'it':0,'ic':0}
    col_pais[p]['vt']+=float(r['VENTAS_UNIVERSO_MP'])
    col_pais[p]['vc']+=float(r['VENTAS_SUBCANASTO'])
    col_pais[p]['it']+=int(r['ITEMS_UNIVERSO_MP'])
    col_pais[p]['ic']+=int(r['ITEMS_SUBCANASTO'])

# KPIs globales
tvt  = sum(float(r['VENTAS_TOTALES']) for r in a1)
tvc  = sum(float(r['VENTAS_CANASTO']) for r in a1)
pctg = round(tvc/tvt*100,2) if tvt else 0
best = max(a1, key=lambda r: float(r['PCT_COB_VENTAS']))
wrst = min(a1, key=lambda r: float(r['PCT_COB_VENTAS']))

print(f"Universo: {fn(tvt)} | Cob: {pctg}%", flush=True)
cjs = load_chartjs()

# --------------- CSS ---------------
CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',Arial,sans-serif;background:#f2f3f4;color:#1a1a1a;font-size:14px}
header{background:#0053e2;color:#fff;padding:18px 32px}
header h1{font-size:19px;font-weight:700}
header p{font-size:12px;opacity:.85;margin-top:3px}
.container{max-width:1400px;margin:0 auto;padding:20px 16px}
.kpi-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(185px,1fr));gap:14px;margin-bottom:22px}
.kpi{background:#fff;border-radius:8px;padding:18px;border-top:4px solid #0053e2;box-shadow:0 1px 4px rgba(0,0,0,.07)}
.kpi .lbl{font-size:11px;color:#6b6b6b;text-transform:uppercase;letter-spacing:.4px;margin-bottom:5px}
.kpi .val{font-size:24px;font-weight:800;color:#0053e2}
.kpi .sub{font-size:11px;color:#6b6b6b;margin-top:3px}
.kpi.g .val{color:#2a8703}.kpi.r .val{color:#ea1100}.kpi.y .val{color:#995213}
.tab-bar{display:flex;flex-wrap:wrap;gap:3px;margin-bottom:16px;background:#fff;padding:7px;
  border-radius:10px;box-shadow:0 1px 4px rgba(0,0,0,.07)}
.tab-btn{padding:7px 14px;border:none;border-radius:6px;cursor:pointer;font-size:13px;
  font-weight:600;background:transparent;color:#6b6b6b;transition:.15s}
.tab-btn:hover{background:#f2f3f4}.tab-btn.active{background:#0053e2;color:#fff}
.tab-pane{display:none}.tab-pane.active{display:block}
.card{background:#fff;border-radius:10px;padding:22px;box-shadow:0 1px 4px rgba(0,0,0,.07);margin-bottom:16px}
.card h2{font-size:15px;font-weight:700;color:#0053e2;margin-bottom:14px;padding-bottom:9px;border-bottom:2px solid #f2f3f4}
.card h3{font-size:13px;font-weight:600;color:#1a1a1a;margin:14px 0 8px}
.nota{font-size:12px;color:#6b6b6b;font-style:italic;margin-bottom:10px}
.cw{position:relative;height:300px;width:100%}
.cw-lg{position:relative;height:360px;width:100%}
.cgrid{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px}
@media(max-width:768px){.cgrid{grid-template-columns:1fr}}
.tc{display:flex;flex-wrap:wrap;gap:7px;align-items:center;margin-bottom:10px}
.tc input,.tc select{padding:6px 10px;border:1px solid #c9cacf;border-radius:6px;font-size:13px;
  outline:none;color:#1a1a1a}
.tc input:focus,.tc select:focus{border-color:#0053e2}
.tc button{padding:6px 13px;border:none;border-radius:6px;cursor:pointer;font-size:13px;font-weight:600}
.dl{background:#ffc220;color:#1a1a1a}.dl:hover{background:#e6ad00}
.pg{background:#f2f3f4;color:#1a1a1a}.pg:hover{background:#c9cacf}
.tw{overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:13px}
th{background:#0053e2;color:#fff;padding:8px 11px;text-align:left;font-weight:600;white-space:nowrap;position:sticky;top:0}
td{padding:7px 11px;border-bottom:1px solid #f2f3f4;white-space:nowrap}
tr:hover td{background:#f2f3f4}tr:nth-child(even) td{background:#fafafa}
.nm{text-align:right}.pt{text-align:right;font-weight:700}
.gd{color:#2a8703}.wn{color:#995213}.bd{color:#ea1100}
.bb{background:#e8ecf3;border-radius:3px;height:9px;min-width:70px}
.bf{height:9px;border-radius:3px}
.ins{background:#fff8e1;border-left:4px solid #ffc220;border-radius:0 7px 7px 0;padding:12px 15px;margin-bottom:10px}
.igrid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:14px}
@media(max-width:768px){.igrid{grid-template-columns:1fr}}
.pill{display:inline-block;padding:2px 7px;border-radius:20px;font-size:11px;font-weight:700}
.pb{background:#dce9fb;color:#0053e2}.py{background:#fff3cd;color:#995213}
.pg2{background:#d4edda;color:#2a8703}.pr{background:#fde8e8;color:#ea1100}
.pag{display:flex;gap:5px;align-items:center;margin-top:8px}
.pag span{font-size:12px;color:#6b6b6b}
"""

# --------------- JS (raw string) ---------------
JS = r"""
function esc(v){return v==null?'':String(v).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
function fN(v){var n=parseFloat(v);if(isNaN(n))return v||'';if(Math.abs(n)>=1e9)return(n/1e9).toFixed(2)+'B';if(Math.abs(n)>=1e6)return(n/1e6).toFixed(2)+'M';if(Math.abs(n)>=1e3)return(n/1e3).toFixed(1)+'K';return n.toLocaleString('es-GT',{minimumFractionDigits:2,maximumFractionDigits:2});}
function fP(v){var n=parseFloat(v);return isNaN(n)?v||'':n.toFixed(2)+'%';}
function pc(v){var n=parseFloat(v);if(isNaN(n))return'';return n>=85?'gd':n>=65?'wn':'bd';}
function bar(pct,col){var n=Math.min(parseFloat(pct)||0,100);var c=col||(n>=85?'#0053e2':n>=65?'#ffc220':'#ea1100');return '<td><div class="bb"><div class="bf" style="width:'+n+'%;background:'+c+'"></div></div></td>';}
function dlCSV(hs,rows,fn){var l=[hs.join(',')];rows.forEach(function(r){l.push(hs.map(function(h){return'"'+String(r[h]||'').replace(/"/g,'""')+'"';}).join(','));});var a=document.createElement('a');a.href=URL.createObjectURL(new Blob(['\uFEFF'+l.join('\n')],{type:'text/csv;charset=utf-8;'}));a.download=fn;a.click();}
document.querySelectorAll('.tab-btn').forEach(function(b){b.addEventListener('click',function(){document.querySelectorAll('.tab-btn').forEach(function(x){x.classList.remove('active');});document.querySelectorAll('.tab-pane').forEach(function(x){x.classList.remove('active');});this.classList.add('active');document.getElementById(this.dataset.tab).classList.add('active');});});
function pT(cfg){
  var PAGE=cfg.ps||50,page=1,flt=cfg.data.slice(),el=document.getElementById(cfg.id);
  function gf(){var q=(document.getElementById(cfg.si)||{value:''}).value.toLowerCase();var s={};(cfg.sels||[]).forEach(function(x){var e=document.getElementById(x.id);s[x.f]=e?e.value:'';});return{q:q,s:s};}
  function ap(){var f=gf();flt=cfg.data.filter(function(r){if(f.q&&Object.values(r).join(' ').toLowerCase().indexOf(f.q)<0)return false;for(var k in f.s){if(f.s[k]&&r[k]!==f.s[k])return false;}return true;});page=1;rn();}
  function rn(){var tot=flt.length,pgs=Math.max(1,Math.ceil(tot/PAGE));page=Math.min(page,pgs);var sl=flt.slice((page-1)*PAGE,page*PAGE);var h='<table><thead><tr>';cfg.cols.forEach(function(c){h+='<th>'+esc(c.l)+'</th>';});h+='</tr></thead><tbody>';if(!sl.length)h+='<tr><td colspan="'+cfg.cols.length+'" style="text-align:center;padding:18px;color:#6b6b6b">Sin resultados</td></tr>';sl.forEach(function(r){h+='<tr>';cfg.cols.forEach(function(c){h+=c.f2?c.f2(r):'<td>'+esc(r[c.f]||'')+'</td>';});h+='</tr>';});h+='</tbody></table><div class="pag"><button class="pg" onclick="__p_'+cfg.id+'(-1)">&#9664;</button><span>Pag '+page+' de '+pgs+' | '+tot+' reg</span><button class="pg" onclick="__p_'+cfg.id+'(1)">&#9654;</button></div>';el.innerHTML=h;}
  window['__p_'+cfg.id]=function(d){page+=d;rn();};
  var si=document.getElementById(cfg.si);if(si)si.addEventListener('input',ap);
  (cfg.sels||[]).forEach(function(x){var e=document.getElementById(x.id);if(e)e.addEventListener('change',ap);});
  var db=document.getElementById(cfg.id+'_dl');if(db)db.addEventListener('click',function(){dlCSV(cfg.cols.map(function(c){return c.f;}),flt,cfg.id+'.csv');});
  rn();
}
var FC={'BODEGAS':'#0053e2','DESCUENTO':'#2a8703','SUPERMERCADOS':'#ffc220','WALMART':'#ea1100'};
var TC={'TIER_1':'#0053e2','TIER_2':'#ffc220','TIER_3':'#4c9be8','SIN CLASIFICACION':'#c9cacf'};
function chBar(id,labels,datasets,opts){
  var el=document.getElementById(id);if(!el)return;
  new Chart(el,{type:'bar',data:{labels:labels,datasets:datasets},options:Object.assign({responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'top'}}},opts||{})});
}
window.addEventListener('load',function(){

// --- TAB 1 ---
chBar('ch1a',DATA_A1.map(function(r){return r.PAIS;}),
  [{label:'% Cob Ventas',data:DATA_A1.map(function(r){return parseFloat(r.PCT_COB_VENTAS);}),backgroundColor:'#0053e2',borderRadius:4},
   {label:'% Cob Items', data:DATA_A1.map(function(r){return parseFloat(r.PCT_COB_ITEMS);}), backgroundColor:'#ffc220',borderRadius:4}],
  {scales:{y:{beginAtZero:true,max:100,ticks:{callback:function(v){return v+'%';}},grid:{color:'#f2f3f4'}},x:{grid:{display:false}}}});
chBar('ch1b',DATA_A1.map(function(r){return r.PAIS;}),
  [{label:'Canasto (M)',data:DATA_A1.map(function(r){return parseFloat(r.VENTAS_CANASTO)/1e6;}),backgroundColor:'#2a8703',borderRadius:4},
   {label:'Fuera (M)',  data:DATA_A1.map(function(r){return parseFloat(r.VENTAS_TOTALES-r.VENTAS_CANASTO)/1e6;}),backgroundColor:'#ea1100',borderRadius:4}],
  {scales:{x:{stacked:true,grid:{display:false}},y:{stacked:true,ticks:{callback:function(v){return'$'+v+'M';}},grid:{color:'#f2f3f4'}}}});

// --- TAB 2: Formato ---
chBar('ch2ft',DATA_FMT.map(function(r){return r.FORMATO;}),
  [{label:'% Cob Ventas',data:DATA_FMT.map(function(r){return parseFloat(r.PCT);}),
    backgroundColor:DATA_FMT.map(function(r){return FC[r.FORMATO]||'#0053e2';}),borderRadius:5}],
  {plugins:{legend:{display:false},tooltip:{callbacks:{label:function(c){return c.parsed.y.toFixed(2)+'%';}}}},
   scales:{y:{beginAtZero:true,max:100,ticks:{callback:function(v){return v+'%';}},grid:{color:'#f2f3f4'}},x:{grid:{display:false}}}});
(function(){
  var ps=['CR','GT','HN','NI','SV'],fs=['BODEGAS','DESCUENTO','SUPERMERCADOS','WALMART'];
  chBar('ch2fp',ps,fs.map(function(f){
    return{label:f,backgroundColor:FC[f],borderRadius:3,
      data:ps.map(function(p){
        var rows=DATA_A2.filter(function(r){return r.PAIS===p&&r.FORMATO===f;});
        var vt=rows.reduce(function(s,r){return s+parseFloat(r.VENTAS_TOTALES);},0);
        var vc=rows.reduce(function(s,r){return s+parseFloat(r.VENTAS_CANASTO);},0);
        return vt?parseFloat((vc/vt*100).toFixed(2)):0;
      })};
  }),{scales:{y:{beginAtZero:true,max:100,ticks:{callback:function(v){return v+'%';}},grid:{color:'#f2f3f4'}},x:{grid:{display:false}}}});
})();
pT({id:'tblA2',data:DATA_A2,ps:50,si:'srcA2',
  sels:[{id:'fA2p',f:'PAIS'},{id:'fA2f',f:'FORMATO'},{id:'fA2d',f:'DIVISION'}],
  cols:[{f:'PAIS',l:'Pais'},{f:'FORMATO',l:'Formato'},{f:'DIVISION',l:'Division'},
    {f:'VENTAS_TOTALES',l:'Vtas Tot',f2:function(r){return'<td class="nm">'+fN(r.VENTAS_TOTALES)+'</td>';}},
    {f:'VENTAS_CANASTO',l:'Vtas Can',f2:function(r){return'<td class="nm">'+fN(r.VENTAS_CANASTO)+'</td>';}},
    {f:'VENTAS_FUERA',l:'Vtas Fuera',f2:function(r){return'<td class="nm">'+fN(r.VENTAS_FUERA)+'</td>';}},
    {f:'PCT_COB_VENTAS',l:'% Cob Vtas',f2:function(r){return'<td class="pt '+pc(r.PCT_COB_VENTAS)+'">'+fP(r.PCT_COB_VENTAS)+'</td>';}},
    {f:'ITEMS_TOTALES',l:'Items Tot',f2:function(r){return'<td class="nm">'+parseInt(r.ITEMS_TOTALES).toLocaleString()+'</td>';}},
    {f:'ITEMS_CANASTO',l:'Items Can',f2:function(r){return'<td class="nm">'+parseInt(r.ITEMS_CANASTO).toLocaleString()+'</td>';}},
    {f:'PCT_COB_ITEMS',l:'% Cob Items',f2:function(r){return'<td class="pt '+pc(r.PCT_COB_ITEMS)+'">'+fP(r.PCT_COB_ITEMS)+'</td>';}},
    {f:'PCT_COB_VENTAS',l:'Barra',f2:function(r){return bar(r.PCT_COB_VENTAS);}}]});

// --- TAB 3: OPPS / PS ---
(function(){
  var opps=DATA_A3.filter(function(r){return r.SUB_CANASTO==='OPPS';});
  var ps=DATA_A3.filter(function(r){return r.SUB_CANASTO==='PS';});
  chBar('ch3',opps.map(function(r){return r.PAIS;}),
    [{label:'OPPS % Ventas',data:opps.map(function(r){return parseFloat(r.PCT_COB_VENTAS);}),backgroundColor:'#0053e2',borderRadius:4},
     {label:'PS % Ventas',  data:ps.map(function(r){return parseFloat(r.PCT_COB_VENTAS);}),  backgroundColor:'#ffc220',borderRadius:4}],
    {scales:{y:{beginAtZero:true,ticks:{callback:function(v){return v+'%';}},grid:{color:'#f2f3f4'}},x:{grid:{display:false}}}});
})();

// --- TAB 4: MP_EXT / MP_INT / COLMENA ---
(function(){
  var tipos=['MP_EXT','MP_INT','COLMENA'];
  var cols4={'MP_EXT':'#0053e2','MP_INT':'#4c9be8','COLMENA':'#2a8703'};
  var ps=['CR','GT','HN','NI','SV'];
  function avgP(tipo,pais){
    var rows=DATA_A4.filter(function(r){return r.TIPO===tipo&&r.PAIS===pais&&parseFloat(r.PCT_COB_VENTAS)>0;});
    if(!rows.length)return 0;
    return rows.reduce(function(s,r){return s+parseFloat(r.PCT_COB_VENTAS);},0)/rows.length;
  }
  chBar('ch4',ps,tipos.map(function(t){
    return{label:t,backgroundColor:cols4[t],borderRadius:4,data:ps.map(function(p){return avgP(t,p);})};
  }),{scales:{y:{beginAtZero:true,ticks:{callback:function(v){return v.toFixed(0)+'%';}},grid:{color:'#f2f3f4'}},x:{grid:{display:false}}}});

  // COLMENA por pais barras absolutas
  var colPais=DATA_COL_PAIS;
  chBar('ch4col',colPais.map(function(r){return r.pais;}),
    [{label:'% Cob Ventas (Univ MP)',data:colPais.map(function(r){return r.pctv;}),backgroundColor:'#2a8703',borderRadius:4},
     {label:'% Cob Items (Univ MP)', data:colPais.map(function(r){return r.pcti;}),backgroundColor:'#ffc220',borderRadius:4}],
    {scales:{y:{beginAtZero:true,max:100,ticks:{callback:function(v){return v+'%';}},grid:{color:'#f2f3f4'}},x:{grid:{display:false}}}});
})();

pT({id:'tblA4',data:DATA_A4,ps:50,si:'srcA4',
  sels:[{id:'fA4t',f:'TIPO'},{id:'fA4p',f:'PAIS'},{id:'fA4f',f:'FORMATO'}],
  cols:[{f:'TIPO',l:'Tipo'},{f:'PAIS',l:'Pais'},{f:'FORMATO',l:'Formato'},{f:'DIVISION',l:'Division'},
    {f:'VENTAS_UNIVERSO_MP',l:'Vtas Univ MP',f2:function(r){return'<td class="nm">'+fN(r.VENTAS_UNIVERSO_MP)+'</td>';}},
    {f:'VENTAS_SUBCANASTO',l:'Vtas Subcan',f2:function(r){return'<td class="nm">'+fN(r.VENTAS_SUBCANASTO)+'</td>';}},
    {f:'PCT_COB_VENTAS',l:'% Cob Vtas',f2:function(r){return'<td class="pt '+pc(r.PCT_COB_VENTAS)+'">'+fP(r.PCT_COB_VENTAS)+'</td>';}},
    {f:'ITEMS_UNIVERSO_MP',l:'Items Univ MP',f2:function(r){return'<td class="nm">'+parseInt(r.ITEMS_UNIVERSO_MP).toLocaleString()+'</td>';}},
    {f:'ITEMS_SUBCANASTO',l:'Items Subcan',f2:function(r){return'<td class="nm">'+parseInt(r.ITEMS_SUBCANASTO).toLocaleString()+'</td>';}},
    {f:'PCT_COB_ITEMS',l:'% Cob Items',f2:function(r){return'<td class="pt '+pc(r.PCT_COB_ITEMS)+'">'+fP(r.PCT_COB_ITEMS)+'</td>';}},
    {f:'PCT_COB_VENTAS',l:'Barra',f2:function(r){return bar(r.PCT_COB_VENTAS);}}]});

// --- TAB 5: Chequeos vs Canasto ---
(function(){
  var bp={};DATA_A5.forEach(function(r){if(!bp[r.PAIS])bp[r.PAIS]={vc:0,vch:0};bp[r.PAIS].vc+=parseFloat(r.VENTAS_CANASTO)||0;bp[r.PAIS].vch+=parseFloat(r.VENTAS_CON_CHEQUEOS)||0;});
  var ls=Object.keys(bp).sort();
  chBar('ch5',ls,[{label:'% Cob Ventas (Nielsen+comp)',data:ls.map(function(p){return bp[p].vc?parseFloat((bp[p].vch/bp[p].vc*100).toFixed(2)):0;}),backgroundColor:'#0053e2',borderRadius:4}],
    {plugins:{legend:{display:false}},scales:{y:{beginAtZero:true,max:100,ticks:{callback:function(v){return v+'%';}},grid:{color:'#f2f3f4'}},x:{grid:{display:false}}}});
})();
pT({id:'tblA5',data:DATA_A5,ps:50,si:'srcA5',
  sels:[{id:'fA5p',f:'PAIS'},{id:'fA5f',f:'FORMATO'}],
  cols:[{f:'PAIS',l:'Pais'},{f:'FORMATO',l:'Formato'},{f:'DIVISION',l:'Division'},
    {f:'VENTAS_CANASTO',l:'Vtas Canasto',f2:function(r){return'<td class="nm">'+fN(r.VENTAS_CANASTO)+'</td>';}},
    {f:'VENTAS_CON_CHEQUEOS',l:'Vtas c/Cheq',f2:function(r){return'<td class="nm">'+fN(r.VENTAS_CON_CHEQUEOS)+'</td>';}},
    {f:'PCT_COB_VENTAS',l:'% Cob Vtas',f2:function(r){return'<td class="pt '+pc(r.PCT_COB_VENTAS)+'">'+fP(r.PCT_COB_VENTAS)+'</td>';}},
    {f:'ITEMS_CANASTO',l:'Items Can',f2:function(r){return'<td class="nm">'+parseInt(r.ITEMS_CANASTO).toLocaleString()+'</td>';}},
    {f:'ITEMS_CON_CHEQUEOS',l:'Items c/Cheq',f2:function(r){return'<td class="nm">'+parseInt(r.ITEMS_CON_CHEQUEOS).toLocaleString()+'</td>';}},
    {f:'PCT_COB_ITEMS',l:'% Cob Items',f2:function(r){return'<td class="pt '+pc(r.PCT_COB_ITEMS)+'">'+fP(r.PCT_COB_ITEMS)+'</td>';}},
    {f:'PCT_COB_VENTAS',l:'Barra',f2:function(r){return bar(r.PCT_COB_VENTAS);}}]});

// --- TAB 6: Chequeos vs Universo ---
(function(){
  var bp={};DATA_A6.forEach(function(r){if(!bp[r.PAIS])bp[r.PAIS]={vt:0,vch:0};bp[r.PAIS].vt+=parseFloat(r.VENTAS_CANASTO)||0;bp[r.PAIS].vch+=parseFloat(r.VENTAS_CON_CHEQUEOS)||0;});
  var ls=Object.keys(bp).sort();
  chBar('ch6',ls,[{label:'% Cob Ventas vs Universo',data:ls.map(function(p){return bp[p].vt?parseFloat((bp[p].vch/bp[p].vt*100).toFixed(2)):0;}),backgroundColor:'#2a8703',borderRadius:4}],
    {plugins:{legend:{display:false}},scales:{y:{beginAtZero:true,max:100,ticks:{callback:function(v){return v+'%';}},grid:{color:'#f2f3f4'}},x:{grid:{display:false}}}});
})();
pT({id:'tblA6',data:DATA_A6,ps:50,si:'srcA6',
  sels:[{id:'fA6p',f:'PAIS'},{id:'fA6f',f:'FORMATO'}],
  cols:[{f:'PAIS',l:'Pais'},{f:'FORMATO',l:'Formato'},{f:'DIVISION',l:'Division'},
    {f:'VENTAS_CANASTO',l:'Vtas Universo',f2:function(r){return'<td class="nm">'+fN(r.VENTAS_CANASTO)+'</td>';}},
    {f:'VENTAS_CON_CHEQUEOS',l:'Vtas c/Cheq',f2:function(r){return'<td class="nm">'+fN(r.VENTAS_CON_CHEQUEOS)+'</td>';}},
    {f:'PCT_COB_VENTAS',l:'% Cob Vtas',f2:function(r){return'<td class="pt '+pc(r.PCT_COB_VENTAS)+'">'+fP(r.PCT_COB_VENTAS)+'</td>';}},
    {f:'ITEMS_CANASTO',l:'Items Universo',f2:function(r){return'<td class="nm">'+parseInt(r.ITEMS_CANASTO).toLocaleString()+'</td>';}},
    {f:'ITEMS_CON_CHEQUEOS',l:'Items c/Cheq',f2:function(r){return'<td class="nm">'+parseInt(r.ITEMS_CON_CHEQUEOS).toLocaleString()+'</td>';}},
    {f:'PCT_COB_ITEMS',l:'% Cob Items',f2:function(r){return'<td class="pt '+pc(r.PCT_COB_ITEMS)+'">'+fP(r.PCT_COB_ITEMS)+'</td>';}},
    {f:'PCT_COB_VENTAS',l:'Barra',f2:function(r){return bar(r.PCT_COB_VENTAS);}}]});

// --- TAB C: Clasificacion 100% apilado ---
(function(){
  var ps=['CR','GT','HN','NI','SV'],ts=['TIER_1','TIER_2','TIER_3','SIN CLASIFICACION'];
  function pctTier(tier,field){
    return ps.map(function(p){
      var tot=ts.reduce(function(s,t){var r=DATA_CLAS.filter(function(x){return x.PAIS===p&&x.CLASIFICACION===t;})[0];return s+(r?parseFloat(r[field]):0);},0);
      var row=DATA_CLAS.filter(function(x){return x.PAIS===p&&x.CLASIFICACION===tier;})[0];
      return tot?parseFloat(((row?parseFloat(row[field]):0)/tot*100).toFixed(1)):0;
    });
  }
  var el=document.getElementById('chCv');if(el)new Chart(el,{type:'bar',data:{labels:ps,datasets:ts.map(function(t){return{label:t,data:pctTier(t,'VENTAS_TOTALES'),backgroundColor:TC[t]};})},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'top'},tooltip:{callbacks:{label:function(c){return c.dataset.label+': '+c.parsed.y.toFixed(1)+'%';}}}},scales:{x:{stacked:true,grid:{display:false}},y:{stacked:true,max:100,ticks:{callback:function(v){return v+'%';}},grid:{color:'#f2f3f4'}}}}});
  var el2=document.getElementById('chCi');if(el2)new Chart(el2,{type:'bar',data:{labels:ps,datasets:ts.map(function(t){return{label:t,data:pctTier(t,'ITEMS_TOTALES'),backgroundColor:TC[t]};})},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'top'},tooltip:{callbacks:{label:function(c){return c.dataset.label+': '+c.parsed.y.toFixed(1)+'%';}}}},scales:{x:{stacked:true,grid:{display:false}},y:{stacked:true,max:100,ticks:{callback:function(v){return v+'%';}},grid:{color:'#f2f3f4'}}}}});
})();

}); // end load
"""


# --------------- Funciones tabla HTML ---------------
def pais_rows():
    rows = ''
    for r in a1:
        pv = float(r['PCT_COB_VENTAS']); pi = float(r['PCT_COB_ITEMS'])
        cv = 'gd' if pv>=90 else ('wn' if pv>=80 else 'bd')
        ci = 'gd' if pi>=40 else ('wn' if pi>=25 else 'bd')
        rows += (f'<tr><td><strong>{r["PAIS"]}</strong></td>'
            f'<td class="nm">{fn(r["VENTAS_TOTALES"])}</td>'
            f'<td class="nm">{fn(r["VENTAS_CANASTO"])}</td>'
            f'<td class="nm">{fn(float(r["VENTAS_TOTALES"])-float(r["VENTAS_CANASTO"]))}</td>'
            f'<td class="pt {cv}">{pv}%</td>'
            f'<td class="nm">{int(r["ITEMS_TOTALES"]):,}</td>'
            f'<td class="nm">{int(r["ITEMS_CANASTO"]):,}</td>'
            f'<td class="nm">{int(r["ITEMS_TOTALES"])-int(r["ITEMS_CANASTO"]):,}</td>'
            f'<td class="pt {ci}">{pi}%</td></tr>')
    return rows

def fmt_rows():
    cols = {'BODEGAS':'#0053e2','DESCUENTO':'#2a8703','SUPERMERCADOS':'#ffc220','WALMART':'#ea1100'}
    rows = ''
    for r in fmt_agg:
        p = r['PCT']; cv = 'gd' if p>=90 else ('wn' if p>=80 else 'bd')
        c = cols.get(r['FORMATO'],'#0053e2')
        bh = f'<div class="bb"><div class="bf" style="width:{min(p,100)}%;background:{c}"></div></div>'
        rows += (f'<tr><td><strong>{r["FORMATO"]}</strong></td>'
            f'<td class="nm">{fn(r["VT"])}</td><td class="nm">{fn(r["VC"])}</td>'
            f'<td class="pt {cv}">{p}%</td><td>{bh}</td></tr>')
    return rows

def opps_ps_rows():
    rows = ''
    for r in a3:
        s = r['SUB_CANASTO']
        pill = 'pb' if s=='OPPS' else 'py'
        cv = 'wn'
        rows += (f'<tr><td><span class="pill {pill}">{s}</span></td>'
            f'<td><strong>{r["PAIS"]}</strong></td>'
            f'<td class="nm">{fn(r["VENTAS_TOTALES"])}</td>'
            f'<td class="nm">{fn(r["VENTAS_CANASTO"])}</td>'
            f'<td class="pt {cv}">{r["PCT_COB_VENTAS"]}%</td>'
            f'<td class="nm">{int(r["ITEMS_TOTALES"]):,}</td>'
            f'<td class="nm">{int(r["ITEMS_CANASTO"]):,}</td>'
            f'<td class="pt">{r["PCT_COB_ITEMS"]}%</td></tr>')
    return rows

def colmena_pais_rows():
    rows = ''
    PILLS={'MP_EXT':'pb','MP_INT':'pg2','COLMENA':'pr'}
    for tipo in ['MP_EXT','MP_INT','COLMENA']:
        rows_tipo = [r for r in a4 if r['TIPO']==tipo]
        pais_agg = {}
        for r in rows_tipo:
            p = r['PAIS']
            if p not in pais_agg: pais_agg[p]={'vt':0.,'vc':0.,'it':0,'ic':0}
            pais_agg[p]['vt']+=float(r['VENTAS_UNIVERSO_MP'])
            pais_agg[p]['vc']+=float(r['VENTAS_SUBCANASTO'])
            pais_agg[p]['it']+=int(r['ITEMS_UNIVERSO_MP'])
            pais_agg[p]['ic']+=int(r['ITEMS_SUBCANASTO'])
        for p in PAISES:
            if p not in pais_agg: continue
            d = pais_agg[p]
            pv = round(d['vc']/d['vt']*100,2) if d['vt'] else 0
            pi = round(d['ic']/d['it']*100,2) if d['it'] else 0
            cv = 'gd' if pv>=50 else ('wn' if pv>=25 else 'bd')
            rows += (f'<tr><td><span class="pill {PILLS[tipo]}">{tipo}</span></td>'
                f'<td><strong>{p}</strong></td>'
                f'<td class="nm">{fn(d["vt"])}</td><td class="nm">{fn(d["vc"])}</td>'
                f'<td class="pt {cv}">{pv}%</td>'
                f'<td class="nm">{d["it"]:,}</td><td class="nm">{d["ic"]:,}</td>'
                f'<td class="pt">{pi}%</td></tr>')
    return rows

def clas_header():
    TLAB=['TIER 1','TIER 2','TIER 3','Sin Clas.']; TPILL=['pb','py','pg2','']
    h='<thead><tr><th rowspan="2" style="vertical-align:middle">Pais</th>'
    for l,p in zip(TLAB,TPILL):
        h+=f'<th colspan="3" style="text-align:center"><span class="pill {p}">{l}</span></th>'
    h+='</tr><tr>'
    for _ in TLAB: h+='<th>% Vtas</th><th style="min-width:70px">Barra</th><th>% Items</th>'
    h+='</tr></thead>'
    return h

def clas_rows():
    TCOLS={'TIER_1':'#0053e2','TIER_2':'#ffc220','TIER_3':'#4c9be8','SIN CLASIFICACION':'#c9cacf'}
    rows=''
    for p in PAISES:
        pvt=sum(cpiv[p][t]['vt'] for t in TIERS)
        pit=sum(cpiv[p][t]['it'] for t in TIERS)
        rows+=f'<tr><td><strong>{p}</strong></td>'
        for t in TIERS:
            pv=round(cpiv[p][t]['vt']/pvt*100,1) if pvt else 0
            pi=round(cpiv[p][t]['it']/pit*100,1) if pit else 0
            c=TCOLS[t]
            bh=f'<div class="bb"><div class="bf" style="width:{min(pv,100)}%;background:{c}"></div></div>'
            rows+=f'<td class="pt">{pv}%</td><td>{bh}</td><td class="pt">{pi}%</td>'
        rows+='</tr>'
    # Fila region
    rvt={t:sum(cpiv[p][t]['vt'] for p in PAISES) for t in TIERS}
    rit={t:sum(cpiv[p][t]['it'] for p in PAISES) for t in TIERS}
    tvt=sum(rvt.values()); tit=sum(rit.values())
    rows+='<tr style="background:#f2f3f4;font-weight:700"><td>REGION</td>'
    for t in TIERS:
        pv=round(rvt[t]/tvt*100,1) if tvt else 0
        pi=round(rit[t]/tit*100,1) if tit else 0
        c=TCOLS[t]
        bh=f'<div class="bb"><div class="bf" style="width:{min(pv,100)}%;background:{c}"></div></div>'
        rows+=f'<td class="pt">{pv}%</td><td>{bh}</td><td class="pt">{pi}%</td>'
    rows+='</tr>'
    return rows


# --------------- HTML builder ---------------
def build():
    fecha = datetime.now().strftime('%d/%m/%Y %H:%M')
    # COLMENA por pais para JS
    col_js = [{'pais':p,'pctv':round(d['vc']/d['vt']*100,2) if d['vt'] else 0,
                'pcti':round(d['ic']/d['it']*100,2) if d['it'] else 0}
               for p,d in sorted(col_pais.items())]
    djs = f"""<script>
var DATA_A1={sj(a1)};
var DATA_A2={sj(a2)};
var DATA_FMT={sj(fmt_agg)};
var DATA_A3={sj(a3)};
var DATA_A4={sj(a4)};
var DATA_A5={sj(a5)};
var DATA_A6={sj(a6)};
var DATA_CLAS={sj(clas_raw)};
var DATA_COL_PAIS={sj(col_js)};
</script>"""

    return f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Cobertura Canasto CAM 2026</title><style>{CSS}</style></head>
<body>
<header>
  <h1>Analisis de Cobertura de Canasto y Sub-Canastos - CAM 2026</h1>
  <p>SW 11-23 | 5 Paises: CR GT HN NI SV | Sin MG Y TEXTIL | COLMENA + Chequeos Nielsen incluidos | {fecha}</p>
</header>
<div class="container">
{djs}
<div class="kpi-grid">
  <div class="kpi"><div class="lbl">Ventas Totales Universo</div><div class="val">{fn(tvt)}</div><div class="sub">USD SW 11-23 2026 (sin MG Y TEXTIL)</div></div>
  <div class="kpi"><div class="lbl">Ventas en Canasto</div><div class="val">{fn(tvc)}</div><div class="sub">{pctg}% del universo</div></div>
  <div class="kpi r"><div class="lbl">Ventas Fuera Canasto</div><div class="val">{fn(tvt-tvc)}</div><div class="sub">{round(100-pctg,2)}% fuera</div></div>
  <div class="kpi g"><div class="lbl">% Cobertura Global</div><div class="val">{pctg}%</div><div class="sub">Promedio 5 paises</div></div>
  <div class="kpi y"><div class="lbl">Mejor Pais</div><div class="val">{best["PAIS"]}</div><div class="sub">{best["PCT_COB_VENTAS"]}% cob ventas</div></div>
  <div class="kpi r"><div class="lbl">Pais a Mejorar</div><div class="val">{wrst["PAIS"]}</div><div class="sub">{wrst["PCT_COB_VENTAS"]}% cob ventas</div></div>
  <div class="kpi g"><div class="lbl">Mejor Formato</div><div class="val">{fmt_agg[0]["FORMATO"]}</div><div class="sub">{fmt_agg[0]["PCT"]}% cob ventas</div></div>
  <div class="kpi y"><div class="lbl">Formato a Mejorar</div><div class="val">{fmt_agg[-1]["FORMATO"]}</div><div class="sub">{fmt_agg[-1]["PCT"]}% cob ventas</div></div>
</div>

<div class="tab-bar">
  <button class="tab-btn active" data-tab="t0">Resumen</button>
  <button class="tab-btn" data-tab="t1">1. Canasto por Pais</button>
  <button class="tab-btn" data-tab="t2">2. Formato y Division</button>
  <button class="tab-btn" data-tab="t3">3. OPPS y PS</button>
  <button class="tab-btn" data-tab="t4">4. Marcas Propias + COLMENA</button>
  <button class="tab-btn" data-tab="t5">5. Chequeos vs Canasto</button>
  <button class="tab-btn" data-tab="t6">6. Chequeos vs Universo</button>
  <button class="tab-btn" data-tab="tC">Clasificacion</button>
</div>

<!-- TAB 0 -->
<div id="t0" class="tab-pane active"><div class="card">
  <h2>Resumen Ejecutivo - Cobertura CAM 2026 (sin MG Y TEXTIL)</h2>
  <div class="igrid">
    <div class="ins"><strong>Cobertura global: {pctg}%</strong><br>{best["PAIS"]} lidera con {best["PCT_COB_VENTAS"]}%. {wrst["PAIS"]} es el de menor cobertura con {wrst["PCT_COB_VENTAS"]}%. Formato DESCUENTO es el mas cubierto ({fmt_agg[0]["PCT"]}%), WALMART el de menor ({fmt_agg[-1]["PCT"]}%).</div>
    <div class="ins"><strong>COLMENA (nuevo)</strong><br>Cobertura del sub-canasto COLMENA dentro del universo de Marcas Propias. ABARROTES lidera en COLMENA (hasta 99% en ventas MP). FRUTAS Y VEGETALES = 0% por diseno. Datos desde prcng_info_cam_MP_CANASTO_AGRUPACION.</div>
    <div class="ins"><strong>Chequeos incluye Nielsen</strong><br>Los Chequeos ahora combinan precios de competidores CAM + datos Nielsen (COD_SG 28500, 45300, 55100, 109300, 311000). Esto incrementa la cobertura de chequeos respecto al analisis anterior.</div>
    <div class="ins"><strong>Clasificacion TIERS</strong><br>TIER_1/2/3 tienen 100% de cobertura por definicion. SIN CLASIFICACION = $195M en ventas sin tier (fuera del canasto). Visualizacion en % del universo por pais.</div>
  </div>
</div></div>

<!-- TAB 1 -->
<div id="t1" class="tab-pane"><div class="card">
  <h2>Analisis 1 - Cobertura del Canasto por Pais (sin MG Y TEXTIL)</h2>
  <p class="nota">Datos directos de BigQuery con nueva query (COLMENA + Nielsen). Items = COUNT DISTINCT ITEM por pais.</p>
  <div class="cgrid">
    <div><h3>% Cobertura Ventas e Items por Pais</h3><div class="cw"><canvas id="ch1a"></canvas></div></div>
    <div><h3>Ventas Canasto vs Fuera (M USD) - apilado</h3><div class="cw"><canvas id="ch1b"></canvas></div></div>
  </div>
  <h3>Detalle por Pais</h3>
  <div class="tw"><table>
    <thead><tr><th>Pais</th><th>Vtas Totales</th><th>Vtas Canasto</th><th>Vtas Fuera</th>
      <th>% Cob Vtas</th><th>Items Tot</th><th>Items Can</th><th>Items Fuera</th><th>% Cob Items</th></tr></thead>
    <tbody>{pais_rows()}</tbody>
  </table></div>
</div></div>

<!-- TAB 2 -->
<div id="t2" class="tab-pane">
  <div class="card">
    <h2>Analisis 2 - Cobertura por Formato (Global y por Pais)</h2>
    <p class="nota">Ventas sumables entre paises. Items: COUNT DISTINCT independiente por pais.</p>
    <div class="cgrid">
      <div><h3>% Cob Ventas por Formato - todos los paises</h3><div class="cw"><canvas id="ch2ft"></canvas></div></div>
      <div><h3>% Cob Ventas por Formato x Pais</h3><div class="cw"><canvas id="ch2fp"></canvas></div></div>
    </div>
    <h3>Resumen Ventas por Formato (global)</h3>
    <div class="tw" style="margin-bottom:16px"><table>
      <thead><tr><th>Formato</th><th>Ventas Totales</th><th>Ventas Canasto</th><th>% Cob Vtas</th><th>Barra</th></tr></thead>
      <tbody>{fmt_rows()}</tbody>
    </table></div>
  </div>
  <div class="card">
    <h2>Detalle por Pais + Formato + Division</h2>
    <div class="tc">
      <input id="srcA2" type="text" placeholder="Buscar...">
      {sel('fA2p', uniq(a2,'PAIS'), 'Todos los Paises')}
      {sel('fA2f', uniq(a2,'FORMATO'), 'Todos los Formatos')}
      {sel('fA2d', uniq(a2,'DIVISION'), 'Todas las Divisiones')}
      <button class="dl" id="tblA2_dl">Descargar CSV</button>
    </div>
    <div class="tw"><div id="tblA2">Cargando...</div></div>
  </div>
</div>

<!-- TAB 3 -->
<div id="t3" class="tab-pane"><div class="card">
  <h2>Analisis 3 - Sub-Canastos Especiales: OPPS y PS</h2>
  <p class="nota">Universo = total DCF (sin MG Y TEXTIL). Que % de ventas/items del universo pertenece a cada sub-canasto.</p>
  <div class="cgrid">
    <div><h3>% Cobertura en Ventas: OPPS vs PS por Pais</h3><div class="cw"><canvas id="ch3"></canvas></div></div>
    <div class="ins" style="margin-top:28px">
      <strong>PS cubre aprox 2.5x mas que OPPS</strong><br>PS: 7-10% del universo por pais. OPPS: 2-6%. HN lidera en PS (10.48%), CR en OPPS (5.50%). SV menor en ambos.
    </div>
  </div>
  <h3>Detalle OPPS y PS por Pais</h3>
  <div class="tw"><table>
    <thead><tr><th>Sub-Canasto</th><th>Pais</th><th>Vtas Universo</th><th>Vtas Sub-Can</th>
      <th>% Cob Vtas</th><th>Items Universo</th><th>Items Sub-Can</th><th>% Cob Items</th></tr></thead>
    <tbody>{opps_ps_rows()}</tbody>
  </table></div>
</div></div>

<!-- TAB 4 -->
<div id="t4" class="tab-pane">
  <div class="card">
    <h2>Analisis 4 - Marcas Propias: MP_EXT, MP_INT y COLMENA (Universo = TIPO_MARCA='MP')</h2>
    <p class="nota">El universo es solo items con TIPO_MARCA='MP'. COLMENA viene de prcng_info_cam_MP_CANASTO_AGRUPACION.</p>
    <div class="cgrid">
      <div><h3>% Cob Ventas promedio por Pais (MP_EXT vs MP_INT vs COLMENA)</h3><div class="cw"><canvas id="ch4"></canvas></div></div>
      <div><h3>COLMENA especifico: % Cob Ventas e Items por Pais</h3><div class="cw"><canvas id="ch4col"></canvas></div></div>
    </div>
    <h3>Resumen MP_EXT / MP_INT / COLMENA por Pais (agregado)</h3>
    <div class="tw" style="margin-bottom:16px"><table>
      <thead><tr><th>Tipo</th><th>Pais</th><th>Vtas Universo MP</th><th>Vtas Sub-Can</th>
        <th>% Cob Vtas</th><th>Items Universo MP</th><th>Items Sub-Can</th><th>% Cob Items</th></tr></thead>
      <tbody>{colmena_pais_rows()}</tbody>
    </table></div>
  </div>
  <div class="card">
    <h2>Detalle por Pais + Formato + Division</h2>
    <div class="tc">
      <input id="srcA4" type="text" placeholder="Buscar...">
      {sel('fA4t', uniq(a4,'TIPO'), 'Todos los Tipos')}
      {sel('fA4p', uniq(a4,'PAIS'), 'Todos los Paises')}
      {sel('fA4f', uniq(a4,'FORMATO'), 'Todos los Formatos')}
      <button class="dl" id="tblA4_dl">Descargar CSV</button>
    </div>
    <div class="tw"><div id="tblA4">Cargando...</div></div>
  </div>
</div>

<!-- TAB 5 -->
<div id="t5" class="tab-pane"><div class="card">
  <h2>Analisis 5 - Chequeos vs Canasto (con Chequeos Nielsen incluidos)</h2>
  <p class="nota">CHEQUEOS = competidores CAM + Nielsen COD_SG 28500/45300/55100/109300/311000. Que % del canasto tiene precio chequeado.</p>
  <div class="cgrid">
    <div><h3>% Cob Ventas Chequeos vs Canasto por Pais</h3><div class="cw"><canvas id="ch5"></canvas></div></div>
    <div class="ins" style="margin-top:28px"><strong>Chequeos Nielsen mejoran la cobertura</strong><br>La inclusion de Nielsen incrementa la cobertura de chequeos especialmente en Frutas y Vegetales. Division Consumo sigue siendo la de menor cobertura relativa.</div>
  </div>
  <div class="tc">
    <input id="srcA5" type="text" placeholder="Buscar...">
    {sel('fA5p', uniq(a5,'PAIS'), 'Todos los Paises')}
    {sel('fA5f', uniq(a5,'FORMATO'), 'Todos los Formatos')}
    <button class="dl" id="tblA5_dl">Descargar CSV</button>
  </div>
  <div class="tw"><div id="tblA5">Cargando...</div></div>
</div></div>

<!-- TAB 6 -->
<div id="t6" class="tab-pane"><div class="card">
  <h2>Analisis 6 - Chequeos vs Universo Total (con Nielsen)</h2>
  <p class="nota">Del universo total, que fraccion tiene algun tipo de chequeo de precio registrado.</p>
  <div class="cgrid">
    <div><h3>% Cob Ventas Chequeos vs Universo por Pais</h3><div class="cw"><canvas id="ch6"></canvas></div></div>
    <div class="ins" style="margin-top:28px"><strong>Items con chequeo pero fuera del canasto</strong><br>Items del universo con chequeo que NO estan en el canasto son candidatos para incorporar. Especialmente en Division Consumo y Farmacia.</div>
  </div>
  <div class="tc">
    <input id="srcA6" type="text" placeholder="Buscar...">
    {sel('fA6p', uniq(a6,'PAIS'), 'Todos los Paises')}
    {sel('fA6f', uniq(a6,'FORMATO'), 'Todos los Formatos')}
    <button class="dl" id="tblA6_dl">Descargar CSV</button>
  </div>
  <div class="tw"><div id="tblA6">Cargando...</div></div>
</div></div>

<!-- TAB C -->
<div id="tC" class="tab-pane"><div class="card">
  <h2>Clasificacion del Canasto por TIER y Pais (% del universo)</h2>
  <p class="nota">Filas = Pais | % Vtas = que porcentaje del universo de ventas de ese pais cae en ese TIER | % Items = idem para items. Filas suman 100%. TIER 1/2/3 son el canasto; Sin Clas. = fuera del canasto.</p>
  <div class="cgrid">
    <div><h3>% Universo Ventas por Pais y TIER - 100% apilado</h3><div class="cw"><canvas id="chCv"></canvas></div></div>
    <div><h3>% Universo Items por Pais y TIER - 100% apilado</h3><div class="cw"><canvas id="chCi"></canvas></div></div>
  </div>
  <h3>Tabla Cruzada: % Composicion del Universo por Pais x TIER</h3>
  <div class="tw"><table>
    {clas_header()}
    <tbody>{clas_rows()}</tbody>
  </table></div>
  <div class="igrid" style="margin-top:14px">
    <div class="ins"><strong>CR concentra la mayor parte del TIER_1 regional</strong><br>CR aporta ~38% de las ventas TIER_1 de toda la region. Sin Clas. en CR: $65M (7.8% de sus ventas totales), pero solo 4.9% de sus items estan en TIER_1.</div>
    <div class="ins"><strong>SIN CLASIFICACION = $195M de oportunidad CAM</strong><br>55-64% de los items por pais estan fuera del canasto (Sin Clas. en items). En ventas representan 7-14% del universo. SV tiene la mayor brecha con 14.4% de ventas fuera.</div>
  </div>
</div></div>

</div>
<script>{cjs}</script>
<script>{JS}</script>
</body></html>"""


print("Generando HTML...", flush=True)
html = build()
with open(OUT,'w',encoding='utf-8') as f: f.write(html)
print(f"Reporte: {OUT} ({os.path.getsize(OUT)//1024} KB)", flush=True)
