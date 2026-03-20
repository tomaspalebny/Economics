import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import random

st.set_page_config(page_title="Smenarna - Hra na realny kurz", layout="wide")
st.title("💱 Smenarna - Hra na realny kurz")
st.markdown("*Interaktivni hra pro vyuku makroekonomie: nominalny kurz, realny kurz a parita kupni sily*")

# ========== CONSTANTS ==========
# Baseline: direct quotation CZK/EUR
BASE_E = 25.10  # nominal CZK per EUR

# Consumer basket: (name, icon, base CZK price, base EUR price)
BASKET_ITEMS = [
    ("Chleb 1 kg",          "🍞", 38,     1.80),
    ("Pivo 0.5L",           "🍺", 25,     3.50),
    ("Benzin 1L",           "⛽", 38,     1.65),
    ("Espresso",            "☕", 65,     2.80),
    ("Big Mac",             "🍔", 109,    4.65),
    ("iPhone 16",           "📱", 27990,  1099.0),
    ("MHD mesicnik",        "🚌", 550,    49.0),
    ("Najem 2+kk mesic",    "🏠", 18000,  950.0),
    ("Elektrina 100 kWh",   "⚡", 650,    35.0),
    ("Mleko 1L",            "🥛", 24,     1.15),
]

# Shock library: each shock adjusts E, P_cz_mult, P_eu_mult
SHOCKS = [
    dict(name="CNB zvysila sazby o 0.5 p.b.", icon="🏦", desc="Vyssi urokove sazby v CR pritahuji zahranicni kapital. Poptavka po CZK roste.",
         explain="Vyssi sazby -> vetsi zajem o CZK -> CZK posiluje (E klesa). Cenova hladina se nemeni okamzite.",
         e_chg=-0.80, p_cz=1.0, p_eu=1.0,
         q1="Jak se zmeni exportni konkurenceschopnost CR?", q1a=["Zhorsi se (CZK je silnejsi, cesky export je drazsi)", "Zlepsi se", "Nezmeni se"], q1correct=0,
         q2="Co se stane s realnym kurzem?", q2a=["Realny kurz klesa (CZK realne posiluje)", "Realny kurz roste", "Nezmeni se"], q2correct=0),
    dict(name="ECB snizila sazby o 0.25 p.b.", icon="🇪🇺", desc="Evropska centralni banka uvolnuje menovou politiku. EUR oslabuje.",
         explain="Nizsi sazby v eurozone -> mensi zajem o EUR -> CZK relativne posiluje.",
         e_chg=-0.50, p_cz=1.0, p_eu=1.0,
         q1="Jak se zmeni cena ceskeho exportu pro nemeckeho kupce?", q1a=["Zdrazuje (CZK posilila)", "Zlevnuje", "Nezmeni se"], q1correct=0,
         q2="Vyplati se nyni Cechum vice nakupovat v Nemecku?", q2a=["Ano, EUR zlevnilo", "Ne, je to drazsi", "Zadna zmena"], q2correct=0),
    dict(name="Inflace v CR zrychlila na 5 %", icon="🔥", desc="Ceny v CR rostou rychleji nez v eurozone. Cenova hladina v CR se zvysuje.",
         explain="Vyssi ceska inflace -> cesky kos zdrazi -> pri stejnem nominalnim kurzu je CR relativne drazsi -> realny kurz roste (CZK realne posiluje, ekonomika ztraci konkurenceschopnost).",
         e_chg=0, p_cz=1.05, p_eu=1.01,
         q1="Co se stane s PPP kurzem?", q1a=["PPP kurz roste (CZK by mela byt slabsi)", "PPP kurz klesa", "Nezmeni se"], q1correct=0,
         q2="Je CZK po tomto soku vice nebo mene nadhodnocena?", q2a=["Vice nadhodnocena (drazsime)", "Mene nadhodnocena", "Nezmeni se"], q2correct=0),
    dict(name="Rust cen ropy o 40 %", icon="🛢️", desc="Globalni rust cen energii zdrazuje benzin, dopravu i vytapeni v obou ekonomikach.",
         explain="Ropa je globalni komodita -> zdrazuje v obou zemich, ale CR je vice zavisla na dovozu -> cesky kos zdrazuje o neco vice.",
         e_chg=0.30, p_cz=1.04, p_eu=1.02,
         q1="Ktera ekonomika je cenove vice zasazena?", q1a=["CR (vetsi zavislost na dovozu)", "Eurozona", "Stejne"], q1correct=0,
         q2="Jak se zmeni realny kurz?", q2a=["CZK realne oslabuje (cesky kos zdrazuje vice)", "CZK realne posiluje", "Nezmeni se"], q2correct=0),
    dict(name="Turisticka sezona - boom v Praze", icon="🏖️", desc="Rekordni pocet turistu v CR zvysuje poptavku po CZK a zdrazuje sluzby.",
         explain="Turiste meni EUR na CZK -> CZK posiluje. Zaroven zdrazuji restaurace, hotely, doprava v CR.",
         e_chg=-0.40, p_cz=1.02, p_eu=1.0,
         q1="Ktera polozka kosu zdrazuje nejvice?", q1a=["Sluzby (espresso, MHD, najem)", "Potraviny", "Elektronika"], q1correct=0,
         q2="Pro turisty je Praha nyni...", q2a=["Drazsi (CZK posilila + ceny rostou)", "Levnejsi", "Stejna"], q2correct=0),
    dict(name="Obchodni prebytek CR", icon="📦", desc="Cesky export prevysuje import. Na devizovem trhu je prebytecna nabidka EUR.",
         explain="Exporteri prodavaji EUR a kupuji CZK -> CZK posiluje. Ceny se nemeni.",
         e_chg=-0.60, p_cz=1.0, p_eu=1.0,
         q1="Proc obchodni prebytek posiluje CZK?", q1a=["Exporteri prodavaji EUR za CZK", "CNB intervnuje", "Import klesa"], q1correct=0,
         q2="Jak to ovlivni ceske vyrobce?", q2a=["Export se zdrazuje, tlak na marze", "Export zlevnuje", "Zadny vliv"], q2correct=0),
    dict(name="Recese v eurozone", icon="📉", desc="Nemecko a dalsi zeme eurozone v recesi. Klesaji objednavky ceskeho prumyslu.",
         explain="Nizsi poptavka po ceskem exportu -> mensi poptavka po CZK -> CZK oslabuje. Ceny v eurozone stagnuji.",
         e_chg=1.20, p_cz=1.0, p_eu=0.99,
         q1="Jak recese v eurozone ovlivni ceskou ekonomiku?", q1a=["Negativne - klesa export do EU", "Pozitivne", "Neovlivni"], q1correct=0,
         q2="Je oslabeni CZK pro ceske exportery spise...", q2a=["Vyhodne (kompenzuje pokles poptavky)", "Nevyhodne", "Irelevantni"], q2correct=0),
    dict(name="Geopoliticka krize", icon="⚔️", desc="Konflikt ve vychodni Evrope zvysuje nejistotu. Investori utikaji do bezpecnych men.",
         explain="CZK je mala mena, investori ji prodavaji -> CZK oslabuje. Zaroven rostou ceny energii a potravin v obou regionech.",
         e_chg=1.50, p_cz=1.03, p_eu=1.02,
         q1="Proc CZK oslabuje pri geopoliticke krizi?", q1a=["Investori preferuji bezpecne meny (USD, CHF)", "CR exportuje zbrane", "ECB intervnuje"], q1correct=0,
         q2="Co se stane s cenami v CR?", q2a=["Rostou (energie + slabe CZK zdrazuje import)", "Klesaji", "Nemeni se"], q2correct=0),
    dict(name="Rust produktivity v CR (Balassa-Samuelson)", icon="🎓", desc="Ceska ekonomika dohani zapadni Evropu. Produktivita v prumyslu roste rychleji nez v EU.",
         explain="Rust produktivity v obchodovatelnem sektoru -> rust mezd -> zdrazuji se neobchodovatelne sluzby (kadernik, najem) -> cenova hladina v CR konverguje k EU. Zaroven CZK tenduje k posilovani.",
         e_chg=-0.30, p_cz=1.03, p_eu=1.01,
         q1="Co je Balassa-Samuelsonuv efekt?", q1a=["Rust produktivity zdrazuje sluzby a posiluje menu", "Inflacni cileni CNB", "Kurzovy mechanismus ECB"], q1correct=0,
         q2="Je rust ceskych cen v tomto pripade problem?", q2a=["Ne, je to prirozena konvergence", "Ano, je to inflace", "Nevime"], q2correct=0),
    dict(name="CNB intervence - oslabeni CZK", icon="🏦", desc="CNB nakupuje eura za koruny, aby oslabila kurz a podporila export a inflaci.",
         explain="CNB prodava CZK na devizovem trhu -> nabidka CZK roste -> CZK oslabuje. Cil: podpora exportu a dosazeni inflacniho cile.",
         e_chg=2.00, p_cz=1.0, p_eu=1.0,
         q1="Proc by CNB chtela oslabovat vlastni menu?", q1a=["Podpora exportu a zabraneni deflaci", "Zvyseni dluhu", "Snizeni uroku"], q1correct=0,
         q2="Kdo na oslabeni CZK vydela?", q2a=["Exporteri (jejich zbozi je v EUR levnejsi)", "Importeri", "Sporitelé"], q2correct=0),
]

