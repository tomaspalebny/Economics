import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.set_page_config(page_title="Smenarna - Realny kurz & PPP", layout="wide")
st.title("💱 Směnárna – Reálný kurz & PPP")

# ========== BASKET WITH WEIGHTS ==========
BASKET_DEFAULTS = [
    ("Chleb 1 kg",          "🍞", 38,    1.80,  6.0),
    ("Pivo 0.5 L",          "🍺", 25,    3.50,  4.0),
    ("Benzin 1 L",          "⛽", 38,    1.65,  8.0),
    ("Espresso",            "☕", 65,    2.80,  3.0),
    ("Big Mac",             "🍔", 109,   4.65,  5.0),
    ("iPhone 16",           "📱", 27990, 1099., 5.0),
    ("MHD mesicnik",        "🚌", 550,   49.0, 10.0),
    ("Najem 2+kk mesic",    "🏠", 18000, 950., 25.0),
    ("Elektrina 100 kWh",   "⚡", 650,   35.0, 12.0),
    ("Mleko 1 L",           "🥛", 24,    1.15,  4.0),
    ("Jizdenka vlak 100km", "🚆", 180,   15.0,  6.0),
    ("Kino listek",         "🎬", 220,   12.0,  3.0),
    ("Pansky strih",        "💈", 350,   22.0,  4.0),
    ("Pizza Margherita",    "🍕", 160,   9.50,  5.0),
]

BASE_E = 25.10

