import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import random
import math

st.set_page_config(page_title="Smenarna - Hra na realny kurz", layout="wide")
st.title("💱 Smenarna - Hra na realny kurz")

# Tab structure: Game vs Sandbox
tab_game, tab_sandbox = st.tabs(["🎮 Hra (kviz s nahodnymi soky)", "🔬 Piskoviste (rucni experimentovani)"])

# ========== SHARED CONSTANTS ==========
BASE_E = 25.10

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
    dict(name="Inflace v CR zrychlila na 5 %", icon="🔥", desc="Ceny v CR rostou rychleji nez v eurozone.",
         explain="Vyssi ceska inflace -> cesky kos zdrazi -> pri stejnem nominalnim kurzu je CR relativne drazsi -> realny kurz klesa (CZK realne posiluje, ztrata konkurenceschopnosti).",
         e_chg=0, p_cz=1.05, p_eu=1.01,
         q1="Co se stane s PPP kurzem?", q1a=["PPP kurz roste (CZK by mela byt slabsi)", "PPP kurz klesa", "Nezmeni se"], q1correct=0,
         q2="Je CZK po tomto soku vice nebo mene nadhodnocena?", q2a=["Vice nadhodnocena (CR je drazsi)", "Mene nadhodnocena", "Nezmeni se"], q2correct=0),
    dict(name="Rust cen ropy o 40 %", icon="🛢️", desc="Globalni rust cen energii zdrazuje benzin, dopravu i vytapeni.",
         explain="Ropa je globalni komodita -> zdrazuje v obou zemich, ale CR je vice zavisla na dovozu.",
         e_chg=0.30, p_cz=1.04, p_eu=1.02,
         q1="Ktera ekonomika je cenove vice zasazena?", q1a=["CR (vetsi zavislost na dovozu energii)", "Eurozona", "Stejne"], q1correct=0,
         q2="Jak se zmeni realny kurz?", q2a=["CZK realne oslabi (cesky kos zdrazi vice)", "CZK realne posili", "Nezmeni se"], q2correct=0),
    dict(name="Turisticka sezona - boom v Praze", icon="🏖️", desc="Rekordni pocet turistu v CR zvysuje poptavku po CZK a zdrazuje sluzby.",
         explain="Turiste meni EUR na CZK -> CZK posiluje. Zaroven zdrazuji restaurace, hotely, doprava.",
         e_chg=-0.40, p_cz=1.02, p_eu=1.0,
         q1="Ktera polozka kosu zdrazuje nejvice?", q1a=["Sluzby (espresso, MHD, najem)", "Potraviny", "Elektronika"], q1correct=0,
         q2="Pro turisty je Praha nyni...", q2a=["Drazsi (CZK posilila + ceny rostou)", "Levnejsi", "Stejna"], q2correct=0),
    dict(name="Obchodni prebytek CR", icon="📦", desc="Cesky export prevysuje import. Na devizovem trhu je prebytecna nabidka EUR.",
         explain="Exporteri prodavaji EUR a kupuji CZK -> CZK posiluje.",
         e_chg=-0.60, p_cz=1.0, p_eu=1.0,
         q1="Proc obchodni prebytek posiluje CZK?", q1a=["Exporteri prodavaji EUR za CZK", "CNB intervnuje", "Import klesa"], q1correct=0,
         q2="Jak to ovlivni ceske vyrobce?", q2a=["Export se zdrazuje, tlak na marze", "Export zlevnuje", "Zadny vliv"], q2correct=0),
    dict(name="Recese v eurozone", icon="📉", desc="Nemecko a dalsi zeme v recesi. Klesaji objednavky ceskeho prumyslu.",
         explain="Nizsi poptavka po ceskem exportu -> mensi poptavka po CZK -> CZK oslabuje.",
         e_chg=1.20, p_cz=1.0, p_eu=0.99,
         q1="Jak recese v EU ovlivni CR?", q1a=["Negativne - klesa export do EU", "Pozitivne", "Neovlivni"], q1correct=0,
         q2="Je oslabeni CZK pro ceske exportery spise...", q2a=["Vyhodne (kompenzuje pokles poptavky)", "Nevyhodne", "Irelevantni"], q2correct=0),
    dict(name="Geopoliticka krize", icon="⚔️", desc="Konflikt ve vychodni Evrope zvysuje nejistotu. Investori utikaji do bezpecnych men.",
         explain="CZK je mala mena, investori ji prodavaji -> CZK oslabuje. Rostou ceny energii.",
         e_chg=1.50, p_cz=1.03, p_eu=1.02,
         q1="Proc CZK oslabuje pri geopoliticke krizi?", q1a=["Investori preferuji bezpecne meny (USD, CHF)", "CR exportuje zbrane", "ECB intervnuje"], q1correct=0,
         q2="Co se stane s cenami v CR?", q2a=["Rostou (energie + slabe CZK zdrazuje import)", "Klesaji", "Nemeni se"], q2correct=0),
    dict(name="Rust produktivity v CR (Balassa-Samuelson)", icon="🎓", desc="Ceska ekonomika dohani zapad. Produktivita v prumyslu roste.",
         explain="Rust produktivity -> rust mezd -> zdrazuji se sluzby -> cenova hladina konverguje k EU. CZK posiluje.",
         e_chg=-0.30, p_cz=1.03, p_eu=1.01,
         q1="Co je Balassa-Samuelsonuv efekt?", q1a=["Rust produktivity zdrazuje sluzby a posiluje menu", "Inflacni cileni CNB", "Kurzovy mechanismus ECB"], q1correct=0,
         q2="Je rust ceskych cen v tomto pripade problem?", q2a=["Ne, je to prirozena konvergence", "Ano, je to inflace", "Nevime"], q2correct=0),
    dict(name="CNB intervence - oslabeni CZK", icon="🏦", desc="CNB nakupuje eura za koruny, aby oslabila kurz a podporila export.",
         explain="CNB prodava CZK na devizovem trhu -> nabidka CZK roste -> CZK oslabuje.",
         e_chg=2.00, p_cz=1.0, p_eu=1.0,
         q1="Proc by CNB chtela oslabovat vlastni menu?", q1a=["Podpora exportu a zabraneni deflaci", "Zvyseni dluhu", "Snizeni uroku"], q1correct=0,
         q2="Kdo na oslabeni CZK vydela?", q2a=["Exporteri (zbozi je v EUR levnejsi)", "Importeri", "Sporitelé"], q2correct=0),
]