# ========== SESSION STATE ==========
DEF = dict(round=0, history=[], score=0, game_active=False, phase="idle",
           shock=None, n_rounds=8, E=BASE_E, P_cz=1.0, P_eu=1.0,
           prev_E=BASE_E, prev_P_cz=1.0, prev_P_eu=1.0,
           prices_czk=[it[2] for it in BASKET_ITEMS],
           prices_eur=[it[3] for it in BASKET_ITEMS],
           quiz_answers={}, streak=0)

for k, v in DEF.items():
    if k not in st.session_state:
        st.session_state[k] = v if not isinstance(v, list) else v.copy()

ss = st.session_state

# ========== QUOTATION TOGGLE ==========
st.sidebar.header("Nastaveni zobrazeni")
quot = st.sidebar.radio("Kotace kurzu", ["Prima (CZK/EUR)", "Neprima (EUR/CZK)"],
                        help="Prima: kolik CZK za 1 EUR. Neprima: kolik EUR za 1 CZK.")
is_direct = quot.startswith("Prima")

def fmt_rate(e_direct):
    if is_direct:
        return f"{e_direct:.2f} CZK/EUR"
    else:
        return f"{1/e_direct:.4f} EUR/CZK"

def fmt_rate_num(e_direct):
    return e_direct if is_direct else 1/e_direct

