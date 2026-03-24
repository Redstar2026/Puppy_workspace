"""CSS styles para el dashboard ejecutivo PGMB."""


def get_css():
    return """
    :root {
      --blue:    #0053e2;
      --blue2:   #003db5;
      --blue3:   #00256e;
      --spark:   #ffc220;
      --spark2:  #e6a800;
      --red:     #ea1100;
      --green:   #2a8703;
      --gray10:  #f4f6fb;
      --gray50:  #cbd5e0;
      --gray160: #1d2633;
      --white:   #ffffff;
    }
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html { scroll-behavior: smooth; }
    body {
      font-family: 'Segoe UI', Arial, sans-serif;
      background: var(--gray10);
      color: var(--gray160);
      min-height: 100vh;
    }

    /* ===== HEADER ===== */
    .topbar {
      background: linear-gradient(135deg, var(--blue3) 0%, var(--blue) 60%, #1a6fff 100%);
      color: var(--white);
      padding: 0 32px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      height: 64px;
      position: sticky;
      top: 0;
      z-index: 100;
      box-shadow: 0 2px 12px rgba(0,0,0,.25);
    }
    .topbar-brand { display: flex; align-items: center; gap: 12px; }
    .spark-icon {
      background: var(--spark);
      color: var(--blue3);
      font-weight: 900;
      font-size: 1.1rem;
      width: 36px; height: 36px;
      border-radius: 8px;
      display: flex; align-items: center; justify-content: center;
    }
    .topbar-title { font-size: 1.1rem; font-weight: 700; letter-spacing: .3px; }
    .topbar-sub { font-size: .78rem; opacity: .75; margin-top: 1px; }
    .topbar-badge {
      background: rgba(255,255,255,.15);
      border: 1px solid rgba(255,255,255,.3);
      border-radius: 20px;
      padding: 4px 14px;
      font-size: .8rem;
      font-weight: 600;
    }

    /* ===== HERO ===== */
    .hero {
      background: linear-gradient(160deg, var(--blue3) 0%, var(--blue) 100%);
      color: var(--white);
      padding: 40px 32px 32px;
    }
    .hero-title { font-size: 1.6rem; font-weight: 800; margin-bottom: 6px; }
    .hero-sub { font-size: .95rem; opacity: .8; margin-bottom: 28px; }
    .hero-kpis { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
    .hero-kpi {
      background: rgba(255,255,255,.1);
      border: 1px solid rgba(255,255,255,.2);
      border-radius: 14px;
      padding: 20px 18px;
      backdrop-filter: blur(4px);
      transition: transform .2s;
    }
    .hero-kpi:hover { transform: translateY(-3px); }
    .hero-kpi-icon { font-size: 1.6rem; margin-bottom: 8px; }
    .hero-kpi-label { font-size: .75rem; opacity: .75; text-transform: uppercase; letter-spacing: .5px; margin-bottom: 4px; }
    .hero-kpi-val { font-size: 2rem; font-weight: 900; line-height: 1; }
    .hero-kpi-pct { font-size: .82rem; opacity: .75; margin-top: 4px; }
    .hero-kpi.green { border-color: rgba(42,135,3,.5); background: rgba(42,135,3,.18); }
    .hero-kpi.red   { border-color: rgba(234,17,0,.5); background: rgba(234,17,0,.18); }
    .hero-kpi.spark { border-color: rgba(255,194,32,.4); background: rgba(255,194,32,.15); }

    /* ===== FILTERS ===== */
    .filter-bar {
      background: var(--white);
      border-bottom: 2px solid var(--blue);
      padding: 12px 32px;
      display: flex;
      align-items: center;
      gap: 18px;
      flex-wrap: wrap;
      position: sticky;
      top: 64px;
      z-index: 90;
      box-shadow: 0 2px 8px rgba(0,0,0,.07);
    }
    .filter-label { font-size: .78rem; font-weight: 700; color: var(--blue); text-transform: uppercase; letter-spacing: .4px; }
    .filter-bar select {
      padding: 6px 12px;
      border: 1.5px solid var(--gray50);
      border-radius: 8px;
      font-size: .88rem;
      color: var(--gray160);
      background: var(--white);
      min-width: 170px;
      cursor: pointer;
      transition: border-color .2s;
    }
    .filter-bar select:focus { outline: none; border-color: var(--blue); }
    .btn-reset {
      padding: 6px 16px;
      background: var(--blue);
      color: var(--white);
      border: none;
      border-radius: 8px;
      font-size: .85rem;
      font-weight: 700;
      cursor: pointer;
      transition: background .2s;
    }
    .btn-reset:hover { background: var(--blue2); }

    /* ===== MAIN LAYOUT ===== */
    .main { max-width: 1600px; margin: 0 auto; padding: 28px 24px; }
    .section-title {
      font-size: 1.05rem;
      font-weight: 800;
      color: var(--blue3);
      margin-bottom: 18px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .section-title::after {
      content: '';
      flex: 1;
      height: 2px;
      background: linear-gradient(90deg, var(--blue) 0%, transparent 100%);
      margin-left: 8px;
    }

    /* ===== NAV TABS ===== */
    .nav-tabs {
      display: flex;
      gap: 4px;
      margin-bottom: 24px;
      background: var(--white);
      padding: 6px;
      border-radius: 12px;
      box-shadow: 0 1px 6px rgba(0,0,0,.08);
      width: fit-content;
    }
    .nav-tab {
      padding: 9px 22px;
      border: none;
      border-radius: 8px;
      font-size: .9rem;
      font-weight: 600;
      cursor: pointer;
      color: #555;
      background: transparent;
      transition: all .2s;
    }
    .nav-tab:hover { background: var(--gray10); color: var(--blue); }
    .nav-tab.active { background: var(--blue); color: var(--white); box-shadow: 0 2px 8px rgba(0,83,226,.3); }
    .tab-panel { display: none; }
    .tab-panel.active { display: block; }

    /* ===== CARDS ===== */
    .card {
      background: var(--white);
      border-radius: 14px;
      padding: 22px;
      box-shadow: 0 2px 10px rgba(0,0,0,.07);
      margin-bottom: 22px;
    }
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 22px; }
    .grid-3 { display: grid; grid-template-columns: repeat(3,1fr); gap: 16px; margin-bottom: 22px; }

    /* ===== COUNTRY SCORECARDS ===== */
    .country-grid { display: grid; grid-template-columns: repeat(5,1fr); gap: 14px; margin-bottom: 22px; }
    .country-card {
      background: var(--white);
      border-radius: 12px;
      padding: 16px;
      box-shadow: 0 2px 8px rgba(0,0,0,.08);
      border-top: 4px solid var(--blue);
      transition: transform .2s;
    }
    .country-card:hover { transform: translateY(-4px); }
    .country-name { font-size: 1rem; font-weight: 800; color: var(--blue3); margin-bottom: 8px; }
    .cc-row-head { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 4px; margin-bottom: 4px; }
    .cc-head-comp { font-size:.7rem; font-weight:800; color: var(--blue); text-align:right; text-transform:uppercase; }
    .cc-head-wm   { font-size:.7rem; font-weight:800; color: #555;        text-align:right; text-transform:uppercase; }
    .cc-row { display: grid; grid-template-columns: 1fr 1fr 1fr; gap:4px; margin-bottom:5px; align-items:center; }
    .cc-lbl { font-size:.78rem; color: #666; }
    .cc-row span:not(.cc-lbl) { font-size:.8rem; font-weight:700; text-align:right; }
    .cc-row small { font-size:.68rem; font-weight:400; color:#888; }
    .cs-bajo   { color: var(--green) !important; }
    .cs-subio  { color: var(--red)   !important; }
    .cs-spark  { color: var(--spark2)!important; }

    /* ===== DONUT WRAP ===== */
    .donut-wrap { height: 280px; position: relative; }
    .chart-wrap  { height: 320px; }
    .chart-wrap-lg { height: 420px; }
    .chart-title { font-size: .9rem; font-weight: 700; color: var(--gray160); margin-bottom: 12px; text-align: center; }

    /* ===== TABLE ===== */
    .tbl-scroll { overflow-x: auto; max-height: 450px; overflow-y: auto; }
    table { width: 100%; border-collapse: collapse; font-size: .83rem; }
    thead { position: sticky; top: 0; z-index: 2; }
    thead th {
      background: var(--blue);
      color: var(--white);
      padding: 10px 10px;
      text-align: left;
      white-space: nowrap;
      cursor: pointer;
      user-select: none;
    }
    thead th:hover { background: var(--blue2); }
    thead th.num { text-align: right; }
    tbody tr:nth-child(even) { background: var(--gray10); }
    tbody tr:hover { background: #dce8ff; }
    tbody td { padding: 7px 10px; border-bottom: 1px solid #edf0f7; white-space: nowrap; }
    tbody td.num { text-align: right; }
    .badge {
      display: inline-block;
      padding: 2px 10px;
      border-radius: 12px;
      font-size: .75rem;
      font-weight: 700;
    }
    .badge-bajo    { background: #d4edda; color: #155724; }
    .badge-subio   { background: #f8d7da; color: #721c24; }
    .badge-mant    { background: #d6d8d9; color: #383d41; }
    .badge-nuevo   { background: #fff3cd; color: #856404; }
    .neg { color: var(--red);   font-weight: 700; }
    .pos { color: var(--green); font-weight: 700; }
    .fw  { font-weight: 700; }

    /* ===== INSIGHT BOX ===== */
    .insight-bar {
      display: flex;
      gap: 14px;
      flex-wrap: wrap;
      margin-bottom: 22px;
    }
    .insight-pill {
      background: var(--white);
      border-left: 4px solid var(--blue);
      border-radius: 0 10px 10px 0;
      padding: 12px 18px;
      flex: 1;
      min-width: 220px;
      box-shadow: 0 1px 6px rgba(0,0,0,.07);
      font-size: .87rem;
      line-height: 1.5;
    }
    .insight-pill.warn { border-color: var(--red); }
    .insight-pill.good { border-color: var(--green); }
    .insight-pill.neutral { border-color: var(--spark2); }
    .insight-pill strong { display: block; margin-bottom: 2px; font-size: .8rem; text-transform: uppercase; color: #888; letter-spacing: .4px; }

    .btn-excel {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 8px 18px;
      background: #1d6f42;
      color: #fff;
      border: none;
      border-radius: 8px;
      font-size: .88rem;
      font-weight: 700;
      cursor: pointer;
      transition: background .2s;
      white-space: nowrap;
    }
    .btn-excel:hover { background: #155233; }
    .btn-excel:active { transform: scale(.97); }

    /* ===== FOOTER ===== */
    .footer {
      text-align: center;
      font-size: .75rem;
      color: #aaa;
      padding: 20px;
      border-top: 1px solid var(--gray50);
      margin-top: 20px;
    }

    @media(max-width:1100px) {
      .hero-kpis { grid-template-columns: repeat(2,1fr); }
      .country-grid { grid-template-columns: repeat(3,1fr); }
      .grid-2 { grid-template-columns: 1fr; }
    }
    @media(max-width:700px) {
      .hero-kpis { grid-template-columns: 1fr 1fr; }
      .country-grid { grid-template-columns: repeat(2,1fr); }
      .hero { padding: 24px 16px; }
    }
    """