# ========== SHARED FUNCTIONS ==========
def calc_all(E, P_cz, P_eu):
    cur_czk = [it[2] * P_cz for it in BASKET_ITEMS]
    cur_eur = [it[3] * P_eu for it in BASKET_ITEMS]
    basket_czk = sum(cur_czk)
    basket_eur = sum(cur_eur)
    ppp = basket_czk / basket_eur if basket_eur > 0 else E
    Q = (E * basket_eur) / basket_czk if basket_czk > 0 else 1
    overval = (ppp - E) / E * 100 if E > 0 else 0
    return dict(cur_czk=cur_czk, cur_eur=cur_eur, basket_czk=basket_czk,
                basket_eur=basket_eur, ppp=ppp, Q=Q, overval=overval)

def fmt_rate(e, is_direct):
    return f"{e:.2f} CZK/EUR" if is_direct else f"{1/e:.4f} EUR/CZK"

def render_basket_table(r, E, container):
    tbl = []
    for i, it in enumerate(BASKET_ITEMS):
        czk_p = r["cur_czk"][i]
        eur_p = r["cur_eur"][i]
        conv = eur_p * E
        diff = (conv - czk_p) / czk_p * 100
        tbl.append({"Polozka": f"{it[1]} {it[0]}", "Cena CZK": f"{czk_p:,.0f} Kc",
                     "Cena EUR": f"{eur_p:,.2f} EUR",
                     f"Prevod CZK (E={E:.2f})": f"{conv:,.0f} Kc",
                     "Rozdil": f"{diff:+.1f} %",
                     "Levneji v": "🇨🇿" if czk_p < conv else "🇪🇺"})
    conv_t = r["basket_eur"] * E
    diff_t = (conv_t - r["basket_czk"]) / r["basket_czk"] * 100
    tbl.append({"Polozka": "📦 CELY KOS", "Cena CZK": f"{r['basket_czk']:,.0f} Kc",
                "Cena EUR": f"{r['basket_eur']:,.2f} EUR",
                f"Prevod CZK (E={E:.2f})": f"{conv_t:,.0f} Kc",
                "Rozdil": f"{diff_t:+.1f} %",
                "Levneji v": "🇨🇿" if r["basket_czk"] < conv_t else "🇪🇺"})
    container.dataframe(pd.DataFrame(tbl), use_container_width=True, hide_index=True)