# ========== CALCULATIONS ==========
def calc_all(E, P_cz, P_eu, prices_czk, prices_eur):
    # Current prices = base * inflation multiplier
    cur_czk = [p * P_cz for p in [it[2] for it in BASKET_ITEMS]]
    cur_eur = [p * P_eu for p in [it[3] for it in BASKET_ITEMS]]
    basket_czk = sum(cur_czk)
    basket_eur = sum(cur_eur)
    # PPP rate (direct): at what E would baskets cost the same?
    ppp_direct = basket_czk / basket_eur if basket_eur > 0 else E
    # Real exchange rate: Q = (E * P_eu_index) / P_cz_index
    # Using basket approach: Q = (E * basket_eur) / basket_czk
    Q = (E * basket_eur) / basket_czk if basket_czk > 0 else 1
    # Overvaluation: how far is E from PPP
    # If E < PPP_direct -> CZK is overvalued (stronger than PPP suggests)
    overval_pct = (ppp_direct - E) / E * 100 if E > 0 else 0
    return dict(cur_czk=cur_czk, cur_eur=cur_eur, basket_czk=basket_czk, basket_eur=basket_eur,
                ppp_direct=ppp_direct, Q=Q, overval_pct=overval_pct)

# ========== SIDEBAR: GAME CONTROLS ==========
st.sidebar.markdown("---")
st.sidebar.header("🎮 Ovladani hry")

if not ss.game_active and ss.phase == "idle":
    n_rounds = st.sidebar.selectbox("Pocet kol", [5, 8, 10], index=1)
    if st.sidebar.button("🚀 Zacit novou hru", use_container_width=True):
        for k, v in DEF.items():
            ss[k] = v if not isinstance(v, list) else v.copy()
        ss.game_active = True
        ss.n_rounds = n_rounds
        ss.phase = "pre_shock"
        r = calc_all(ss.E, ss.P_cz, ss.P_eu, ss.prices_czk, ss.prices_eur)
        ss.history = [dict(round=0, E=ss.E, P_cz=ss.P_cz, P_eu=ss.P_eu,
                           basket_czk=r["basket_czk"], basket_eur=r["basket_eur"],
                           Q=r["Q"], ppp=r["ppp_direct"], score=0, shock="-")]
        st.rerun()

