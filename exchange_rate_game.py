import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.set_page_config(page_title="Směnárna – Reálný kurz & PPP", layout="wide")
st.title("💱 Směnárna – Reálný kurz & PPP")

# ========== BASKET WITH WEIGHTS ==========
# (name, icon, base_czk, base_eur, default_weight_pct)
BASKET_DEFAULTS = [
    ("Chléb 1 kg",          "🍞", 38,    1.80,  6.0),
    ("Pivo 0.5 L",          "🍺", 25,    3.50,  4.0),
    ("Benzín 1 L",          "⛽", 38,    1.65,  8.0),
    ("Espresso",            "☕", 65,    2.80,  3.0),
    ("Big Mac",             "🍔", 109,   4.65,  5.0),
    ("iPhone 16",           "📱", 27990, 1099., 5.0),
    ("MHD měsíčník",        "🚌", 550,   49.0, 10.0),
    ("Nájem 2+kk měsíc",    "🏠", 18000, 950., 25.0),
    ("Elektřina 100 kWh",   "⚡", 650,   35.0, 12.0),
    ("Mléko 1 L",           "🥛", 24,    1.15,  4.0),
    ("Jízdenka vlak 100 km","🚆", 180,   15.0,  6.0),
    ("Kino lístek",         "🎬", 220,   12.0,  3.0),
    ("Pánský střih",        "💈", 350,   22.0,  4.0),
    ("Pizza Margherita",    "🍕", 160,   9.50,  5.0),
]

BASE_E = 25.10