# ========== PRESETS ==========
PRESETS = [
    dict(
        key="baseline",
        name="Vychozi stav (bez soku)",
        icon="📌",
        desc_event="Zadna zmena - zakladni kalibrace modelu na aktualni ceny a kurz 25,10 CZK/EUR.",
        desc_domestic="Ceny v CR odpovidaji bezne cenove hladine.",
        desc_foreign="Ceny v eurozone odpovidaji bezne cenove hladine.",
        desc_nominal="Nominalni kurz je stabilni kolem 25,10 CZK/EUR.",
        desc_real="Realny kurz Q ukazuje, zda je CR cenove drazsi nebo levnejsi nez EU.",
        desc_ppp="PPP kurz porovnava cenove hladiny obou ekonomik.",
        E=25.10, p_cz_mult=1.0, p_eu_mult=1.0,
    ),
    dict(
        key="cnb_hike_2022",
        name="CNB zvysila sazby 2022 (na 7 %)",
        icon="🏦",
        desc_event="V roce 2022 CNB agresivne zvysila urokove sazby z 0,25 % na 7 % jako reakci na inflaci. Vyssi sazby prilakaly zahranicni kapital, poptavka po CZK rostla.",
        desc_domestic="Ceske ceny stale rostly setrvacnosti (inflace ~15 %), ale rust se postupne zpomaloval diky vyssim sazbam.",
        desc_foreign="Eurozona mela nizsi inflaci (~8 %), ECB reagovala pomaleji, cenovy diferencial se zvysil.",
        desc_nominal="CZK posilila (kurz klesl z ~25,5 na ~24,2 CZK/EUR). Kapitalove toky do CR kvuli urokovemu diferencialu.",
        desc_real="Realny kurz CZK vyrazne posilil - kombinace silnejsi CZK + vyssi ceske ceny. CR se stala relativne drazsi.",
        desc_ppp="PPP kurz vzrostl (ceske ceny rostly rychleji), zatimco nominalni kurz klesal, CZK se realne nadhodnotila.",
        E=24.20, p_cz_mult=1.15, p_eu_mult=1.08,
    ),
    dict(
        key="ecb_easing_2024",
        name="ECB snizila sazby 2024",
        icon="🇪🇺",
        desc_event="ECB zahajila v cervnu 2024 cyklus snizovani sazeb. EUR oslabilo vuci rade men. CNB zustala na vyssich sazbch.",
        desc_domestic="Ceska inflace se vratila k cili (~2,5 %), ceny rostly mirne.",
        desc_foreign="V eurozone inflace klesla pod 2,5 %, ceny se stabilizovaly.",
        desc_nominal="CZK mirne posilila (z ~25,3 na ~25,0 CZK/EUR), protoze urokovy diferencial favorizoval CZK.",
        desc_real="Realny kurz se prilis nezmenil - mirne posileni CZK bylo kompenzovano podobnymi cenovymi trendy.",
        desc_ppp="PPP kurz zustal temer stabilni diky vyrovnane inflaci v obou ekonomikach.",
        E=25.00, p_cz_mult=1.025, p_eu_mult=1.02,
    ),
    dict(
        key="energy_crisis_2022",
        name="Energeticka krize 2022",
        icon="🛢️",
        desc_event="Ruska invaze na Ukrajinu vyvolala prudky rust cen energii. Cena plynu v Evrope vzrostla 10x (TTF hub). CR jako dovozce energii byla silne zasazena.",
        desc_domestic="Ceske ceny energii explodovaly (+80 % elektrina, +60 % plyn). Preneslo se do potravin, dopravy, sluzeb. Celkova inflace ~16 %.",
        desc_foreign="Eurozona zasazena take, ale mene rovnomerne (Francie - jadro, Nemecko - plyn). Prumerna inflace EU ~9 %.",
        desc_nominal="CZK mirne oslabila (kurz ~24,7 na ~25,3) kvuli nejistote a blizkosti konfliktu.",
        desc_real="CR se stala vyrazne drazsi relativne k EU - ceske ceny rostly rychleji, ale CZK neoslabila dostatecne.",
        desc_ppp="PPP kurz prudce vzrostl (cenovy kos CR zdrazil vice), ale nominalni kurz nereagoval proporcionalne.",
        E=25.30, p_cz_mult=1.16, p_eu_mult=1.09,
    ),
    dict(
        key="tourism_boom",
        name="Turisticky boom v Praze 2023",
        icon="🏖️",
        desc_event="Rekordni navstevnost Prahy (8+ mil. turistu rocne). Turiste smenuji EUR/USD na CZK, rostou ceny sluzeb v centru.",
        desc_domestic="Zdrazily hlavne sluzby: restaurace, ubytovani, doprava v Praze (+5-10 %). Potraviny a zbozi stabilni.",
        desc_foreign="Ceny v eurozone stabilni, bez vyrazneho tlaku z turismu.",
        desc_nominal="CZK mirne posilila (turiste kupuji CZK). Kurz klesl z ~25,2 na ~24,9.",
        desc_real="Realny kurz posilil - CZK nominalne silnejsi + ceske ceny sluzeb vyssi. Praha se stala drazsi pro turisty.",
        desc_ppp="PPP kurz vzrostl (ceske ceny nahoru), nominalni kurz klesl, CZK realne nadhodnocena.",
        E=24.90, p_cz_mult=1.03, p_eu_mult=1.00,
    ),
    dict(
        key="eu_recession",
        name="Recese v eurozone 2023",
        icon="📉",
        desc_event="Nemecko v technicke recesi, prumyslova produkce EU klesa. Klesaji objednavky ceskeho exportu (auta, dily).",
        desc_domestic="Ceske ceny stabilni, ale poptavka klesa. Mirna deflace prumyslovych vstupu.",
        desc_foreign="V EU mirny pokles cen prumyslovych vyrobku, sluzby drahe. Inflace ~3 %.",
        desc_nominal="CZK oslabila (z ~24,8 na ~25,5 CZK/EUR) - nizsi export = nizsi poptavka po CZK.",
        desc_real="Slabsi CZK kompenzovala stabilni ceny, realny kurz se prilis nezmenil.",
        desc_ppp="PPP kurz mirne klesl (ceske ceny stabilni, EU ceny mirne nahoru).",
        E=25.50, p_cz_mult=1.00, p_eu_mult=1.03,
    ),
    dict(
        key="cnb_intervention_2013",
        name="Devizove intervence CNB 2013-2017",
        icon="🏦",
        desc_event="CNB zavedla kurzovy zavazek 27 CZK/EUR (nakupovala eura, tiskla koruny). Cil: zabranit deflaci a podporit export.",
        desc_domestic="Ceske ceny zacaly mirne rust (cil splnen - odvracena deflace). Inflace ~1-2 %.",
        desc_foreign="Eurozona bojovala s nizkou inflaci (~0,5 %), ECB zavedla QE.",
        desc_nominal="Kurz skocil z ~25,5 na 27,0 CZK/EUR - umele oslabena CZK.",
        desc_real="CZK realne vyrazne oslabila - ceske zbozi se stalo levnejsim pro zahranicni kupce. Export vzrostl.",
        desc_ppp="PPP kurz zustal kolem ~22-23 CZK/EUR, ale nominalni kurz byl 27, CZK vyrazne podhodnocena.",
        E=27.00, p_cz_mult=1.02, p_eu_mult=1.005,
    ),
    dict(
        key="balassa_samuelson",
        name="Balassuv-Samuelsonuv efekt (konvergence)",
        icon="🎓",
        desc_event="CR jako konvergujici ekonomika ma rostouci produktivitu v prumyslu, rostou mzdy, rostou ceny sluzeb. Dlouhodoby strukturalni trend.",
        desc_domestic="Ceske ceny sluzeb rostou rychleji nez ceny zbozi. Cenova hladina CR se priblizuje EU (~75 % na 80 % EU).",
        desc_foreign="Ceny v EU rostou stabilnim tempem (~2 %).",
        desc_nominal="CZK dlouhodobe posiluje (z ~30 v 2004 na ~25 v 2024). Odrazi rust produktivity.",
        desc_real="CZK realne posiluje - kombinace nominalniho posileni + vyssi ceske inflace. CR konverguje cenove k EU.",
        desc_ppp="PPP kurz roste (ceske ceny rostou rychleji), ale nominalni kurz posiluje jeste rychleji, CZK se priblizuje spravne hodnote.",
        E=24.50, p_cz_mult=1.04, p_eu_mult=1.02,
    ),
    dict(
        key="geopolitical_2022",
        name="Geopoliticka krize - Ukrajina 2022",
        icon="⚔️",
        desc_event="Ruska invaze vyvolala utek kapitalu z regionu CEE. Investori preferovali bezpecne meny (USD, CHF). CZK jako mala otevrena ekonomika pod tlakem.",
        desc_domestic="Ceske ceny raketove rostly (+15-18 %) - energie, potraviny, stavebni material.",
        desc_foreign="EU ceny rostly (+8-10 %), ale mene nez v CR diky vetsi diverzifikaci.",
        desc_nominal="CZK prudce oslabila (z ~24,3 na ~25,5), pak se stabilizovala diky intervencim CNB a vyssim sazbam.",
        desc_real="Realny kurz nejprve posilil (ceske ceny rostly rychleji nez CZK oslabila), pak se stabilizoval.",
        desc_ppp="PPP kurz vyrazne vzrostl (ceske ceny nahoru o 15 %), nominalni kurz reagoval jen zcasti.",
        E=25.50, p_cz_mult=1.15, p_eu_mult=1.09,
    ),
]