# Generate shock
if ss.game_active and ss.phase == "pre_shock":
    ss.round += 1
    shock = random.choice(SHOCKS).copy()
    ss.prev_E = ss.E
    ss.prev_P_cz = ss.P_cz
    ss.prev_P_eu = ss.P_eu
    ss.E = round(ss.E + shock["e_chg"] + random.gauss(0, 0.15), 2)
    ss.E = max(15.0, min(40.0, ss.E))
    ss.P_cz *= shock["p_cz"]
    ss.P_eu *= shock["p_eu"]
    ss.shock = shock
    ss.quiz_answers = {}
    ss.phase = "shock_shown"
    st.rerun()

# Quiz submission
if ss.game_active and ss.phase == "shock_shown":
    sh = ss.shock
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"### Kolo {ss.round}/{ss.n_rounds}")
    st.sidebar.markdown(f"## {sh['icon']} {sh['name']}")

    st.sidebar.markdown("### Kviz")
    a1 = st.sidebar.radio(sh["q1"], sh["q1a"], index=None, key=f"q1_{ss.round}")
    a2 = st.sidebar.radio(sh["q2"], sh["q2a"], index=None, key=f"q2_{ss.round}")

    if st.sidebar.button("✅ Odeslat odpovedi", use_container_width=True):
        pts = 0
        if a1 == sh["q1a"][sh["q1correct"]]:
            pts += 10
        if a2 == sh["q2a"][sh["q2correct"]]:
            pts += 10
        if pts == 20:
            ss.streak += 1
            if ss.streak >= 3:
                pts += 5  # streak bonus
        else:
            ss.streak = 0
        ss.score += pts
        ss.quiz_answers = dict(a1=a1, a2=a2, pts=pts,
                               c1=sh["q1a"][sh["q1correct"]], c2=sh["q2a"][sh["q2correct"]])

        r = calc_all(ss.E, ss.P_cz, ss.P_eu, ss.prices_czk, ss.prices_eur)
        ss.history.append(dict(round=ss.round, E=ss.E, P_cz=ss.P_cz, P_eu=ss.P_eu,
                               basket_czk=r["basket_czk"], basket_eur=r["basket_eur"],
                               Q=r["Q"], ppp=r["ppp_direct"], score=pts,
                               shock=f"{sh['icon']} {sh['name']}"))

        if ss.round >= ss.n_rounds:
            ss.phase = "game_over"
            ss.game_active = False
        else:
            ss.phase = "pre_shock"
        st.rerun()

# ========== MAIN CONTENT ==========
r = calc_all(ss.E, ss.P_cz, ss.P_eu, ss.prices_czk, ss.prices_eur)

# --- IDLE ---
if ss.phase == "idle":
    st.info("👈 Zvolte kotaci kurzu a pocet kol, pak kliknete **Zacit novou hru**.")
    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🎯 Jak hra funguje")
        st.markdown("""
        Jste **analytik CNB** a sledujete vyvoj kurzu CZK/EUR.

        1. 📢 **Ekonomicka udalost** zmeni nominalni kurz a/nebo cenove hladiny
        2. 📊 **Spotrebni kos** se prepocita - vidite ceny v CZK i EUR
        3. ❓ **Kviz** - odpovidate na 2 otazky o dopadech udalosti
        4. 🏆 **Skore** - 10 bodu za spravnou odpoved, bonus za serii
        """)
    with c2:
        st.subheader("📚 Klicove vzorce")
        if is_direct:
            st.markdown("**Prima kotace** (CZK/EUR) - kolik CZK za 1 EUR:")
            st.latex(r"Q = \frac{E_{CZK/EUR} \times P^*_{EU}}{P_{CZ}}")
            st.latex(r"E_{PPP} = \frac{P_{CZ}}{P^*_{EU}} = \frac{\text{kos v CZK}}{\text{kos v EUR}}")
            st.markdown("Nadhodnoceni CZK = pokud $E < E_{PPP}$ (koruna silnejsi nez PPP)")
        else:
            st.markdown("**Neprima kotace** (EUR/CZK) - kolik EUR za 1 CZK:")
            st.latex(r"Q = \frac{P^*_{EU}}{E_{EUR/CZK} \times P_{CZ}}")
            st.latex(r"E_{PPP} = \frac{P^*_{EU}}{P_{CZ}} = \frac{\text{kos v EUR}}{\text{kos v CZK}}")
            st.markdown("Nadhodnoceni CZK = pokud $E > E_{PPP}$ (koruna silnejsi nez PPP)")

    st.subheader("Ukazkovy spotrebni kos (vychozi stav)")
    df = pd.DataFrame({
        "Polozka": [f"{it[1]} {it[0]}" for it in BASKET_ITEMS],
        "Cena CZK": [f"{it[2]:,.0f} Kc" for it in BASKET_ITEMS],
        "Cena EUR": [f"{it[3]:,.2f} EUR" for it in BASKET_ITEMS],
        f"Prevod na CZK ({BASE_E:.2f})": [f"{it[3]*BASE_E:,.0f} Kc" for it in BASKET_ITEMS],
        "Kde levneji?": ["🇨🇿" if it[2] < it[3]*BASE_E else "🇪🇺" for it in BASKET_ITEMS],
    })
    st.dataframe(df, use_container_width=True, hide_index=True)