# ========== PRESETS (real-event based) ==========
PRESETS = [
    dict(
        key="baseline",
        name="📌 Výchozí stav (bez šoku)",
        desc_event="Žádná změna – základní kalibrace modelu na aktuální ceny a kurz 25,10 CZK/EUR.",
        desc_domestic="Ceny v ČR odpovídají běžné cenové hladině.",
        desc_foreign="Ceny v eurozóně odpovídají běžné cenové hladině.",
        desc_nominal="Nominální kurz je stabilní kolem 25,10 CZK/EUR.",
        desc_real="Reálný kurz Q ukazuje, zda je ČR cenově dražší nebo levnější než EU.",
        desc_ppp="PPP kurz porovnává cenové hladiny obou ekonomik.",
        E=25.10, p_cz_mult=1.0, p_eu_mult=1.0,
    ),
    dict(
        key="cnb_hike_2022",
        name="🏦 ČNB zvýšila sazby 2022 (na 7 %)",
        desc_event="V roce 2022 ČNB agresivně zvýšila úrokové sazby z 0,25 % na 7 % jako reakci na inflaci. Vyšší sazby přilákaly zahraniční kapitál → poptávka po CZK rostla.",
        desc_domestic="České ceny stále rostly setrvačností (inflace ~15 %), ale růst se postupně zpomaloval díky vyšším sazbám.",
        desc_foreign="Eurozóna měla nižší inflaci (~8 %), ECB reagovala pomaleji → cenový diferenciál se zvýšil.",
        desc_nominal="CZK posílila (kurz klesl z ~25,5 na ~24,2 CZK/EUR). Kapitálové toky do ČR kvůli úrokovému diferenciálu.",
        desc_real="Reálný kurz CZK výrazně posílil – kombinace silnější CZK + vyšší české ceny. ČR se stala relativně dražší.",
        desc_ppp="PPP kurz vzrostl (české ceny rostly rychleji), zatímco nominální kurz klesal → CZK se reálně nadhodnotila.",
        E=24.20, p_cz_mult=1.15, p_eu_mult=1.08,
    ),
    dict(
        key="ecb_easing_2024",
        name="🇪🇺 ECB snížila sazby 2024",
        desc_event="ECB zahájila v červnu 2024 cyklus snižování sazeb. EUR oslabilo vůči řadě měn. ČNB zůstala na vyšších sazbách.",
        desc_domestic="Česká inflace se vrátila k cíli (~2,5 %), ceny rostly mírně.",
        desc_foreign="V eurozóně inflace klesla pod 2,5 %, ceny se stabilizovaly.",
        desc_nominal="CZK mírně posílila (z ~25,3 na ~25,0 CZK/EUR), protože úrokový diferenciál favorizoval CZK.",
        desc_real="Reálný kurz se příliš nezměnil – mírné posílení CZK bylo kompenzováno podobnými cenovými trendy.",
        desc_ppp="PPP kurz zůstal téměř stabilní díky vyrovnané inflaci v obou ekonomikách.",
        E=25.00, p_cz_mult=1.025, p_eu_mult=1.02,
    ),
    dict(
        key="energy_crisis_2022",
        name="🛢️ Energetická krize 2022",
        desc_event="Ruská invaze na Ukrajinu vyvolala prudký růst cen energií. Cena plynu v Evropě vzrostla 10× (TTF hub). ČR jako dovozce energií byla silně zasažena.",
        desc_domestic="České ceny energií explodovaly (+80 % elektřina, +60 % plyn). Přeneslo se do potravin, dopravy, služeb. Celková inflace ~16 %.",
        desc_foreign="Eurozóna zasažena také, ale méně rovnoměrně (Francie – jádro, Německo – plyn). Průměrná inflace EU ~9 %.",
        desc_nominal="CZK mírně oslabila (kurz ~24,7 → ~25,3) kvůli nejistotě a blízkosti konfliktu.",
        desc_real="ČR se stala výrazně dražší relativně k EU – české ceny rostly rychleji, ale CZK neoslabila dostatečně.",
        desc_ppp="PPP kurz prudce vzrostl (cenový koš ČR zdražil více), ale nominální kurz nereagoval proporcionálně.",
        E=25.30, p_cz_mult=1.16, p_eu_mult=1.09,
    ),
    dict(
        key="tourism_boom",
        name="🏖️ Turistický boom v Praze 2023",
        desc_event="Rekordní návštěvnost Prahy (8+ mil. turistů ročně). Turisté směňují EUR/USD → CZK, rostou ceny služeb v centru.",
        desc_domestic="Zdražily hlavně služby: restaurace, ubytování, doprava v Praze (+5–10 %). Potraviny a zboží stabilní.",
        desc_foreign="Ceny v eurozóně stabilní, bez výrazného tlaku z turismu.",
        desc_nominal="CZK mírně posílila (turisti kupují CZK). Kurz klesl z ~25,2 na ~24,9.",
        desc_real="Reálný kurz posílil – CZK nominálně silnější + české ceny služeb vyšší. Praha se stala dražší pro turisty.",
        desc_ppp="PPP kurz vzrostl (české ceny nahoru), nominální kurz klesl → CZK reálně nadhodnocená.",
        E=24.90, p_cz_mult=1.03, p_eu_mult=1.00,
    ),
    dict(
        key="eu_recession",
        name="📉 Recese v eurozóně 2023",
        desc_event="Německo v technické recesi, průmyslová produkce EU klesá. Klesají objednávky českého exportu (auta, díly).",
        desc_domestic="České ceny stabilní, ale poptávka klesá. Mírná deflace průmyslových vstupů.",
        desc_foreign="V EU mírný pokles cen průmyslových výrobků, služby drahé. Inflace ~3 %.",
        desc_nominal="CZK oslabila (z ~24,8 na ~25,5 CZK/EUR) – nižší export = nižší poptávka po CZK.",
        desc_real="Slabší CZK kompenzovala stabilní ceny → reálný kurz se příliš nezměnil.",
        desc_ppp="PPP kurz mírně klesl (české ceny stabilní, EU ceny mírně nahoru).",
        E=25.50, p_cz_mult=1.00, p_eu_mult=1.03,
    ),
    dict(
        key="cnb_intervention_2013",
        name="🏦 Devizové intervence ČNB 2013–2017",
        desc_event="ČNB zavedla kurzový závazek 27 CZK/EUR (nakupovala eura, tiskla koruny). Cíl: zabránit deflaci a podpořit export.",
        desc_domestic="České ceny začaly mírně růst (cíl splněn – odvrácena deflace). Inflace ~1–2 %.",
        desc_foreign="Eurozóna bojovala s nízkou inflací (~0,5 %), ECB zavedla QE.",
        desc_nominal="Kurz skočil z ~25,5 na 27,0 CZK/EUR – uměle oslabená CZK.",
        desc_real="CZK reálně výrazně oslabila – české zboží se stalo levnějším pro zahraniční kupce. Export vzrostl.",
        desc_ppp="PPP kurz zůstal kolem ~22–23 CZK/EUR, ale nominální kurz byl 27 → CZK výrazně podhodnocená.",
        E=27.00, p_cz_mult=1.02, p_eu_mult=1.005,
    ),
    dict(
        key="balassa_samuelson",
        name="🎓 Balassův-Samuelsonův efekt (konvergence)",
        desc_event="ČR jako konvergující ekonomika má rostoucí produktivitu v průmyslu → rostou mzdy → rostou ceny služeb. Dlouhodobý strukturální trend.",
        desc_domestic="České ceny služeb rostou rychleji než ceny zboží. Cenová hladina ČR se přibližuje EU (~75 % → 80 % EU).",
        desc_foreign="Ceny v EU rostou stabilním tempem (~2 %).",
        desc_nominal="CZK dlouhodobě posiluje (z ~30 v 2004 na ~25 v 2024). Odráží růst produktivity.",
        desc_real="CZK reálně posiluje – kombinace nominálního posílení + vyšší české inflace. ČR konverguje cenově k EU.",
        desc_ppp="PPP kurz roste (české ceny rostou rychleji), ale nominální kurz posiluje ještě rychleji → CZK se přibližuje paritní hodnotě.",
        E=24.50, p_cz_mult=1.04, p_eu_mult=1.02,
    ),
    dict(
        key="geopolitical_2022",
        name="⚔️ Geopolitická krize – Ukrajina 2022",
        desc_event="Ruská invaze vyvolala útěk kapitálu z regionu CEE. Investoři preferovali bezpečné měny (USD, CHF). CZK jako malá otevřená ekonomika pod tlakem.",
        desc_domestic="České ceny raketově rostly (+15–18 %) – energie, potraviny, stavební materiál.",
        desc_foreign="EU ceny rostly (+8–10 %), ale méně než v ČR díky větší diverzifikaci.",
        desc_nominal="CZK prudce oslabila (z ~24,3 na ~25,5), pak se stabilizovala díky intervencím ČNB a vyšším sazbám.",
        desc_real="Reálný kurz nejprve posílil (české ceny rostly rychleji než CZK oslabila), pak se stabilizoval.",
        desc_ppp="PPP kurz výrazně vzrostl (české ceny nahoru o 15 %), nominální kurz reagoval jen zčásti.",
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

def calc_unweighted(prices_czk, prices_eur, E):
    basket_czk = sum(prices_czk)
    basket_eur = sum(prices_eur)
    ppp = basket_czk / basket_eur if basket_eur > 0 else E
    Q = (E * basket_eur) / basket_czk if basket_czk > 0 else 1
    overval = (ppp - E) / E * 100 if E > 0 else 0
    return dict(
        basket_czk=basket_czk, basket_eur=basket_eur,
        ppp=ppp, Q=Q, overval=overval,
        prices_czk=list(prices_czk), prices_eur=list(prices_eur),
        weights=None,
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
            "Položka": f"{it[1]} {it[0]}",
            "Váha": w_str,
            "Cena CZK": f"{czk_p:,.0f} Kč",
            "Cena EUR": f"{eur_p:,.2f} €",
            f"Převod CZK (E={E:.2f})": f"{conv:,.0f} Kč",
            "Rozdíl": f"{diff:+.1f} %",
            "Levněji v": "🇨🇿" if czk_p < conv else "🇪🇺",
        })
    container.dataframe(pd.DataFrame(tbl), use_container_width=True, hide_index=True)

def render_bar_chart(r, E, container):
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
        yaxis=dict(title="O kolik % je ČR levnější (+) / dražší (-)", gridcolor="rgba(100,100,100,0.2)"),
        xaxis=dict(tickangle=-30),
        plot_bgcolor="rgba(15,23,42,0.5)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"), margin=dict(t=30, b=80), showlegend=False)
    container.plotly_chart(fig, use_container_width=True)
    container.caption("🔵 Kladné = v ČR levněji | 🔴 Záporné = v ČR dražší")