# ========== FUNCTIONS ==========
def calc_weighted(prices_czk, prices_eur, weights, E):
    w = np.array(weights)
    w_norm = w / w.sum() if w.sum() > 0 else w
    p_czk = np.array(prices_czk)
    p_eur = np.array(prices_eur)
    basket_czk = float(np.dot(p_czk, w_norm))
    basket_eur = float(np.dot(p_eur, w_norm))
    ppp = basket_czk / basket_eur if basket_eur > 0 else E
    Q = (E * basket_eur) / basket_czk if basket_czk > 0 else 1
    overval = (ppp - E) / E * 100 if E > 0 else 0
    return dict(
        basket_czk=basket_czk, basket_eur=basket_eur,
        ppp=ppp, Q=Q, overval=overval,
        prices_czk=p_czk.tolist(), prices_eur=p_eur.tolist(),
        weights=w_norm.tolist(),
    )

def fmt_rate(e, is_direct):
    return f"{e:.2f} CZK/EUR" if is_direct else f"{1/e:.4f} EUR/CZK"

def render_basket_table(r, E, weights, container):
    tbl = []
    for i, it in enumerate(BASKET_DEFAULTS):
        czk_p = r["prices_czk"][i]
        eur_p = r["prices_eur"][i]
        conv = eur_p * E
        diff = (conv - czk_p) / czk_p * 100 if czk_p > 0 else 0
        w_str = f"{weights[i]:.1f} %" if weights is not None else ""
        tbl.append({
            "Polozka": f"{it[1]} {it[0]}",
            "Vaha": w_str,
            "Cena CZK": f"{czk_p:,.0f} Kc",
            "Cena EUR": f"{eur_p:,.2f} EUR",
            f"Prevod CZK (E={E:.2f})": f"{conv:,.0f} Kc",
            "Rozdil": f"{diff:+.1f} %",
            "Levneji v": "🇨🇿" if czk_p < conv else "🇪🇺",
        })
    container.dataframe(pd.DataFrame(tbl), use_container_width=True, hide_index=True)

def render_bar_chart(r, E, container, chart_key="bar"):
    names = [f"{it[1]} {it[0]}" for it in BASKET_DEFAULTS]
    pct_diff = []
    for i in range(len(BASKET_DEFAULTS)):
        czk = r["prices_czk"][i]
        conv = r["prices_eur"][i] * E
        pct_diff.append((conv - czk) / czk * 100 if czk > 0 else 0)
    colors = ["#6366f1" if d > 0 else "#ef4444" for d in pct_diff]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=names, y=pct_diff, marker_color=colors,
        text=[f"{d:+.1f} %" for d in pct_diff], textposition="outside"))
    fig.add_hline(y=0, line_color="white", line_width=1)
    fig.update_layout(height=380,
        yaxis=dict(title="O kolik % je CR levnejsi (+) / drazsi (-)", gridcolor="rgba(100,100,100,0.2)"),
        xaxis=dict(tickangle=-30),
        plot_bgcolor="rgba(15,23,42,0.5)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"), margin=dict(t=30, b=80), showlegend=False)
    container.plotly_chart(fig, use_container_width=True, key=chart_key)
    container.caption("🔵 Kladne = v CR levneji | 🔴 Zaporne = v CR drazsi")

