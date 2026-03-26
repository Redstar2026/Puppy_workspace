"""Generador de graficas matplotlib para el reporte de precios CAM."""
import io, base64
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

matplotlib.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 9,
    'axes.spines.top': False, 'axes.spines.right': False,
    'axes.grid': True, 'grid.alpha': 0.3, 'figure.facecolor': 'white',
})

C_ES, C_FDS = '#0053e2', '#ffc220'
COLORS = [
    '#0053e2','#ea1100','#2a8703','#7c3aed','#f97316',
    '#10b981','#e11d48','#3b82f6','#84cc16','#f59e0b',
    '#06b6d4','#8b5cf6','#ec4899','#14b8a6','#a855f7',
    '#22c55e','#fb923c','#00b0b9','#ffc220','#374151',
]
MES_NAMES = {1:'Ene',2:'Feb',3:'Mar',4:'Abr',5:'May',6:'Jun',
             7:'Jul',8:'Ago',9:'Sep',10:'Oct',11:'Nov',12:'Dic'}


def mes_key(ano, mes):
    if ano == 2025: return mes          # 8..12
    if ano == 2026: return 12 + mes    # 13..15
    return ano * 100 + mes


def mes_label(ano, mes):
    return f"{MES_NAMES.get(mes, mes)} {str(ano)[2:]}"


def fig_to_b64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=80, facecolor='white')
    buf.seek(0)
    enc = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return enc


def as_df(records):
    df = pd.DataFrame(records)
    df['mes_key']   = df.apply(lambda r: mes_key(r['ano'], r['mes']), axis=1)
    df['mes_label'] = df.apply(lambda r: mes_label(r['ano'], r['mes']), axis=1)
    return df


def top_n(df, col, n=12, field='cnt_precio_normal'):
    return (df.groupby(col)[field].sum()
              .nlargest(n).index.tolist())


def fmt_axis(ax):
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{int(v):,}'))
    ax.set_axisbelow(True)


# ------------------------------------------------------------------
# TAB 1 – Conteos Semanales ES vs FdS
# ------------------------------------------------------------------
def chart_sw_bars(df1, field, title):
    """Grouped bar: ES vs FdS por semana cronologica."""
    df1 = df1.copy()
    df1['sw_key']   = df1['mes_key'] * 100 + df1['semana']
    df1['sw_label'] = df1.apply(lambda r: f"{r['mes_label']} W{int(r['semana'])}", axis=1)

    grp = df1.groupby(['sw_key','sw_label','segmento'])[field].sum().reset_index()
    weeks = grp[['sw_key','sw_label']].drop_duplicates().sort_values('sw_key')
    labels = weeks['sw_label'].tolist()
    x = np.arange(len(labels))
    w = 0.35

    es_vals  = [grp[(grp['sw_key']==k) & (grp['segmento']=='Entre Semana')][field].sum()
                for k in weeks['sw_key']]
    fds_vals = [grp[(grp['sw_key']==k) & (grp['segmento']=='Fin de Semana')][field].sum()
                for k in weeks['sw_key']]

    fig, ax = plt.subplots(figsize=(max(14, len(labels)*0.5), 5))
    ax.bar(x - w/2, es_vals,  w, label='Entre Semana', color=C_ES,  alpha=0.88)
    ax.bar(x + w/2, fds_vals, w, label='Fin de Semana', color=C_FDS, alpha=0.88)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=65, ha='right', fontsize=7.5)
    ax.set_ylabel('Conteo')
    ax.legend()
    fmt_axis(ax)
    fig.tight_layout()
    return fig_to_b64(fig)


# ------------------------------------------------------------------
# TAB 2 – Tendencia Diaria
# ------------------------------------------------------------------
DIAS = ['Lunes','Martes','Miercoles','Jueves','Viernes','Sabado','Domingo']
DIA_COLORS = [C_ES]*4 + [C_FDS]*3


def chart_daily_bar(df1, field, title):
    vals = [df1[df1['dia_semana']==d][field].sum() for d in DIAS]
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(DIAS, vals, color=DIA_COLORS, alpha=0.88, edgecolor='white', linewidth=0.5)
    mx = max(vals) if vals else 1
    for b, v in zip(bars, vals):
        if v > 0:
            ax.text(b.get_x()+b.get_width()/2, b.get_height()+mx*0.01,
                    f'{int(v):,}', ha='center', va='bottom', fontsize=8, fontweight='bold')
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_ylabel('Conteo')
    fmt_axis(ax)
    legend = [mpatches.Patch(color=C_ES,  label='Entre Semana (Lun-Jue)'),
              mpatches.Patch(color=C_FDS, label='Fin de Semana (Vie-Dom)')]
    ax.legend(handles=legend)
    fig.tight_layout()
    return fig_to_b64(fig)