# --- ACTIVE GAME ---
if ss.phase in ("shock_shown",):
    sh = ss.shock

    # TOP METRICS
    mc = st.columns(6)
    mc[0].metric("Kolo", f"{ss.round}/{ss.n_rounds}")
    mc[1].metric("Nominalni kurz", fmt_rate(ss.E),
                 delta=f"{fmt_rate_num(ss.E) - fmt_rate_num(ss.prev_E):+.2f}")
    mc[2].metric("Cen. hladina CZ", f"{ss.P_cz*100:.1f}",
                 delta=f"{(ss.P_cz - ss.prev_P_cz)*100:+.1f}")
    mc[3].metric("Cen. hladina EU", f"{ss.P_eu*100:.1f}",
                 delta=f"{(ss.P_eu - ss.prev_P_eu)*100:+.1f}")
    mc[4].metric("Realny kurz Q", f"{r['Q']:.3f}",
                 delta="CZK podhodnocena" if r['Q'] > 1.02 else ("CZK nadhodnocena" if r['Q'] < 0.98 else "~ PPP"))
    mc[5].metric("Skore", f"{ss.score}", delta=f"serie {ss.streak}x" if ss.streak >= 2 else "")

    st.markdown("---")

    # STEP 1
    st.markdown("## 📢 Krok 1 - Co se stalo")
    ce, cm = st.columns([3, 2])
    with ce:
        st.error(f"### {sh['icon']} {sh['name']}")
        st.markdown(f"**{sh['desc']}**")
    with cm:
        st.warning("#### ⚙️ Mechanismus")
        st.markdown(sh["explain"])

    st.markdown("---")

    # STEP 2 - BASKET TABLE
    st.markdown("## 📊 Krok 2 - Spotrebni kos po udalosti")
    st.markdown(f"Nominalni kurz: **{fmt_rate(ss.E)}** | Predchozi: {fmt_rate(ss.prev_E)}")

    cur_czk = r["cur_czk"]
    cur_eur = r["cur_eur"]

    tbl_data = []
    for i, it in enumerate(BASKET_ITEMS):
        czk_p = cur_czk[i]
        eur_p = cur_eur[i]
        conv = eur_p * ss.E
        cheaper = "🇨🇿 CR" if czk_p < conv else "🇪🇺 EU"
        diff_pct = (conv - czk_p) / czk_p * 100
        tbl_data.append({
            "Polozka": f"{it[1]} {it[0]}",
            "Cena CZK": f"{czk_p:,.0f} Kc",
            "Cena EUR": f"{eur_p:,.2f} EUR",
            f"Prevod na CZK (E={ss.E:.2f})": f"{conv:,.0f} Kc",
            "Rozdil": f"{diff_pct:+.1f} %",
            "Levneji v": cheaper,
        })
    # Totals
    conv_total = r["basket_eur"] * ss.E
    diff_total = (conv_total - r["basket_czk"]) / r["basket_czk"] * 100
    tbl_data.append({
        "Polozka": "📦 CELY KOS",
        "Cena CZK": f"{r['basket_czk']:,.0f} Kc",
        "Cena EUR": f"{r['basket_eur']:,.2f} EUR",
        f"Prevod na CZK (E={ss.E:.2f})": f"{conv_total:,.0f} Kc",
        "Rozdil": f"{diff_total:+.1f} %",
        "Levneji v": "🇨🇿 CR" if r["basket_czk"] < conv_total else "🇪🇺 EU",
    })
    st.dataframe(pd.DataFrame(tbl_data), use_container_width=True, hide_index=True)

    # Key indicators
    st.markdown("---")
    ki = st.columns(4)
    ki[0].metric("Kos v CZK", f"{r['basket_czk']:,.0f} Kc")
    ki[1].metric("Kos v EUR", f"{r['basket_eur']:,.2f} EUR")
    ppp_val = r["ppp_direct"]
    if is_direct:
        ki[2].metric("PPP kurz", f"{ppp_val:.2f} CZK/EUR",
                     help="Kurz, pri kterem by kos stal v obou zemich stejne")
    else:
        ki[2].metric("PPP kurz", f"{1/ppp_val:.4f} EUR/CZK",
                     help="Kurz, pri kterem by kos stal v obou zemich stejne")
    ov = r["overval_pct"]
    ki[3].metric("Nadhodnoceni CZK", f"{ov:+.1f} %",
                 help="Kladne = CZK nadhodnocena (CR je drazsi nez PPP), zaporne = podhodnocena")

    # Formulas
    with st.expander("📐 Vzorce - jak se to pocita"):
        if is_direct:
            st.markdown(f"""
**Prima kotace (CZK/EUR):** E = {ss.E:.2f}

**Realny kurz:**
""")
            st.latex(rf"Q = \frac{{E \times P^*}}{{P}} = \frac{{{ss.E:.2f} \times {r['basket_eur']:,.2f}}}{{{r['basket_czk']:,.0f}}} = {r['Q']:.3f}")
            st.markdown("**PPP kurz:**")
            st.latex(rf"E_{{PPP}} = \frac{{P}}{{P^*}} = \frac{{{r['basket_czk']:,.0f}}}{{{r['basket_eur']:,.2f}}} = {ppp_val:.2f} \text{{ CZK/EUR}}")
            st.markdown(f"""
- Pokud Q < 1: CZK je nadhodnocena (cesky kos je relativne drazsi)
- Pokud Q > 1: CZK je podhodnocena (cesky kos je relativne levnejsi)
- Pokud Q = 1: platí parita kupni sily
""")
        else:
            e_inv = 1/ss.E
            ppp_inv = 1/ppp_val
            st.markdown(f"""
**Neprima kotace (EUR/CZK):** E = {e_inv:.4f}

**Realny kurz:**
""")
            st.latex(rf"Q = \frac{{P^*}}{{E \times P}} = \frac{{{r['basket_eur']:,.2f}}}{{{e_inv:.4f} \times {r['basket_czk']:,.0f}}} = {r['Q']:.3f}")
            st.markdown("**PPP kurz:**")
            st.latex(rf"E_{{PPP}} = \frac{{P^*}}{{P}} = \frac{{{r['basket_eur']:,.2f}}}{{{r['basket_czk']:,.0f}}} = {ppp_inv:.4f} \text{{ EUR/CZK}}")
            st.markdown(f"""
- Pokud Q < 1: CZK je nadhodnocena (cesky kos je relativne drazsi)
- Pokud Q > 1: CZK je podhodnocena (cesky kos je relativne levnejsi)
- Pokud Q = 1: plati parita kupni sily
""")

    # BAR CHART comparison
    st.markdown("---")
    col_bar, col_gauge = st.columns([2, 1])
    with col_bar:
        st.subheader("Porovnani kosu")
        names = [f"{it[1]} {it[0]}" for it in BASKET_ITEMS]
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(name="Cena v CR (CZK)", x=names, y=cur_czk, marker_color="#6366f1"))
        fig_bar.add_trace(go.Bar(name="Cena v EU (prevedeno na CZK)", x=names, y=[e * ss.E for e in cur_eur], marker_color="#f59e0b"))
        fig_bar.update_layout(barmode="group", height=380,
            plot_bgcolor="rgba(15,23,42,0.5)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0"), xaxis=dict(tickangle=-35),
            yaxis=dict(title="CZK", gridcolor="rgba(100,100,100,0.2)"),
            legend=dict(orientation="h", y=1.1), margin=dict(t=40, b=80))
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_gauge:
        st.subheader("Realny kurz")
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=r["Q"],
            delta={"reference": 1.0, "position": "bottom"},
            gauge=dict(
                axis=dict(range=[0.7, 1.3], tickcolor="#e2e8f0"),
                bar=dict(color="#f59e0b"),
                steps=[
                    dict(range=[0.7, 0.95], color="rgba(239,68,68,0.2)"),
                    dict(range=[0.95, 1.05], color="rgba(34,197,94,0.2)"),
                    dict(range=[1.05, 1.3], color="rgba(99,102,241,0.2)")],
                threshold=dict(line=dict(color="#22c55e", width=3), value=1.0)),
            title=dict(text="Q (1.0 = PPP)", font=dict(size=14))))
        fig_g.update_layout(height=280, paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#e2e8f0"), margin=dict(t=60, b=20))
        st.plotly_chart(fig_g, use_container_width=True)
        st.caption("🔴 Q < 0.95: CZK nadhodnocena | 🟢 Q ~ 1: PPP | 🔵 Q > 1.05: CZK podhodnocena")

    # STEP 3 - QUIZ
    st.markdown("---")
    st.markdown("## ❓ Krok 3 - Otestujte se")
    st.markdown("Odpovezte na dve otazky v **postrannim panelu** a kliknete **Odeslat odpovedi**.")

    # Previous answers feedback
    if ss.quiz_answers:
        st.success(f"Minule kolo: **{ss.quiz_answers['pts']} bodu**")
        if ss.quiz_answers.get("a1") != ss.quiz_answers["c1"]:
            st.caption(f"Ot. 1 spravne: {ss.quiz_answers['c1']}")
        if ss.quiz_answers.get("a2") != ss.quiz_answers["c2"]:
            st.caption(f"Ot. 2 spravne: {ss.quiz_answers['c2']}")

    # HISTORY
    if len(ss.history) > 1:
        st.markdown("---")
        st.subheader("📈 Vyvoj")
        hist = ss.history
        rounds = [h["round"] for h in hist]
        fig_h = go.Figure()
        fig_h.add_trace(go.Scatter(x=rounds, y=[h["E"] for h in hist], mode="lines+markers", name="Nom. kurz CZK/EUR", line=dict(color="#6366f1", width=2), yaxis="y"))
        fig_h.add_trace(go.Scatter(x=rounds, y=[h["Q"] for h in hist], mode="lines+markers", name="Realny kurz Q", line=dict(color="#f59e0b", width=2), yaxis="y2"))
        fig_h.add_trace(go.Scatter(x=rounds, y=[h["ppp"] for h in hist], mode="lines+markers", name="PPP kurz", line=dict(color="#22c55e", width=2, dash="dash"), yaxis="y"))
        fig_h.update_layout(height=320,
            yaxis=dict(title="CZK/EUR", gridcolor="rgba(100,100,100,0.2)"),
            yaxis2=dict(title="Q", overlaying="y", side="right", range=[0.7, 1.3]),
            plot_bgcolor="rgba(15,23,42,0.5)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2e8f0"), xaxis=dict(title="Kolo", dtick=1),
            legend=dict(orientation="h", y=1.1), margin=dict(t=40, b=40))
        st.plotly_chart(fig_h, use_container_width=True)