def render_gauge(r, container, chart_key="gauge"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta", value=r["Q"],
        delta={"reference": 1.0, "position": "bottom"},
        gauge=dict(axis=dict(range=[0.7, 1.3], tickcolor="#1a1a2e"),
            bar=dict(color="#f59e0b"),
            steps=[dict(range=[0.7, 0.95], color="rgba(239,68,68,0.3)"),
                   dict(range=[0.95, 1.05], color="rgba(34,197,94,0.3)"),
                   dict(range=[1.05, 1.3], color="rgba(99,102,241,0.3)")],
            threshold=dict(line=dict(color="#22c55e", width=3), value=1.0)),
        title=dict(text="Q (1.0 = PPP)", font=dict(size=14, color="#1a1a2e")),
        number=dict(font=dict(color="#1a1a2e")),
        delta_font=dict(color="#1a1a2e")))
    fig.update_layout(height=260, paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#1a1a2e"), margin=dict(t=60, b=10))
    container.plotly_chart(fig, use_container_width=True, key=chart_key)
    container.caption("🔴 Q < 0.95: CZK nadhodnocena | 🟢 Q ~ 1: PPP | 🔵 Q > 1.05: CZK podhodnocena")

def render_weight_pie(weights, container, chart_key="pie"):
    names = [f"{it[1]} {it[0]}" for it in BASKET_DEFAULTS]
    fig = go.Figure(go.Pie(labels=names, values=weights, hole=0.35,
        textinfo="label+percent", textposition="outside",
        textfont=dict(color="#1a1a2e", size=12),
        marker=dict(colors=["#6366f1","#f59e0b","#ef4444","#22c55e","#8b5cf6",
                            "#ec4899","#14b8a6","#f97316","#06b6d4","#84cc16",
                            "#a855f7","#e11d48","#0ea5e9","#eab308"])))
    fig.update_layout(height=380, paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#1a1a2e"),
        margin=dict(t=20, b=20, l=20, r=20), showlegend=False)
    container.plotly_chart(fig, use_container_width=True, key=chart_key)

def render_formulas(r, E, is_direct, container):
    ppp = r["ppp"]
    Q = r["Q"]
    if r["weights"] is not None:
        container.markdown("**Vazeny kos:** $P = \\sum w_i \\cdot p_i$")
    if is_direct:
        container.latex(rf"Q = \frac{{E \times P^*}}{{P}} = \frac{{{E:.2f} \times {r['basket_eur']:,.2f}}}{{{r['basket_czk']:,.2f}}} = {Q:.3f}")
        container.latex(rf"E_{{PPP}} = \frac{{P}}{{P^*}} = \frac{{{r['basket_czk']:,.2f}}}{{{r['basket_eur']:,.2f}}} = {ppp:.2f} \text{{ CZK/EUR}}")
    else:
        container.latex(rf"Q = \frac{{P^*}}{{E \times P}} = \frac{{{r['basket_eur']:,.2f}}}{{{(1/E):.4f} \times {r['basket_czk']:,.2f}}} = {Q:.3f}")
        container.latex(rf"E_{{PPP}} = \frac{{P^*}}{{P}} = \frac{{{r['basket_eur']:,.2f}}}{{{r['basket_czk']:,.2f}}} = {1/ppp:.4f} \text{{ EUR/CZK}}")
    container.markdown("Q < 1: CZK nadhodnocena | Q > 1: CZK podhodnocena | Q = 1: PPP")

# ========== TABS ==========
tab_presets, tab_sandbox = st.tabs(["📚 Scenare (presety)", "🔬 Piskoviste"])

# ================================================================
# TAB 1: PRESETS
# ================================================================
with tab_presets:
    st.subheader("📚 Scenare z realne ekonomiky")
    st.markdown("Vyberte ekonomickou udalost a sledujte, co se stalo s cenami doma, v zahranici, s nominalnim kurzem a jaky to melo dusledek na realny kurz a PPP.")

    preset_names = [f"{p['icon']} {p['name']}" for p in PRESETS]
    selected_idx = st.selectbox("Vyberte scenar:", range(len(PRESETS)),
        format_func=lambda i: preset_names[i], key="preset_sel")
    preset = PRESETS[selected_idx]

    # Detect preset change and reset slider values via on_change
    if "prev_preset_idx" not in st.session_state:
        st.session_state.prev_preset_idx = selected_idx
        st.session_state.pr_E = float(preset["E"])
        st.session_state.pr_pcz = float(preset["p_cz_mult"])
        st.session_state.pr_peu = float(preset["p_eu_mult"])
    if st.session_state.prev_preset_idx != selected_idx:
        st.session_state.prev_preset_idx = selected_idx
        st.session_state.pr_E = float(preset["E"])
        st.session_state.pr_pcz = float(preset["p_cz_mult"])
        st.session_state.pr_peu = float(preset["p_eu_mult"])
        for i, it in enumerate(BASKET_DEFAULTS):
            if f"prc_{i}" in st.session_state:
                st.session_state[f"prc_{i}"] = float(round(it[2] * preset["p_cz_mult"], 1))
            if f"pre_{i}" in st.session_state:
                st.session_state[f"pre_{i}"] = float(round(it[3] * preset["p_eu_mult"], 2))
        st.rerun()

    st.markdown("---")

    # Event description
    st.markdown(f"### {preset['icon']} {preset['name']}")
    st.info(f"**Udalost:** {preset['desc_event']}")

    col_dom, col_for = st.columns(2)
    with col_dom:
        st.markdown("#### 🇨🇿 Dopad na ceske ceny")
        st.warning(preset["desc_domestic"])
    with col_for:
        st.markdown("#### 🇪🇺 Dopad na zahranicni ceny")
        st.warning(preset["desc_foreign"])

    col_nom, col_real, col_ppp = st.columns(3)
    with col_nom:
        st.markdown("#### 💱 Nominalni kurz")
        st.success(preset["desc_nominal"])
    with col_real:
        st.markdown("#### 📊 Realny kurz")
        st.error(preset["desc_real"])
    with col_ppp:
        st.markdown("#### ⚖️ PPP kurz")
        st.error(preset["desc_ppp"])

    st.markdown("---")

    # Adjustable parameters
    st.markdown("### ⚙️ Parametry scenare (upravitelne)")
    st.markdown("Hodnoty jsou prednastaveny podle scenare, ale muzete je libovolne menit.")

    pr_quot = st.radio("Kotace", ["Prima (CZK/EUR)", "Neprima (EUR/CZK)"], key="pr_quot", horizontal=True)
    pr_direct = pr_quot.startswith("Prima")

    pc1, pc2, pc3 = st.columns(3)
    with pc1:
        pr_E = st.slider("Nominalni kurz (CZK/EUR)", 15.0, 40.0, step=0.05, key="pr_E",
            help="Kolik CZK zaplatite za 1 EUR")
        if not pr_direct:
            st.caption(f"= {1/pr_E:.4f} EUR/CZK")
    with pc2:
        pr_pcz = st.slider("Cenovy multiplikator CR", 0.80, 1.30, step=0.005, key="pr_pcz",
            format="%.3f", help="1.0 = zakladni ceny, 1.10 = +10 % inflace")
    with pc3:
        pr_peu = st.slider("Cenovy multiplikator EU", 0.80, 1.30, step=0.005, key="pr_peu",
            format="%.3f", help="1.0 = zakladni ceny, 1.05 = +5 % inflace")

    # Weights
    st.markdown("---")
    st.markdown("### 🎯 Vahy polozek v kosi")
    use_custom_weights = st.checkbox("Upravit vahy rucne", key="pr_cw")

    weights_raw = []
    if use_custom_weights:
        wcols = st.columns(7)
        for i, it in enumerate(BASKET_DEFAULTS):
            with wcols[i % 7]:
                w = st.number_input(f"{it[1]} {it[0]}", 0.0, 100.0, it[4], 0.5,
                    key=f"prw_{i}", format="%.1f")
                weights_raw.append(w)
        wsum = sum(weights_raw)
        if abs(wsum - 100) > 0.5:
            st.warning(f"Soucet vah = {wsum:.1f} % (bude normalizovano na 100 %)")
    else:
        weights_raw = [it[4] for it in BASKET_DEFAULTS]

    # Individual prices
    st.markdown("---")
    use_custom_prices = st.checkbox("Upravit jednotlive ceny rucne", key="pr_cp")

    prices_czk = []
    prices_eur = []
    if use_custom_prices:
        st.markdown("#### Ceny v CR (CZK) a EU (EUR)")
        for i, it in enumerate(BASKET_DEFAULTS):
            cc1, cc2 = st.columns(2)
            with cc1:
                p = st.number_input(f"{it[1]} {it[0]} - CZK", 0.0, 100000.0,
                    float(round(it[2] * preset["p_cz_mult"], 1)), key=f"prc_{i}")
                prices_czk.append(p)
            with cc2:
                p = st.number_input(f"{it[1]} {it[0]} - EUR", 0.0, 10000.0,
                    float(round(it[3] * preset["p_eu_mult"], 2)), 0.01, key=f"pre_{i}", format="%.2f")
                prices_eur.append(p)
    else:
        prices_czk = [it[2] * pr_pcz for it in BASKET_DEFAULTS]
        prices_eur = [it[3] * pr_peu for it in BASKET_DEFAULTS]

    # Calculate
    r = calc_weighted(prices_czk, prices_eur, weights_raw, pr_E)
    base_czk = [it[2] for it in BASKET_DEFAULTS]
    base_eur = [it[3] for it in BASKET_DEFAULTS]
    r_base = calc_weighted(base_czk, base_eur, weights_raw, BASE_E)

    # Results
    st.markdown("---")
    st.markdown("### 📊 Vysledky")

    mc = st.columns(5)
    mc[0].metric("Nominalni kurz", fmt_rate(pr_E, pr_direct),
        delta=f"{pr_E - BASE_E:+.2f} vs zaklad", delta_color="inverse")
    mc[1].metric("Vazeny kos CR", f"{r['basket_czk']:,.2f} Kc",
        delta=f"{(r['basket_czk']/r_base['basket_czk']-1)*100:+.1f} %")
    mc[2].metric("Vazeny kos EU", f"{r['basket_eur']:,.2f} EUR",
        delta=f"{(r['basket_eur']/r_base['basket_eur']-1)*100:+.1f} %")
    mc[3].metric("Realny kurz Q", f"{r['Q']:.3f}",
        delta=f"{r['Q']-1:+.3f} vs PPP")
    mc[4].metric("PPP kurz", fmt_rate(r['ppp'], pr_direct),
        delta=f"{r['overval']:+.1f} % nadhodnoceni")

    if r["Q"] < 0.95:
        st.error(f"🔴 **CZK je nadhodnocena** (Q = {r['Q']:.3f}). Cesky kos je relativne drahy. Export ztraci konkurenceschopnost.")
    elif r["Q"] > 1.05:
        st.info(f"🔵 **CZK je podhodnocena** (Q = {r['Q']:.3f}). Cesky kos je relativne levny. Export je konkurenceschopny.")
    else:
        st.success(f"🟢 **Kurz je blizko PPP** (Q = {r['Q']:.3f}). Cenove hladiny jsou priblizne v rovnovaze.")

    # Charts
    st.markdown("---")
    col_tbl, col_pie = st.columns([3, 1])
    with col_tbl:
        st.markdown("#### Spotrebni kos - detaily")
        render_basket_table(r, pr_E, weights_raw, st)
    with col_pie:
        st.markdown("#### Struktura vah")
        render_weight_pie(weights_raw, st, chart_key="pie_preset")

    col_bar, col_gauge = st.columns([2, 1])
    with col_bar:
        st.markdown("#### Cenove srovnani CR vs EU")
        render_bar_chart(r, pr_E, st, chart_key="bar_preset")
    with col_gauge:
        st.markdown("#### Realny kurz Q")
        render_gauge(r, st, chart_key="gauge_preset")

    with st.expander("📐 Vzorce s dosazenymi hodnotami"):
        render_formulas(r, pr_E, pr_direct, st)

    # Sensitivity
    st.markdown("---")
    st.markdown("### 📈 Citlivostni analyza")
    e_range = np.linspace(max(15, pr_E - 5), min(40, pr_E + 5), 60)
    q_base_line = [(e * r["basket_eur"]) / r["basket_czk"] for e in e_range]
    p_hi = [p * 1.03 for p in prices_czk]
    r_hi = calc_weighted(p_hi, prices_eur, weights_raw, pr_E)
    q_hi = [(e * r_hi["basket_eur"]) / r_hi["basket_czk"] for e in e_range]
    p_lo = [p * 0.97 for p in prices_czk]
    r_lo = calc_weighted(p_lo, prices_eur, weights_raw, pr_E)
    q_lo = [(e * r_lo["basket_eur"]) / r_lo["basket_czk"] for e in e_range]

    fig_sens = go.Figure()
    fig_sens.add_trace(go.Scatter(x=e_range, y=q_lo, mode="lines", name="CR inflace -3 %", line=dict(color="#22c55e", width=2, dash="dash")))
    fig_sens.add_trace(go.Scatter(x=e_range, y=q_base_line, mode="lines", name="Aktualni cen. hladina", line=dict(color="#f59e0b", width=3)))
    fig_sens.add_trace(go.Scatter(x=e_range, y=q_hi, mode="lines", name="CR inflace +3 %", line=dict(color="#ef4444", width=2, dash="dash")))
    fig_sens.add_hline(y=1.0, line_color="white", line_width=1, line_dash="dot", annotation_text="PPP (Q=1)")
    fig_sens.add_vline(x=pr_E, line_color="rgba(255,255,255,0.3)", line_dash="dot", annotation_text=f"E={pr_E:.2f}")
    fig_sens.update_layout(height=350,
        xaxis=dict(title="Nominalni kurz CZK/EUR", gridcolor="rgba(100,100,100,0.2)"),
        yaxis=dict(title="Realny kurz Q", gridcolor="rgba(100,100,100,0.2)", range=[0.6, 1.4]),
        plot_bgcolor="rgba(15,23,42,0.5)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"), legend=dict(orientation="h", y=1.1), margin=dict(t=40, b=40))
    st.plotly_chart(fig_sens, use_container_width=True, key="sens_preset")