def chart_daily_pie(df1):
    es  = df1[df1['segmento']=='Entre Semana']['cnt_precio_normal'].sum()
    fds = df1[df1['segmento']=='Fin de Semana']['cnt_precio_normal'].sum()
    if es + fds == 0:
        es, fds = 1, 0
    fig, ax = plt.subplots(figsize=(5, 5))
    wedges, texts, autotexts = ax.pie(
        [es, fds], labels=['Entre Semana','Fin de Semana'],
        colors=[C_ES, C_FDS], autopct='%1.1f%%', startangle=90,
        wedgeprops={'edgecolor':'white','linewidth':2}
    )
    for t in autotexts: t.set_fontsize(11); t.set_fontweight('bold')
    ax.set_title('Distribucion ES vs FdS\n(Precio Normal)', fontsize=11, fontweight='bold')
    fig.tight_layout()
    return fig_to_b64(fig)


# ------------------------------------------------------------------
# TAB 3 – Por Mes/Pais/Competidor
# ------------------------------------------------------------------
def chart_monthly_lines(df3, field, title, n_comp=10):
    """Line chart ES (solido) vs FdS (discontinuo) por competidor."""
    comps   = top_n(df3, 'competidor', n_comp, field)
    periodos = df3[['mes_key','mes_label']].drop_duplicates().sort_values('mes_key')
    labels   = periodos['mes_label'].tolist()
    keys     = periodos['mes_key'].tolist()

    fig, ax = plt.subplots(figsize=(14, 6))
    for i, comp in enumerate(comps):
        c = COLORS[i % len(COLORS)]
        sub = df3[df3['competidor']==comp]
        es_vals  = [sub[(sub['mes_key']==k) & (sub['segmento']=='Entre Semana')][field].sum() for k in keys]
        fds_vals = [sub[(sub['mes_key']==k) & (sub['segmento']=='Fin de Semana')][field].sum() for k in keys]
        ax.plot(labels, es_vals,  color=c, linestyle='-',  linewidth=2,   marker='o', markersize=5, label=f'{comp} ES')
        ax.plot(labels, fds_vals, color=c, linestyle='--', linewidth=1.5, marker='s', markersize=4, label=f'{comp} FdS', alpha=0.7)
    ax.set_title(title + '\n(linea solida=ES, discontinua=FdS)', fontsize=11, fontweight='bold')
    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)
    ax.set_ylabel('Conteo')
    fmt_axis(ax)
    ax.legend(fontsize=7, ncol=2, loc='upper left', bbox_to_anchor=(1.01, 1))
    fig.tight_layout()
    return fig_to_b64(fig)


# ------------------------------------------------------------------
# TAB 4 – Caida FdS
# ------------------------------------------------------------------
def chart_caida_fds_lines(df3, field, title, n_comp=15):
    """Lineas de conteo FdS por mes para cada competidor."""
    comps   = top_n(df3, 'competidor', n_comp, field)
    periodos = df3[['mes_key','mes_label']].drop_duplicates().sort_values('mes_key')
    labels   = periodos['mes_label'].tolist()
    keys     = periodos['mes_key'].tolist()

    fig, ax = plt.subplots(figsize=(14, 6))
    for i, comp in enumerate(comps):
        c = COLORS[i % len(COLORS)]
        sub = df3[(df3['competidor']==comp) & (df3['segmento']=='Fin de Semana')]
        vals = [sub[sub['mes_key']==k][field].sum() for k in keys]
        ax.plot(labels, vals, color=c, linewidth=2, marker='o', markersize=5, label=comp)
    ax.set_title(title, fontsize=11, fontweight='bold')
    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)
    ax.set_ylabel('Conteo Registros FdS')
    fmt_axis(ax)
    ax.legend(fontsize=7, ncol=2, loc='upper left', bbox_to_anchor=(1.01, 1))
    fig.tight_layout()
    return fig_to_b64(fig)


# ------------------------------------------------------------------
# TAB 5 – Deltas MoM
# ------------------------------------------------------------------
def chart_mom_trend(df3, field, title, n_comp=8):
    """Lineas mensuales ES+FdS combinados para ver tendencia global."""
    comps   = top_n(df3, 'competidor', n_comp, field)
    periodos = df3[['mes_key','mes_label']].drop_duplicates().sort_values('mes_key')
    labels   = periodos['mes_label'].tolist()
    keys     = periodos['mes_key'].tolist()

    fig, ax = plt.subplots(figsize=(13, 5))
    for i, comp in enumerate(comps):
        c = COLORS[i % len(COLORS)]
        sub = df3[df3['competidor']==comp]
        vals = [sub[sub['mes_key']==k][field].sum() for k in keys]
        ax.plot(labels, vals, color=c, linewidth=2, marker='o', markersize=5, label=comp)
    ax.set_title(title, fontsize=11, fontweight='bold')
    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)
    ax.set_ylabel('Conteo Total (ES+FdS)')
    fmt_axis(ax)
    ax.legend(fontsize=8, loc='upper left', bbox_to_anchor=(1.01, 1))
    fig.tight_layout()
    return fig_to_b64(fig)