# --- GAME OVER ---
if ss.phase == "game_over":
    st.balloons()
    avg = ss.score / max(1, ss.round)
    max_possible = ss.round * 20

    st.success(f"## 🏁 Hra skoncila! Skore: **{ss.score}/{max_possible}** ({ss.score/max_possible*100:.0f} %)")
    if ss.score / max_possible >= 0.8:
        st.markdown("### 🏆 Vyborne! Muzete nastoupit na CNB.")
    elif ss.score / max_possible >= 0.6:
        st.markdown("### 🥈 Dobra prace! Zakladni principy mate.")
    elif ss.score / max_possible >= 0.4:
        st.markdown("### 🥉 Ujde to. Doporucuji zopakovat PPP a realny kurz.")
    else:
        st.markdown("### 📚 Zkuste to znovu po prostudovani teorie.")

    st.markdown("---")
    if len(ss.history) > 1:
        st.subheader("📋 Prehled kol")
        df_h = pd.DataFrame(ss.history[1:])
        df_h.columns = ["Kolo", "Nom. kurz", "P_CZ", "P_EU", "Kos CZK", "Kos EUR", "Q", "PPP", "Body", "Udalost"]
        st.dataframe(df_h, use_container_width=True, hide_index=True)

    if st.button("🔄 Nova hra", use_container_width=True):
        for k, v in DEF.items():
            ss[k] = v if not isinstance(v, list) else v.copy()
        st.rerun()

st.markdown("---")
st.caption("⚠️ Zjednoduseny model pro vyukove ucely. Ceny jsou priblizne, realny kurz je komplexnejsi.")