def render_bar_chart(r, E, container):
    """Percentage difference chart instead of absolute values - readable for all items"""
    names = [f"{it[1]} {it[0]}" for it in BASKET_ITEMS]
    czk_prices = r["cur_czk"]
    eur_conv = [r["cur_eur"][i] * E for i in range(len(BASKET_ITEMS))]
    pct_diff = [(eur_conv[i] - czk_prices[i]) / czk_prices[i] * 100 for i in range(len(BASKET_ITEMS))]
    colors = ["#6366f1" if d > 0 else "#ef4444" for d in pct_diff]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=names, y=pct_diff, marker_color=colors,
                         text=[f"{d:+.1f} %" for d in pct_diff], textposition="outside"))
    fig.add_hline(y=0, line_color="white", line_width=1)
    fig.update_layout(height=380,
        yaxis=dict(title="O kolik % je CR levnejsi (+) / drazsi (-) nez EU", gridcolor="rgba(100,100,100,0.2)", zeroline=True),
        xaxis=dict(tickangle=-30),
        plot_bgcolor="rgba(15,23,42,0.5)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"), margin=dict(t=30, b=80),
        showlegend=False)
    container.plotly_chart(fig, use_container_width=True)
    container.caption("🔵 Kladne = v CR je levneji | 🔴 Zaporne = v CR je drazsi. Srovnani pri aktualnim kurzu.")

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
    container.caption("🔴 Q < 0.95: CZK nadhodnocena | 🟢 Q ~ 1: PPP | 🔵 Q > 1.05: CZK podhodnocena")

def render_formulas(r, E, is_direct, container):
    ppp = r["ppp"]
    Q = r["Q"]
    if is_direct:
        container.latex(rf"Q = \frac{{E \times P^*}}{{P}} = \frac{{{E:.2f} \times {r['basket_eur']:,.2f}}}{{{r['basket_czk']:,.0f}}} = {Q:.3f}")
        container.latex(rf"E_{{PPP}} = \frac{{P}}{{P^*}} = \frac{{{r['basket_czk']:,.0f}}}{{{r['basket_eur']:,.2f}}} = {ppp:.2f} \text{{ CZK/EUR}}")
        container.markdown("Q < 1: CZK nadhodnocena | Q > 1: CZK podhodnocena | Q = 1: PPP")
    else:
        ei = 1/E
        pi = 1/ppp
        container.latex(rf"Q = \frac{{P^*}}{{E \times P}} = \frac{{{r['basket_eur']:,.2f}}}{{{ei:.4f} \times {r['basket_czk']:,.0f}}} = {Q:.3f}")
        container.latex(rf"E_{{PPP}} = \frac{{P^*}}{{P}} = \frac{{{r['basket_eur']:,.2f}}}{{{r['basket_czk']:,.0f}}} = {pi:.4f} \text{{ EUR/CZK}}")
        container.markdown("Q < 1: CZK nadhodnocena | Q > 1: CZK podhodnocena | Q = 1: PPP")