def render_gauge(r, container):
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta", value=r["Q"],
        delta={"reference": 1.0, "position": "bottom"},
        gauge=dict(axis=dict(range=[0.7, 1.3], tickcolor="#e2e8f0"),
            bar=dict(color="#f59e0b"),
            steps=[dict(range=[0.7, 0.95], color="rgba(239,68,68,0.2)"),
                   dict(range=[0.95, 1.05], color="rgba(34,197,94,0.2)"),
                   dict(range=[1.05, 1.3], color="rgba(99,102,241,0.2)")],
            threshold=dict(line=dict(color="#22c55e", width=3), value=1.0)),
        title=dict(text="Q (1.0 = PPP)", font=dict(size=14))))
    fig.update_layout(height=260, paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#e2e8f0"), margin=dict(t=60, b=10))
    container.plotly_chart(fig, use_container_width=True)
    container.caption("🔴 Q < 0.95: CZK nadhodnocena | 🟢 Q ≈ 1: PPP | 🔵 Q > 1.05: CZK podhodnocena")

def render_formulas(r, E, is_direct, container):
    ppp = r["ppp"]
    Q = r["Q"]
    if r["weights"] is not None:
        container.markdown("**Vážený koš:** $P = \\sum w_i \\cdot p_i$")
    if is_direct:
        container.latex(rf"Q = \frac{{E \times P^*}}{{P}} = \frac{{{E:.2f} \times {r['basket_eur']:,.2f}}}{{{r['basket_czk']:,.2f}}} = {Q:.3f}")
        container.latex(rf"E_{{PPP}} = \frac{{P}}{{P^*}} = \frac{{{r['basket_czk']:,.2f}}}{{{r['basket_eur']:,.2f}}} = {ppp:.2f} \text{{ CZK/EUR}}")
    else:
        container.latex(rf"Q = \frac{{P^*}}{{E \times P}} = \frac{{{r['basket_eur']:,.2f}}}{{{(1/E):.4f} \times {r['basket_czk']:,.2f}}} = {Q:.3f}")
        container.latex(rf"E_{{PPP}} = \frac{{P^*}}{{P}} = \frac{{{r['basket_eur']:,.2f}}}{{{r['basket_czk']:,.2f}}} = {1/ppp:.4f} \text{{ EUR/CZK}}")
    container.markdown("Q < 1 → CZK nadhodnocena | Q > 1 → CZK podhodnocena | Q = 1 → PPP platí")

def render_weight_pie(weights, container):
    names = [f"{it[1]} {it[0]}" for it in BASKET_DEFAULTS]
    fig = go.Figure(go.Pie(labels=names, values=weights, hole=0.35,
        textinfo="label+percent", textposition="outside",
        marker=dict(colors=["#6366f1","#f59e0b","#ef4444","#22c55e","#8b5cf6",
                            "#ec4899","#14b8a6","#f97316","#06b6d4","#84cc16",
                            "#a855f7","#e11d48","#0ea5e9","#eab308"])))
    fig.update_layout(height=380, paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#e2e8f0"),
        margin=dict(t=20, b=20, l=20, r=20), showlegend=False)
    container.plotly_chart(fig, use_container_width=True)

# ========== TABS ==========
tab_presets, tab_sandbox = st.tabs(["📚 Scénáře (presety)", "🔬 Pískoviště (ruční experimentování)"])

# ================================================================
# TAB 1: PRESETS
# ================================================================
with tab_presets:
    st.subheader("📚 Scénáře z reálné ekonomiky")
    st.markdown("Vyberte ekonomickou událost a sledujte, co se stalo s cenami doma, v zahraničí, s nominálním kurzem a jaký to mělo důsledek na reálný kurz a PPP.")

    preset_names = [p["name"] for p in PRESETS]
    selected_idx = st.selectbox("Vyberte scénář:", range(len(PRESETS)),
        format_func=lambda i: preset_names[i], key="preset_sel")
    preset = PRESETS[selected_idx]

    st.markdown("---")

    # --- Event description ---
    st.markdown(f"### {preset['name']}")
    st.info(f"**Událost:** {preset['desc_event']}")

    col_dom, col_for = st.columns(2)
    with col_dom:
        st.markdown("#### 🇨🇿 Dopad na české ceny")
        st.warning(preset["desc_domestic"])
    with col_for:
        st.markdown("#### 🇪🇺 Dopad na zahraniční ceny")
        st.warning(preset["desc_foreign"])

    col_nom, col_real, col_ppp = st.columns(3)
    with col_nom:
        st.markdown("#### 💱 Nominální kurz")
        st.success(preset["desc_nominal"])
    with col_real:
        st.markdown("#### 📊 Reálný kurz")
        st.error(preset["desc_real"])
    with col_ppp:
        st.markdown("#### ⚖️ PPP kurz")
        st.error(preset["desc_ppp"])

    st.markdown("---")

    # --- Adjustable parameters ---
    st.markdown("### ⚙️ Parametry scénáře (upravitelné)")
    st.markdown("Hodnoty jsou přednastaveny podle scénáře, ale můžete je libovolně měnit.")

    pr_quot = st.radio("Kotace", ["Přímá (CZK/EUR)", "Nepřímá (EUR/CZK)"], key="pr_quot", horizontal=True)
    pr_direct = pr_quot.startswith("Př")

    pc1, pc2, pc3 = st.columns(3)
    with pc1:
        pr_E = st.slider("Nominální kurz (CZK/EUR)", 15.0, 40.0, float(preset["E"]), 0.05, key="pr_E",
            help="Kolik CZK zaplatíte za 1 EUR")
        if not pr_direct:
            st.caption(f"= {1/pr_E:.4f} EUR/CZK")
    with pc2:
        pr_pcz = st.slider("Cenový multiplikátor ČR", 0.80, 1.30, float(preset["p_cz_mult"]), 0.005, key="pr_pcz",
            format="%.3f", help="1.0 = základní ceny, 1.10 = +10 % inflace")
    with pc3:
        pr_peu = st.slider("Cenový multiplikátor EU", 0.80, 1.30, float(preset["p_eu_mult"]), 0.005, key="pr_peu",
            format="%.3f", help="1.0 = základní ceny, 1.05 = +5 % inflace")

    # Weights
    st.markdown("---")
    st.markdown("### 🎯 Váhy položek v koši")
    use_custom_weights = st.checkbox("Upravit váhy ručně", key="pr_cw")

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
            st.warning(f"⚠️ Součet vah = {wsum:.1f} % (bude normalizováno na 100 %)")
    else:
        weights_raw = [it[4] for it in BASKET_DEFAULTS]

    # Individual prices
    st.markdown("---")
    use_custom_prices = st.checkbox("Upravit jednotlivé ceny ručně", key="pr_cp")

    prices_czk = []
    prices_eur = []
    if use_custom_prices:
        st.markdown("#### Ceny v ČR (CZK) a EU (EUR)")
        for i, it in enumerate(BASKET_DEFAULTS):
            cc1, cc2 = st.columns(2)
            with cc1:
                p = st.number_input(f"{it[1]} {it[0]} – CZK", 0.0, 100000.0,
                    float(round(it[2] * preset["p_cz_mult"], 1)), key=f"prc_{i}")
                prices_czk.append(p)
            with cc2:
                p = st.number_input(f"{it[1]} {it[0]} – EUR", 0.0, 10000.0,
                    float(round(it[3] * preset["p_eu_mult"], 2)), 0.01, key=f"pre_{i}", format="%.2f")
                prices_eur.append(p)
    else:
        prices_czk = [it[2] * pr_pcz for it in BASKET_DEFAULTS]
        prices_eur = [it[3] * pr_peu for it in BASKET_DEFAULTS]

    # Calculate
    r = calc_weighted(prices_czk, prices_eur, weights_raw, pr_E)

    # Also compute baseline for comparison
    base_czk = [it[2] for it in BASKET_DEFAULTS]
    base_eur = [it[3] for it in BASKET_DEFAULTS]
    r_base = calc_weighted(base_czk, base_eur, weights_raw, BASE_E)

    # --- Results ---
    st.markdown("---")
    st.markdown("### 📊 Výsledky")

    mc = st.columns(5)
    mc[0].metric("Nominální kurz", fmt_rate(pr_E, pr_direct),
        delta=f"{pr_E - BASE_E:+.2f} vs základ", delta_color="inverse")
    mc[1].metric("Vážený koš ČR", f"{r['basket_czk']:,.2f} Kč",
        delta=f"{(r['basket_czk']/r_base['basket_czk']-1)*100:+.1f} %")
    mc[2].metric("Vážený koš EU", f"{r['basket_eur']:,.2f} €",
        delta=f"{(r['basket_eur']/r_base['basket_eur']-1)*100:+.1f} %")
    mc[3].metric("Reálný kurz Q", f"{r['Q']:.3f}",
        delta=f"{r['Q']-1:+.3f} vs PPP")
    mc[4].metric("PPP kurz", fmt_rate(r['ppp'], pr_direct),
        delta=f"{r['overval']:+.1f} % nadhodnocení")

    # Interpretation
    if r["Q"] < 0.95:
        st.error(f"🔴 **CZK je nadhodnocena** (Q = {r['Q']:.3f}). Český koš je relativně drahý. Export ztrácí konkurenceschopnost.")
    elif r["Q"] > 1.05:
        st.info(f"🔵 **CZK je podhodnocena** (Q = {r['Q']:.3f}). Český koš je relativně levný. Export je konkurenceschopný.")
    else:
        st.success(f"🟢 **Kurz je blízko PPP** (Q = {r['Q']:.3f}). Cenové hladiny jsou přibližně v rovnováze.")

    # Charts
    st.markdown("---")
    col_tbl, col_pie = st.columns([3, 1])
    with col_tbl:
        st.markdown("#### Spotřební koš – detaily")
        render_basket_table(r, pr_E, weights_raw, st)
    with col_pie:
        st.markdown("#### Struktura vah")
        render_weight_pie(weights_raw, st)

    col_bar, col_gauge = st.columns([2, 1])
    with col_bar:
        st.markdown("#### Cenové srovnání ČR vs EU")
        render_bar_chart(r, pr_E, st)
    with col_gauge:
        st.markdown("#### Reálný kurz Q")
        render_gauge(r, st)

    with st.expander("📐 Vzorce s dosazenými hodnotami"):
        render_formulas(r, pr_E, pr_direct, st)

    # Sensitivity
    st.markdown("---")
    st.markdown("### 📈 Citlivostní analýza")
    e_range = np.linspace(max(15, pr_E - 5), min(40, pr_E + 5), 60)
    q_base_line = [(e * r["basket_eur"]) / r["basket_czk"] for e in e_range]
    # +3% CZ
    p_hi = [p * 1.03 for p in prices_czk]
    r_hi = calc_weighted(p_hi, prices_eur, weights_raw, pr_E)
    q_hi = [(e * r_hi["basket_eur"]) / r_hi["basket_czk"] for e in e_range]
    # -3% CZ
    p_lo = [p * 0.97 for p in prices_czk]
    r_lo = calc_weighted(p_lo, prices_eur, weights_raw, pr_E)
    q_lo = [(e * r_lo["basket_eur"]) / r_lo["basket_czk"] for e in e_range]

    fig_sens = go.Figure()
    fig_sens.add_trace(go.Scatter(x=e_range, y=q_lo, mode="lines", name="ČR inflace −3 %", line=dict(color="#22c55e", width=2, dash="dash")))
    fig_sens.add_trace(go.Scatter(x=e_range, y=q_base_line, mode="lines", name="Aktuální cen. hladina", line=dict(color="#f59e0b", width=3)))
    fig_sens.add_trace(go.Scatter(x=e_range, y=q_hi, mode="lines", name="ČR inflace +3 %", line=dict(color="#ef4444", width=2, dash="dash")))
    fig_sens.add_hline(y=1.0, line_color="white", line_width=1, line_dash="dot", annotation_text="PPP (Q=1)")
    fig_sens.add_vline(x=pr_E, line_color="rgba(255,255,255,0.3)", line_dash="dot", annotation_text=f"E={pr_E:.2f}")
    fig_sens.update_layout(height=350,
        xaxis=dict(title="Nominální kurz CZK/EUR", gridcolor="rgba(100,100,100,0.2)"),
        yaxis=dict(title="Reálný kurz Q", gridcolor="rgba(100,100,100,0.2)", range=[0.6, 1.4]),
        plot_bgcolor="rgba(15,23,42,0.5)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"), legend=dict(orientation="h", y=1.1), margin=dict(t=40, b=40))
    st.plotly_chart(fig_sens, use_container_width=True)