# ================================================================
# TAB 2: SANDBOX
# ================================================================
with tab_sandbox:
    st.subheader("🔬 Piskoviste - plna kontrola nad vsemi parametry")
    st.markdown("Mente nominalni kurz, cenove hladiny, vahy i jednotlive ceny. Sledujte dopad na kos, realny kurz a PPP.")

    sb_quot = st.radio("Kotace", ["Prima (CZK/EUR)", "Neprima (EUR/CZK)"], key="sb_quot", horizontal=True)
    sb_direct = sb_quot.startswith("Prima")

    st.markdown("---")
    st.markdown("### Hlavni parametry")
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        sb_E = st.slider("Nominalni kurz (CZK/EUR)", 15.0, 40.0, BASE_E, 0.05, key="sb_E")
        if not sb_direct:
            st.caption(f"= {1/sb_E:.4f} EUR/CZK")
    with sc2:
        sb_pcz = st.slider("Cenova hladina CR (index)", 70.0, 160.0, 100.0, 0.5, key="sb_pcz",
            help="100 = zakladni ceny")
    with sc3:
        sb_peu = st.slider("Cenova hladina EU (index)", 70.0, 160.0, 100.0, 0.5, key="sb_peu",
            help="100 = zakladni ceny")

    sb_Pcz = sb_pcz / 100
    sb_Peu = sb_peu / 100

    # Weights
    st.markdown("---")
    st.markdown("### 🎯 Vahy v kosi")
    sb_custom_w = st.checkbox("Upravit vahy", key="sb_cw")
    sb_weights = []
    if sb_custom_w:
        swcols = st.columns(7)
        for i, it in enumerate(BASKET_DEFAULTS):
            with swcols[i % 7]:
                w = st.number_input(f"{it[1]}", 0.0, 100.0, it[4], 0.5, key=f"sbw_{i}", format="%.1f")
                sb_weights.append(w)
        swsum = sum(sb_weights)
        if abs(swsum - 100) > 0.5:
            st.warning(f"Soucet vah = {swsum:.1f} % (bude normalizovano)")
    else:
        sb_weights = [it[4] for it in BASKET_DEFAULTS]

    # Individual prices
    st.markdown("---")
    sb_custom_p = st.checkbox("Upravit jednotlive ceny", key="sb_cp")
    sb_prices_czk = []
    sb_prices_eur = []
    if sb_custom_p:
        st.markdown("#### Ceny polozek")
        for i, it in enumerate(BASKET_DEFAULTS):
            cc1, cc2 = st.columns(2)
            with cc1:
                p = st.number_input(f"{it[1]} {it[0]} CZK", 0.0, 100000.0,
                    float(round(it[2] * sb_Pcz, 1)), key=f"sbc_{i}")
                sb_prices_czk.append(p)
            with cc2:
                p = st.number_input(f"{it[1]} {it[0]} EUR", 0.0, 10000.0,
                    float(round(it[3] * sb_Peu, 2)), 0.01, key=f"sbe_{i}", format="%.2f")
                sb_prices_eur.append(p)
    else:
        sb_prices_czk = [it[2] * sb_Pcz for it in BASKET_DEFAULTS]
        sb_prices_eur = [it[3] * sb_Peu for it in BASKET_DEFAULTS]

    sb_r = calc_weighted(sb_prices_czk, sb_prices_eur, sb_weights, sb_E)
    sb_r_base = calc_weighted([it[2] for it in BASKET_DEFAULTS], [it[3] for it in BASKET_DEFAULTS], sb_weights, BASE_E)

    # Short vs Long run
    st.markdown("---")
    st.markdown("### Kratkodobe vs. dlouhodobe dopady")
    lr_E = sb_r["ppp"]
    lr_r = calc_weighted(sb_prices_czk, sb_prices_eur, sb_weights, lr_E)

    col_sr, col_lr = st.columns(2)
    with col_sr:
        st.markdown("#### ⏱️ Kratke obdobi")
        m1, m2, m3 = st.columns(3)
        m1.metric("Nom. kurz", fmt_rate(sb_E, sb_direct))
        m2.metric("Realny kurz Q", f"{sb_r['Q']:.3f}")
        m3.metric("Nadhodnoceni CZK", f"{sb_r['overval']:+.1f} %")
        if sb_r["Q"] < 0.95:
            st.error(f"CZK **nadhodnocena** o {-sb_r['overval']:.1f} %. Export trpi.")
        elif sb_r["Q"] > 1.05:
            st.info(f"CZK **podhodnocena** o {sb_r['overval']:.1f} %. Export prosperuje.")
        else:
            st.success("Kurz blizko PPP. Rovnovaha.")

    with col_lr:
        st.markdown("#### 🕰️ Dlouhe obdobi")
        m1, m2, m3 = st.columns(3)
        m1.metric("PPP kurz", fmt_rate(lr_E, sb_direct))
        m2.metric("Realny kurz Q", f"{lr_r['Q']:.3f}")
        m3.metric("Nadhodnoceni", f"{lr_r['overval']:+.1f} %")
        if abs(sb_E - lr_E) > 0.5:
            direction = "posili (E klesa)" if sb_E > lr_E else "oslabi (E roste)"
            st.warning(f"PPP predpovida, ze CZK **{direction}** smerem k {lr_E:.2f} CZK/EUR.")

    # Results
    st.markdown("---")
    st.markdown("### 📊 Vysledky")
    mc = st.columns(5)
    mc[0].metric("Nominalni kurz", fmt_rate(sb_E, sb_direct))
    mc[1].metric("Vazeny kos CR", f"{sb_r['basket_czk']:,.2f} Kc",
        delta=f"{(sb_r['basket_czk']/sb_r_base['basket_czk']-1)*100:+.1f} %")
    mc[2].metric("Vazeny kos EU", f"{sb_r['basket_eur']:,.2f} EUR",
        delta=f"{(sb_r['basket_eur']/sb_r_base['basket_eur']-1)*100:+.1f} %")
    mc[3].metric("Realny kurz Q", f"{sb_r['Q']:.3f}")
    mc[4].metric("PPP kurz", fmt_rate(sb_r['ppp'], sb_direct))

    st.markdown("---")
    col_tbl2, col_pie2 = st.columns([3, 1])
    with col_tbl2:
        st.markdown("#### Spotrebni kos")
        render_basket_table(sb_r, sb_E, sb_weights, st)
    with col_pie2:
        st.markdown("#### Struktura vah")
        render_weight_pie(sb_weights, st, chart_key="pie_sandbox")

    col_bar2, col_gauge2 = st.columns([2, 1])
    with col_bar2:
        render_bar_chart(sb_r, sb_E, st, chart_key="bar_sandbox")
    with col_gauge2:
        render_gauge(sb_r, st, chart_key="gauge_sandbox")

    with st.expander("📐 Vzorce"):
        render_formulas(sb_r, sb_E, sb_direct, st)

    # Sensitivity
    st.markdown("---")
    st.markdown("### 📈 Citlivostni analyza")
    se_range = np.linspace(max(15, sb_E - 5), min(40, sb_E + 5), 60)
    sq_base = [(e * sb_r["basket_eur"]) / sb_r["basket_czk"] for e in se_range]
    sp_hi = [p * 1.03 for p in sb_prices_czk]
    sr_hi = calc_weighted(sp_hi, sb_prices_eur, sb_weights, sb_E)
    sq_hi = [(e * sr_hi["basket_eur"]) / sr_hi["basket_czk"] for e in se_range]
    sp_lo = [p * 0.97 for p in sb_prices_czk]
    sr_lo = calc_weighted(sp_lo, sb_prices_eur, sb_weights, sb_E)
    sq_lo = [(e * sr_lo["basket_eur"]) / sr_lo["basket_czk"] for e in se_range]

    sfig = go.Figure()
    sfig.add_trace(go.Scatter(x=se_range, y=sq_lo, mode="lines", name="CR -3 %", line=dict(color="#22c55e", width=2, dash="dash")))
    sfig.add_trace(go.Scatter(x=se_range, y=sq_base, mode="lines", name="Aktualni", line=dict(color="#f59e0b", width=3)))
    sfig.add_trace(go.Scatter(x=se_range, y=sq_hi, mode="lines", name="CR +3 %", line=dict(color="#ef4444", width=2, dash="dash")))
    sfig.add_hline(y=1.0, line_color="white", line_width=1, line_dash="dot", annotation_text="PPP")
    sfig.add_vline(x=sb_E, line_color="rgba(255,255,255,0.3)", line_dash="dot", annotation_text=f"E={sb_E:.2f}")
    sfig.update_layout(height=350,
        xaxis=dict(title="Nom. kurz CZK/EUR", gridcolor="rgba(100,100,100,0.2)"),
        yaxis=dict(title="Q", gridcolor="rgba(100,100,100,0.2)", range=[0.6, 1.4]),
        plot_bgcolor="rgba(15,23,42,0.5)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"), legend=dict(orientation="h", y=1.1), margin=dict(t=40, b=40))
    st.plotly_chart(sfig, use_container_width=True, key="sens_sandbox")

st.markdown("---")
st.caption("Zjednoduseny model pro vyukove ucely. Ceny jsou priblizne, realny kurz je v praxi ovlivnen mnoha dalsimi faktory.")