# ================================================================
#  TAB 2: SANDBOX (placed first in code for state isolation)
# ================================================================
with tab_sandbox:
    st.subheader("🔬 Piskoviste - experimentujte s parametry")
    st.markdown("Menite nominalni kurz a cenove hladiny a sledujete dopad na realny kurz, PPP a spotrebni kos. Zadny kviz, zadne skore - cista laboratot.")

    sb_quot = st.radio("Kotace kurzu", ["Prima (CZK/EUR)", "Neprima (EUR/CZK)"], key="sb_quot", horizontal=True)
    sb_direct = sb_quot.startswith("Prima")

    st.markdown("---")

    sb_c1, sb_c2, sb_c3 = st.columns(3)
    with sb_c1:
        sb_E = st.number_input("Nominalni kurz (CZK/EUR)", 15.0, 40.0, BASE_E, 0.10, format="%.2f", key="sb_E")
        if not sb_direct:
            st.caption(f"= {1/sb_E:.4f} EUR/CZK")
    with sb_c2:
        sb_pcz = st.number_input("Cenova hladina CR (index, zaklad=100)", 80.0, 150.0, 100.0, 0.5, format="%.1f", key="sb_pcz")
    with sb_c3:
        sb_peu = st.number_input("Cenova hladina EU (index, zaklad=100)", 80.0, 150.0, 100.0, 0.5, format="%.1f", key="sb_peu")

    sb_Pcz = sb_pcz / 100
    sb_Peu = sb_peu / 100
    sb_r = calc_all(sb_E, sb_Pcz, sb_Peu)

    # Short-run vs long-run
    st.markdown("---")
    st.markdown("### Kratkodobe vs. dlouhodobe dopady")

    # Long run: PPP tends to hold -> E converges to PPP
    lr_E = sb_r["ppp"]
    lr_r = calc_all(lr_E, sb_Pcz, sb_Peu)

    col_sr, col_lr = st.columns(2)
    with col_sr:
        st.markdown("#### ⏱️ Kratke obdobi")
        st.markdown("Nominalni kurz se **nemusi** rovnat PPP. Trh reaguje na uroky, kapitolove toky, spekulace.")
        m1, m2, m3 = st.columns(3)
        m1.metric("Nom. kurz", fmt_rate(sb_E, sb_direct))
        m2.metric("Realny kurz Q", f"{sb_r['Q']:.3f}")
        m3.metric("Nadhodnoceni CZK", f"{sb_r['overval']:+.1f} %")

        if sb_r["Q"] < 0.95:
            st.error(f"CZK je **nadhodnocena** o {-sb_r['overval']:.1f} %. Cesky kos je relativne drahy. Export trpi, import se vyplati.")
        elif sb_r["Q"] > 1.05:
            st.info(f"CZK je **podhodnocena** o {sb_r['overval']:.1f} %. Cesky kos je relativne levny. Export je konkurenceschopny, import drahy.")
        else:
            st.success("Kurz je blizko PPP. Cenove hladiny jsou v rovnovaze pri aktualnim kurzu.")

    with col_lr:
        st.markdown("#### 🕰️ Dlouhe obdobi")
        st.markdown("Podle teorie PPP se nominalni kurz **postupne priblizuje** PPP kurzu. Arbitraz vyrovnava cenove rozdily.")
        m1, m2, m3 = st.columns(3)
        m1.metric("PPP kurz", fmt_rate(lr_E, sb_direct))
        m2.metric("Realny kurz Q", f"{lr_r['Q']:.3f}")
        m3.metric("Nadhodnoceni", f"{lr_r['overval']:+.1f} %")

        # Explain convergence
        if abs(sb_E - lr_E) > 0.5:
            direction = "posili (E klesa)" if sb_E > lr_E else "oslabi (E roste)"
            st.warning(f"PPP predpovida, ze CZK v dlouhem obdobi **{direction}** smerem k {lr_E:.2f} CZK/EUR.")
            st.markdown(f"""
**Proc?** Aktualni kurz {sb_E:.2f} se lisi od PPP {lr_E:.2f}:
- Pokud je CR levnejsi (Q > 1): zahranicci vic kupuji v CR -> roste poptavka po CZK -> CZK posiluje
- Pokud je CR drazsi (Q < 1): Cesi vic kupuji v zahranici -> roste poptavka po EUR -> CZK oslabuje
- Tento proces trva **roky az desitky let** (empiricky 3-5 let pro polovicni priblizeni)
""")
        else:
            st.success("Kurz je jiz blizko PPP. V dlouhem obdobi se ocekava stabilita.")

    st.markdown("---")

    # Basket + charts
    st.markdown("### Spotrebni kos")
    render_basket_table(sb_r, sb_E, st)

    sb_col_bar, sb_col_gauge = st.columns([2, 1])
    with sb_col_bar:
        st.markdown("#### Cenove srovnani CR vs EU")
        render_bar_chart(sb_r, sb_E, st)
    with sb_col_gauge:
        st.markdown("#### Realny kurz")
        render_gauge(sb_r, st)

    # Formulas
    with st.expander("📐 Vzorce s dosazenymi hodnotami"):
        render_formulas(sb_r, sb_E, sb_direct, st)

    # Sensitivity analysis
    st.markdown("---")
    st.markdown("### 📊 Citlivostni analyza")
    st.markdown("Jak se meni realny kurz Q pri ruznych hodnotach nominalniho kurzu a inflacniho diferencialu?")

    e_range = np.linspace(sb_E - 4, sb_E + 4, 50)
    q_base = [(e * sb_r["basket_eur"]) / sb_r["basket_czk"] for e in e_range]
    # +2% CZ inflation
    r_hi = calc_all(sb_E, sb_Pcz * 1.02, sb_Peu)
    q_hi = [(e * r_hi["basket_eur"]) / r_hi["basket_czk"] for e in e_range]
    # -2% CZ inflation
    r_lo = calc_all(sb_E, sb_Pcz * 0.98, sb_Peu)
    q_lo = [(e * r_lo["basket_eur"]) / r_lo["basket_czk"] for e in e_range]

    fig_sens = go.Figure()
    fig_sens.add_trace(go.Scatter(x=e_range, y=q_lo, mode="lines", name="Inflace CR -2 %", line=dict(color="#22c55e", width=2, dash="dash")))
    fig_sens.add_trace(go.Scatter(x=e_range, y=q_base, mode="lines", name="Aktualni cenova hladina", line=dict(color="#f59e0b", width=3)))
    fig_sens.add_trace(go.Scatter(x=e_range, y=q_hi, mode="lines", name="Inflace CR +2 %", line=dict(color="#ef4444", width=2, dash="dash")))
    fig_sens.add_hline(y=1.0, line_color="white", line_width=1, line_dash="dot", annotation_text="PPP (Q=1)")
    fig_sens.add_vline(x=sb_E, line_color="rgba(255,255,255,0.3)", line_dash="dot", annotation_text=f"E={sb_E:.2f}")
    fig_sens.update_layout(height=350, xaxis=dict(title="Nominalni kurz CZK/EUR", gridcolor="rgba(100,100,100,0.2)"),
        yaxis=dict(title="Realny kurz Q", gridcolor="rgba(100,100,100,0.2)", range=[0.6, 1.4]),
        plot_bgcolor="rgba(15,23,42,0.5)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"), legend=dict(orientation="h", y=1.1), margin=dict(t=40, b=40))
    st.plotly_chart(fig_sens, use_container_width=True)
    st.caption("Graf ukazuje, jak se realny kurz Q meni s nominalnim kurzem. Vyssi ceska inflace posouva krivku dolu (CZK se realne nadhodnocuje).")