# ------------------------------------------------------------------
# TAB 6 – Tendencias por Pais y Competidor
# ------------------------------------------------------------------
def chart_trend_by_pais(df3, pais, seg_filter, field, title, n_comp=8):
    """Curvas de comportamiento por competidor para un pais dado."""
    sub = df3[df3['pais']==pais].copy() if pais != 'TODOS' else df3.copy()
    if seg_filter == 'es':  sub = sub[sub['segmento']=='Entre Semana']
    elif seg_filter == 'fds': sub = sub[sub['segmento']=='Fin de Semana']

    comps   = top_n(sub, 'competidor', n_comp, field)
    periodos = sub[['mes_key','mes_label']].drop_duplicates().sort_values('mes_key')
    labels   = periodos['mes_label'].tolist()
    keys     = periodos['mes_key'].tolist()

    fig, ax = plt.subplots(figsize=(12, 5))
    for i, comp in enumerate(comps):
        c = COLORS[i % len(COLORS)]
        csub = sub[sub['competidor']==comp]
        vals = [csub[csub['mes_key']==k][field].sum() for k in keys]
        ax.plot(labels, vals, color=c, linewidth=2, marker='o', markersize=5, label=comp)
    ax.set_title(title, fontsize=11, fontweight='bold')
    if labels:
        ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)
    ax.set_ylabel('Conteo')
    fmt_axis(ax)
    ax.legend(fontsize=8, loc='upper left', bbox_to_anchor=(1.01, 1))
    fig.tight_layout()
    return fig_to_b64(fig)


# ------------------------------------------------------------------
# TAB 7 – Categorias por Pais
# ------------------------------------------------------------------
def chart_cat_lines(df5, pais, seg_filter, field, title, n_cat=8):
    """Lineas de categorias por mes para un pais."""
    sub = df5[df5['pais']==pais].copy() if pais != 'TODOS' else df5.copy()
    if seg_filter == 'es':  sub = sub[sub['segmento']=='Entre Semana']
    elif seg_filter == 'fds': sub = sub[sub['segmento']=='Fin de Semana']

    # Clean categories
    sub = sub[~sub['categoria'].isin(['SIN CANASTO','','3','1','SIN SUBCANASTO','nan'])]
    sub = sub[sub['categoria'].notna()]
    if sub.empty:
        sub = df5[df5['pais']==pais] if pais != 'TODOS' else df5.copy()

    cats    = top_n(sub, 'categoria', n_cat, field)
    periodos = sub[['mes_key','mes_label']].drop_duplicates().sort_values('mes_key')
    labels   = periodos['mes_label'].tolist()
    keys     = periodos['mes_key'].tolist()

    fig, ax = plt.subplots(figsize=(12, 5))
    for i, cat in enumerate(cats):
        c = COLORS[i % len(COLORS)]
        csub = sub[sub['categoria']==cat]
        vals = [csub[csub['mes_key']==k][field].sum() for k in keys]
        ax.plot(labels, vals, color=c, linewidth=2, marker='o', markersize=5, label=cat)
    ax.set_title(title, fontsize=11, fontweight='bold')
    if labels:
        ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)
    ax.set_ylabel('Conteo')
    fmt_axis(ax)
    ax.legend(fontsize=8, loc='upper left', bbox_to_anchor=(1.01, 1))
    fig.tight_layout()
    return fig_to_b64(fig)


def chart_cat_stacked_pais(df5, seg_filter, field, title, n_cat=8):
    """Barras apiladas: categorias por pais."""
    sub = df5.copy()
    if seg_filter == 'es':  sub = sub[sub['segmento']=='Entre Semana']
    elif seg_filter == 'fds': sub = sub[sub['segmento']=='Fin de Semana']
    sub = sub[~sub['categoria'].isin(['SIN CANASTO','','3','1','SIN SUBCANASTO','nan'])]
    sub = sub[sub['categoria'].notna()]
    if sub.empty: sub = df5.copy()

    cats   = top_n(sub, 'categoria', n_cat, field)
    paises = sorted(sub['pais'].unique())
    x      = np.arange(len(paises))
    bottom = np.zeros(len(paises))

    fig, ax = plt.subplots(figsize=(10, 5))
    for i, cat in enumerate(cats):
        c = COLORS[i % len(COLORS)]
        vals = [sub[(sub['pais']==p) & (sub['categoria']==cat)][field].sum() for p in paises]
        ax.bar(x, vals, bottom=bottom, color=c, alpha=0.85, label=cat)
        bottom += np.array(vals, dtype=float)
    ax.set_title(title, fontsize=11, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(paises)
    ax.set_ylabel('Conteo')
    fmt_axis(ax)
    ax.legend(fontsize=8, loc='upper left', bbox_to_anchor=(1.01, 1))
    fig.tight_layout()
    return fig_to_b64(fig)