# ================================================================
# TAB 2: SANDBOX
# ================================================================
with tab_sandbox:
    st.subheader("🔬 Pískoviště – plná kontrola nad všemi parametry")
    st.markdown("Měňte nominální kurz, cenové hladiny, váhy i jednotlivé ceny. Sledujte dopad na koš, reálný kurz a PPP.")

    sb_quot = st.radio("Kotace", ["Přímá (CZK/EUR)", "Nepřímá (EUR/CZK)"], key="sb_quot", horizontal=True)
    sb_direct = sb_quot.startswith("Př")

    st.markdown("---")
    st.markdown("### Hlavní parametry")
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        sb_E = st.slider("Nominální kurz (CZK/EUR)", 15.0, 40.0, BASE_E, 0.05, key="sb_E")
        if not sb_direct:
            st.caption(f"= {1/sb_E:.4f} EUR/CZK")
    with sc2:
        sb_pcz = st.slider("Cenová hladina ČR (index)", 70.0, 160.0, 100.0, 0.5, key="sb_pcz",
            help="100 = základní ceny")
    with sc3:
        sb_peu = st.slider("Cenová hladina EU (index)", 70.0, 160.0, 100.0, 0.5, key="sb_peu",
            help="100 = základní ceny")

    sb_Pcz = sb_pcz / 100
    sb_Peu = sb_peu / 100

    # Weights
    st.markdown("---")
    st.markdown("### 🎯 Váhy v koši")
    sb_custom_w = st.checkbox("Upravit váhy", key="sb_cw")
    sb_weights = []
    if sb_custom_w:
        swcols = st.columns(7)
        for i, it in enumerate(BASKET_DEFAULTS):
            with swcols[i % 7]:
                w = st.number_input(f"{it[1]}", 0.0, 100.0, it[4], 0.5, key=f"sbw_{i}", format="%.1f")
                sb_weights.append(w)
        swsum = sum(sb_weights)
        if abs(swsum - 100) > 0.5:
            st.warning(f"Součet vah = {swsum:.1f} % (bude normalizováno)")
    else:
        sb_weights = [it[4] for it in BASKET_DEFAULTS]

    # Individual prices
    st.markdown("---")
    sb_custom_p = st.checkbox("Upravit jednotlivé ceny", key="sb_cp")
    sb_prices_czk = []
    sb_prices_eur = []
    if sb_custom_p:
        st.markdown("#### Ceny položek")
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
    st.markdown("### Krátkodobé vs. dlouhodobé dopady")
    lr_E = sb_r["ppp"]
    lr_r = calc_weighted(sb_prices_czk, sb_prices_eur, sb_weights, lr_E)

    col_sr, col_lr = st.columns(2)
    with col_sr:
        st.markdown("#### ⏱️ Krátké období")
        m1, m2, m3 = st.columns(3)
        m1.metric("Nom. kurz", fmt_rate(sb_E, sb_direct))
        m2.metric("Reálný kurz Q", f"{sb_r['Q']:.3f}")
        m3.metric("Nadhodnocení CZK", f"{sb_r['overval']:+.1f} %")
        if sb_r["Q"] < 0.95:
            st.error(f"CZK **nadhodnocena** o {-sb_r['overval']:.1f} %. Export trpí.")
        elif sb_r["Q"] > 1.05:
            st.info(f"CZK **podhodnocena** o {sb_r['overval']:.1f} %. Export prosperuje.")
        else:
            st.success("Kurz blízko PPP. Rovnováha.")

    with col_lr:
        st.markdown("#### 🕰️ Dlouhé období")
        m1, m2, m3 = st.columns(3)
        m1.metric("PPP kurz", fmt_rate(lr_E, sb_direct))
        m2.metric("Reálný kurz Q", f"{lr_r['Q']:.3f}")
        m3.metric("Nadhodnocení", f"{lr_r['overval']:+.1f} %")
        if abs(sb_E - lr_E) > 0.5:
            direction = "posílí (E klesá)" if sb_E > lr_E else "oslabí (E roste)"
            st.warning(f"PPP předpovídá, že CZK **{direction}** směrem k {lr_E:.2f} CZK/EUR.")

    # Results
    st.markdown("---")
    st.markdown("### 📊 Výsledky")
    mc = st.columns(5)
    mc[0].metric("Nominální kurz", fmt_rate(sb_E, sb_direct))
    mc[1].metric("Vážený koš ČR", f"{sb_r['basket_czk']:,.2f} Kč",
        delta=f"{(sb_r['basket_czk']/sb_r_base['basket_czk']-1)*100:+.1f} %")
    mc[2].metric("Vážený koš EU", f"{sb_r['basket_eur']:,.2f} €",
        delta=f"{(sb_r['basket_eur']/sb_r_base['basket_eur']-1)*100:+.1f} %")
    mc[3].metric("Reálný kurz Q", f"{sb_r['Q']:.3f}")
    mc[4].metric("PPP kurz", fmt_rate(sb_r['ppp'], sb_direct))

    st.markdown("---")
    col_tbl2, col_pie2 = st.columns([3, 1])
    with col_tbl2:
        st.markdown("#### Spotřební koš")
        render_basket_table(sb_r, sb_E, sb_weights, st)
    with col_pie2:
        st.markdown("#### Struktura vah")
        render_weight_pie(sb_weights, st)

    col_bar2, col_gauge2 = st.columns([2, 1])
    with col_bar2:
        render_bar_chart(sb_r, sb_E, st)
    with col_gauge2:
        render_gauge(sb_r, st)

    with st.expander("📐 Vzorce"):
        render_formulas(sb_r, sb_E, sb_direct, st)

    # Sensitivity
    st.markdown("---")
    st.markdown("### 📈 Citlivostní analýza")
    se_range = np.linspace(max(15, sb_E - 5), min(40, sb_E + 5), 60)
    sq_base = [(e * sb_r["basket_eur"]) / sb_r["basket_czk"] for e in se_range]
    sp_hi = [p * 1.03 for p in sb_prices_czk]
    sr_hi = calc_weighted(sp_hi, sb_prices_eur, sb_weights, sb_E)
    sq_hi = [(e * sr_hi["basket_eur"]) / sr_hi["basket_czk"] for e in se_range]
    sp_lo = [p * 0.97 for p in sb_prices_czk]
    sr_lo = calc_weighted(sp_lo, sb_prices_eur, sb_weights, sb_E)
    sq_lo = [(e * sr_lo["basket_eur"]) / sr_lo["basket_czk"] for e in se_range]

    sfig = go.Figure()
    sfig.add_trace(go.Scatter(x=se_range, y=sq_lo, mode="lines", name="ČR −3 %", line=dict(color="#22c55e", width=2, dash="dash")))
    sfig.add_trace(go.Scatter(x=se_range, y=sq_base, mode="lines", name="Aktuální", line=dict(color="#f59e0b", width=3)))
    sfig.add_trace(go.Scatter(x=se_range, y=sq_hi, mode="lines", name="ČR +3 %", line=dict(color="#ef4444", width=2, dash="dash")))
    sfig.add_hline(y=1.0, line_color="white", line_width=1, line_dash="dot", annotation_text="PPP")
    sfig.add_vline(x=sb_E, line_color="rgba(255,255,255,0.3)", line_dash="dot", annotation_text=f"E={sb_E:.2f}")
    sfig.update_layout(height=350,
        xaxis=dict(title="Nom. kurz CZK/EUR", gridcolor="rgba(100,100,100,0.2)"),
        yaxis=dict(title="Q", gridcolor="rgba(100,100,100,0.2)", range=[0.6, 1.4]),
        plot_bgcolor="rgba(15,23,42,0.5)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"), legend=dict(orientation="h", y=1.1), margin=dict(t=40, b=40))
    st.plotly_chart(sfig, use_container_width=True)

st.markdown("---")
st.caption("⚠️ Zjednodušený model pro výukové účely. Ceny jsou přibližné. Reálný kurz je v praxi ovlivněn mnoha dalšími faktory.")