# ================================================================
#  TAB 1: GAME
# ================================================================
with tab_game:
    # Quotation toggle
    gm_quot = st.radio("Kotace kurzu", ["Prima (CZK/EUR)", "Neprima (EUR/CZK)"], key="gm_quot", horizontal=True)
    gm_direct = gm_quot.startswith("Prima")

    # Session state
    G_DEF = dict(g_round=0, g_history=[], g_score=0, g_active=False, g_phase="idle",
                 g_shock=None, g_nrounds=8, g_E=BASE_E, g_Pcz=1.0, g_Peu=1.0,
                 g_prevE=BASE_E, g_prevPcz=1.0, g_prevPeu=1.0, g_quiz={}, g_streak=0)
    for k, v in G_DEF.items():
        if k not in st.session_state:
            st.session_state[k] = v if not isinstance(v, list) else v.copy()

    gs = st.session_state

    # --- IDLE ---
    if not gs.g_active and gs.g_phase == "idle":
        st.info("Nastavte pocet kol a kliknet **Zacit novou hru**.")
        n_r = st.selectbox("Pocet kol", [5, 8, 10], index=1, key="gm_nr")
        if st.button("🚀 Zacit novou hru", use_container_width=True, key="gm_start"):
            for k, v in G_DEF.items():
                gs[k] = v if not isinstance(v, list) else v.copy()
            gs.g_active = True
            gs.g_nrounds = n_r
            gs.g_phase = "pre_shock"
            r0 = calc_all(gs.g_E, gs.g_Pcz, gs.g_Peu)
            gs.g_history = [dict(round=0, E=gs.g_E, Pcz=gs.g_Pcz, Peu=gs.g_Peu,
                                 bczk=r0["basket_czk"], beur=r0["basket_eur"],
                                 Q=r0["Q"], ppp=r0["ppp"], score=0, shock="-")]
            st.rerun()

        # Intro
        st.markdown("---")
        ic1, ic2 = st.columns(2)
        with ic1:
            st.subheader("🎯 Jak hra funguje")
            st.markdown("""
            1. 📢 Prijde **ekonomicka udalost** (sok)
            2. 📊 Zmeni se kurz a/nebo cenove hladiny
            3. ❓ Odpovidate na **2 otazky** o dopadech
            4. 🏆 Ziskavate **body** (max 20/kolo + streak bonus)
            """)
        with ic2:
            st.subheader("📚 Co se naucite")
            st.markdown("""
            - Rozdil mezi nominalnim a realnym kurzem
            - Jak inflacni diferencial ovlivnuje konkurenceschopnost
            - Co je parita kupni sily (PPP)
            - Proc se PPP v kratkem obdobi neplati
            """)

    # --- GENERATE SHOCK ---
    if gs.g_active and gs.g_phase == "pre_shock":
        gs.g_round += 1
        sh = random.choice(SHOCKS).copy()
        sh["e_chg"] = round(sh["e_chg"] + random.gauss(0, 0.15), 2)
        gs.g_prevE = gs.g_E
        gs.g_prevPcz = gs.g_Pcz
        gs.g_prevPeu = gs.g_Peu
        gs.g_E = round(max(15.0, min(40.0, gs.g_E + sh["e_chg"])), 2)
        gs.g_Pcz *= sh["p_cz"]
        gs.g_Peu *= sh["p_eu"]
        gs.g_shock = sh
        gs.g_quiz = {}
        gs.g_phase = "shock_shown"
        st.rerun()

    # --- SHOCK SHOWN ---
    if gs.g_active and gs.g_phase == "shock_shown":
        sh = gs.g_shock
        gr = calc_all(gs.g_E, gs.g_Pcz, gs.g_Peu)

        # Metrics
        mc = st.columns(6)
        mc[0].metric("Kolo", f"{gs.g_round}/{gs.g_nrounds}")
        mc[1].metric("Nom. kurz", fmt_rate(gs.g_E, gm_direct),
                     delta=f"{gs.g_E - gs.g_prevE:+.2f} CZK/EUR")
        mc[2].metric("Cen. hladina CR", f"{gs.g_Pcz*100:.1f}")
        mc[3].metric("Cen. hladina EU", f"{gs.g_Peu*100:.1f}")
        mc[4].metric("Realny kurz Q", f"{gr['Q']:.3f}")
        mc[5].metric("Skore", f"{gs.g_score}", delta=f"serie {gs.g_streak}x" if gs.g_streak >= 2 else "")

        st.markdown("---")

        # Step 1: Event
        st.markdown("## 📢 Krok 1 - Co se stalo")
        ce, cm = st.columns([3, 2])
        with ce:
            st.error(f"### {sh['icon']} {sh['name']}")
            st.markdown(f"**{sh['desc']}**")
        with cm:
            st.warning("#### ⚙️ Mechanismus")
            st.markdown(sh["explain"])

        st.markdown("---")

        # Step 2: Basket
        st.markdown("## 📊 Krok 2 - Dopad na spotrebni kos")
        st.markdown(f"Kurz: **{fmt_rate(gs.g_E, gm_direct)}** (predtim {fmt_rate(gs.g_prevE, gm_direct)})")
        render_basket_table(gr, gs.g_E, st)

        cb, cg = st.columns([2, 1])
        with cb:
            render_bar_chart(gr, gs.g_E, st)
        with cg:
            render_gauge(gr, st)

        with st.expander("📐 Vzorce"):
            render_formulas(gr, gs.g_E, gm_direct, st)

        st.markdown("---")

        # Step 3: Quiz
        st.markdown("## ❓ Krok 3 - Otestujte se")
        qc1, qc2 = st.columns(2)
        with qc1:
            a1 = st.radio(sh["q1"], sh["q1a"], index=None, key=f"gq1_{gs.g_round}")
        with qc2:
            a2 = st.radio(sh["q2"], sh["q2a"], index=None, key=f"gq2_{gs.g_round}")

        if st.button("✅ Odeslat odpovedi", use_container_width=True, key="gm_submit"):
            pts = 0
            if a1 == sh["q1a"][sh["q1correct"]]: pts += 10
            if a2 == sh["q2a"][sh["q2correct"]]: pts += 10
            if pts == 20:
                gs.g_streak += 1
                if gs.g_streak >= 3: pts += 5
            else:
                gs.g_streak = 0
            gs.g_score += pts
            gs.g_quiz = dict(pts=pts, c1=sh["q1a"][sh["q1correct"]], c2=sh["q2a"][sh["q2correct"]], a1=a1, a2=a2)
            gs.g_history.append(dict(round=gs.g_round, E=gs.g_E, Pcz=gs.g_Pcz, Peu=gs.g_Peu,
                                     bczk=gr["basket_czk"], beur=gr["basket_eur"],
                                     Q=gr["Q"], ppp=gr["ppp"], score=pts,
                                     shock=f"{sh['icon']} {sh['name']}"))
            if gs.g_round >= gs.g_nrounds:
                gs.g_phase = "game_over"
                gs.g_active = False
            else:
                gs.g_phase = "pre_shock"
            st.rerun()

        # Previous feedback
        if gs.g_quiz:
            st.markdown("---")
            st.markdown(f"**Minule kolo:** {gs.g_quiz['pts']} bodu")
            if gs.g_quiz.get("a1") != gs.g_quiz["c1"]:
                st.caption(f"Ot. 1 spravne: {gs.g_quiz['c1']}")
            if gs.g_quiz.get("a2") != gs.g_quiz["c2"]:
                st.caption(f"Ot. 2 spravne: {gs.g_quiz['c2']}")

        # History chart
        if len(gs.g_history) > 1:
            st.markdown("---")
            with st.expander("📈 Vyvoj pres kola"):
                h = gs.g_history
                fig_h = go.Figure()
                fig_h.add_trace(go.Scatter(x=[x["round"] for x in h], y=[x["E"] for x in h], mode="lines+markers", name="Nom. kurz", line=dict(color="#6366f1", width=2)))
                fig_h.add_trace(go.Scatter(x=[x["round"] for x in h], y=[x["ppp"] for x in h], mode="lines+markers", name="PPP kurz", line=dict(color="#22c55e", width=2, dash="dash")))
                fig_h.add_trace(go.Scatter(x=[x["round"] for x in h], y=[x["Q"] for x in h], mode="lines+markers", name="Q", line=dict(color="#f59e0b", width=2), yaxis="y2"))
                fig_h.update_layout(height=300,
                    yaxis=dict(title="CZK/EUR", gridcolor="rgba(100,100,100,0.2)"),
                    yaxis2=dict(title="Q", overlaying="y", side="right", range=[0.7, 1.3]),
                    plot_bgcolor="rgba(15,23,42,0.5)", paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#e2e8f0"), xaxis=dict(title="Kolo", dtick=1),
                    legend=dict(orientation="h", y=1.1), margin=dict(t=40, b=40))
                st.plotly_chart(fig_h, use_container_width=True)

    # --- GAME OVER ---
    if gs.g_phase == "game_over":
        st.balloons()
        mx = gs.g_nrounds * 20
        pct = gs.g_score / mx * 100 if mx > 0 else 0
        st.success(f"## 🏁 Hra skoncila! Skore: **{gs.g_score}/{mx}** ({pct:.0f} %)")
        if pct >= 80:
            st.markdown("### 🏆 Vyborne! Mate na analytika CNB.")
        elif pct >= 60:
            st.markdown("### 🥈 Dobra prace!")
        elif pct >= 40:
            st.markdown("### 🥉 Ujde to. Zkuste prostudovat PPP a realny kurz.")
        else:
            st.markdown("### 📚 Doporucuji zopakovat teorii.")

        if len(gs.g_history) > 1:
            df = pd.DataFrame(gs.g_history[1:])
            df.columns = ["Kolo", "E", "P_CZ", "P_EU", "Kos CZK", "Kos EUR", "Q", "PPP", "Body", "Udalost"]
            st.dataframe(df, use_container_width=True, hide_index=True)

        if st.button("🔄 Nova hra", use_container_width=True, key="gm_reset"):
            for k, v in G_DEF.items():
                gs[k] = v if not isinstance(v, list) else v.copy()
            st.rerun()

st.markdown("---")
st.caption("⚠️ Zjednoduseny model pro vyukove ucely. Ceny jsou priblizne, realny kurz je komplexnejsi.")
