import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="Simulátor veřejných financí ČR", layout="wide", page_icon="🏛️")

# Session state pro reset
if "reset" not in st.session_state:
    st.session_state.reset = False

def do_reset():
    st.session_state.reset = True
    # Vymaže všechny widget klíče aby se načetly defaulty
    for key in list(st.session_state.keys()):
        if key != "reset":
            del st.session_state[key]

st.title("🏛️ Simulátor veřejných financí")

# ─────────────────────────────────────────────────────────────────────────────
# DATOVÉ PŘESETY  –  zdrojem MFČR „SR v kostce 2025" (plán 2025)
# HDP 2025 odhad MFČR: 8 400 mld Kč
# SR: příjmy 2 086,1 / výdaje 2 327,1 / saldo −241,0 mld
# Vládní sektor: příjmy ~43,5 % HDP / výdaje ~45,8 % HDP / saldo −2,3 % HDP
# Skutečnost 2025: příjmy 1 965,4 / výdaje 2 236,8 / saldo −271,4 mld (2024 SK)
# ─────────────────────────────────────────────────────────────────────────────

GDP_DEFAULT = 8400.0        # mld Kč, odhad MFČR 2025
WORKFORCE   = 5.50          # mil. zaměstnaných
PENSIONERS  = 2.90          # mil. důchodců
UNEMPLOYED  = 0.15          # mil. nezaměstnaných
AVG_WAGE    = 46700         # Kč/měsíc (průměrná hrubá mzda ČR 2025 dle MFČR)
AVG_PENSION = 21080         # Kč/měsíc (průměrný důchod k 1.1.2025)
AVG_UNEMP   = 14500         # Kč/měsíc

# ── Příjmy SR 2025 (mld Kč, MFČR) ──────────────────────────────────────────
SR_REV_DEFAULT = {
    "Pojistné na soc. zabezpečení":      809.4,
    "DPH":                               414.0,
    "DPPO":                              244.3,
    "DPFO":                              184.7,
    "Spotřební daně":                    161.1,
    "Transfery přijaté (EU + FM)":       172.5,
    "Kapitálové příjmy":                  34.6,
    "Nedaňové příjmy":                    38.9,
    "Ostatní daňové příjmy":              26.6,
}
# ── Výdaje SR 2025 (mld Kč, MFČR) ──────────────────────────────────────────
SR_EXP_DEFAULT = {
    "Důchody":                           717.2,
    "Ostatní sociální dávky":            187.5,
    "Podpora v nezaměstnanosti":          12.0,
    "Platba státu do VZP":               154.6,
    "Vzdělávání":                        255.0,
    "Obrana":                            160.8,
    "Bezpečnost, policie, IZS, justice":  95.0,
    "Doprava a infrastruktura":          105.0,
    "Obsluha státního dluhu":            100.0,
    "Odvody do EU":                       65.3,
    "Zemědělství a lesnictví":            55.0,
    "Průmysl a podnikání":                47.2,
    "Věda a výzkum":                      51.6,
    "Životní prostředí":                  30.0,
    "Kultura, sport, média":              22.0,
    "Bydlení a územní rozvoj":            22.0,
    "Státní správa":                      80.0,
    "Ostatní výdaje a rezervy":          166.9,
}
# ── Vládní sektor 2025 (% HDP, MFČR/Eurostat odhad) ─────────────────────────
GS_REV_PCT = {
    "Sociální pojistné (celý systém)":      15.8,
    "DPH (celý výnos)":                      7.0,
    "DPFO (celý výnos)":                     4.5,
    "DPPO (celý výnos)":                     3.5,
    "Spotřební daně (celý výnos)":           2.3,
    "Zdravotní pojistné (VZP)":              4.8,
    "Majetkové, enviro a ostatní daně":      1.8,
    "Transfery EU a ostatní":                2.0,
    "Nedaňové + kapitálové příjmy":          1.8,
}
GS_EXP_PCT = {
    "Důchody a penze":                      10.2,
    "Zdravotnictví (celý sektor)":           8.0,
    "Vzdělávání (celý sektor)":              5.2,
    "Sociální dávky (ostatní)":              3.2,
    "Obrana":                                2.0,
    "Bezpečnost a justice":                  1.5,
    "Doprava a infrastruktura":              1.8,
    "Obecná státní správa":                  1.4,
    "Zemědělství, lesnictví, rybářství":     0.8,
    "Průmysl, obchod a podnikání":           0.8,
    "Věda a výzkum":                         0.7,
    "Životní prostředí":                     0.5,
    "Kultura, sport, média":                 0.5,
    "Bydlení a územní rozvoj":               0.4,
    "Obsluha dluhu":                         1.4,
    "Odvody do EU":                          0.8,
    "Ostatní výdaje":                        6.6,
}

DEBT_SR  = 3613.6    # mld Kč, státní dluh plán 2025 dle MFČR
DEBT_GS  = GDP_DEFAULT * 44.3 / 100  # vládní sektor dluh odhad 2025

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    if st.button("🔄 Reset na výchozí hodnoty", use_container_width=True, type="primary"):
        do_reset()
        st.rerun()
    st.markdown("---")
    st.header("⚙️ Makro parametry")
    gdp = st.number_input("HDP (mld Kč)", min_value=1000.0, max_value=20000.0,
                          value=GDP_DEFAULT, step=100.0, format="%.0f",
                          help="HDP ČR 2025 – MFČR odhad 8 400 mld Kč", key="w_gdp")
    workforce  = st.number_input("Zaměstnaní (mil.)", 1.0, 10.0, WORKFORCE, 0.01, "%.2f", key="w_workforce")
    pensioners = st.number_input("Důchodci (mil.)", 0.5, 5.0, PENSIONERS, 0.01, "%.2f", key="w_pensioners")
    unemployed = st.number_input("Nezaměstnaní (mil.)", 0.0, 2.0, UNEMPLOYED, 0.01, "%.2f", key="w_unemployed")
    avg_wage   = st.number_input("Průměrná mzda (Kč/měs.)", 20000, 150000, AVG_WAGE, 500, key="w_avg_wage")
    avg_pension= st.number_input("Průměrný důchod (Kč/měs.)", 5000, 60000, AVG_PENSION, 100, key="w_avg_pension")
    avg_unemp  = st.number_input("Podpora v nezam. (Kč/měs.)", 0, 40000, AVG_UNEMP, 100, key="w_avg_unemp")

    st.markdown("---")
    st.header("📐 Daňové sazby (%)")
    vat_basic   = st.slider("DPH základní", 0, 35, 21, key="w_vat_basic")
    vat_reduced = st.slider("DPH snížená", 0, 25, 12, key="w_vat_reduced")
    dpfo_rate   = st.slider("DPFO (zákonná)", 0, 50, 15, key="w_dpfo_rate")
    dppo_rate   = st.slider("DPPO", 0, 40, 21, key="w_dppo_rate")
    soc_emp     = st.slider("Pojistné – zaměstnavatel (%)", 0, 50, 34, key="w_soc_emp")
    soc_empl    = st.slider("Pojistné – zaměstnanec (%)", 0, 30, 12, key="w_soc_empl")

    st.markdown("---")
    st.header("🏦 Dluh")
    debt_sr_mld = st.number_input("Státní dluh (mld Kč)", 0.0, 10000.0, DEBT_SR, 10.0, "%.0f", key="w_debt_sr")
    debt_gs_mld = st.number_input("Dluh vládního sektoru (mld Kč)", 0.0, 12000.0,
                                   round(DEBT_GS, 0), 10.0, "%.0f", key="w_debt_gs")
    interest_sr = st.slider("Úr. sazba – státní dluh (%)", 0.0, 15.0, 2.8, 0.1, key="w_interest_sr")
    interest_gs = st.slider("Úr. sazba – vládní sektor (%)", 0.0, 15.0, 3.0, 0.1, key="w_interest_gs")

# ─────────────────────────────────────────────────────────────────────────────
# POMOCNÉ FUNKCE
# ─────────────────────────────────────────────────────────────────────────────
def scale_from_sazby(base_rev: dict, base_exp: dict) -> tuple[dict, dict]:
    """
    Přepočítá příjmy/výdaje dle změněných sazeb a makroparametrů.
    Přístup: lineární škálování klíčových daní od zákonné sazby.
    """
    rev = dict(base_rev)
    exp = dict(base_exp)
    # Koeficienty změny sazeb (vůči defaultu)
    k_vat  = ((vat_basic * 0.65 + vat_reduced * 0.35) /
              (21 * 0.65 + 12 * 0.35))
    k_dpfo = dpfo_rate / 15.0
    k_dppo = dppo_rate / 21.0
    k_soc  = (soc_emp + soc_empl) / (34 + 12)
    k_wage = (workforce * avg_wage) / (WORKFORCE * AVG_WAGE)
    k_pens = (pensioners * avg_pension) / (PENSIONERS * AVG_PENSION)
    k_unemp= (unemployed * avg_unemp) / (UNEMPLOYED * AVG_UNEMP)

    rev["DPH"]                               = base_rev["DPH"] * k_vat
    rev["DPFO"]                              = base_rev["DPFO"] * k_dpfo * k_wage
    rev["DPPO"]                              = base_rev["DPPO"] * k_dppo
    rev["Pojistné na soc. zabezpečení"]      = base_rev["Pojistné na soc. zabezpečení"] * k_soc * k_wage
    exp["Důchody"]                           = base_exp["Důchody"] * k_pens
    exp["Podpora v nezaměstnanosti"]         = base_exp["Podpora v nezaměstnanosti"] * k_unemp
    exp["Obsluha státního dluhu"]            = debt_sr_mld * interest_sr / 100
    return rev, exp

def scale_gs(base_rev_pct: dict, base_exp_pct: dict) -> tuple[dict, dict]:
    rev = {k: gdp * v / 100 for k, v in base_rev_pct.items()}
    exp = {k: gdp * v / 100 for k, v in base_exp_pct.items()}
    # Přepočet klíčových daní dle sazeb
    k_vat  = ((vat_basic * 0.65 + vat_reduced * 0.35) / (21 * 0.65 + 12 * 0.35))
    k_dpfo = dpfo_rate / 15.0
    k_dppo = dppo_rate / 21.0
    k_soc  = (soc_emp + soc_empl) / (34 + 12)
    k_pens = (pensioners * avg_pension) / (PENSIONERS * AVG_PENSION)
    k_unemp= (unemployed * avg_unemp) / (UNEMPLOYED * AVG_UNEMP)
    k_wage = (workforce * avg_wage) / (WORKFORCE * AVG_WAGE)
    rev["DPH (celý výnos)"]                  = GDP_DEFAULT * 7.0/100 * k_vat * (gdp/GDP_DEFAULT)
    rev["DPFO (celý výnos)"]                 = GDP_DEFAULT * 4.5/100 * k_dpfo * k_wage * (gdp/GDP_DEFAULT)
    rev["DPPO (celý výnos)"]                 = GDP_DEFAULT * 3.5/100 * k_dppo * (gdp/GDP_DEFAULT)
    rev["Sociální pojistné (celý systém)"]   = GDP_DEFAULT * 15.8/100 * k_soc * k_wage * (gdp/GDP_DEFAULT)
    rev["Zdravotní pojistné (VZP)"]          = GDP_DEFAULT * 4.8/100 * k_soc * k_wage * (gdp/GDP_DEFAULT)
    exp["Důchody a penze"]                   = GDP_DEFAULT * 10.2/100 * k_pens * (gdp/GDP_DEFAULT)
    exp["Sociální dávky (ostatní)"]          = GDP_DEFAULT *  3.2/100 * k_unemp * (gdp/GDP_DEFAULT)
    exp["Obsluha dluhu"]                     = debt_gs_mld * interest_gs / 100
    return rev, exp

def metrics_row(rev, exp, debt, interest_rate_pct, label="SR"):
    total_r = sum(rev.values())
    total_e = sum(exp.values())
    bal = total_r - total_e
    debt_next = debt - bal
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric(f"Příjmy {label}", f"{total_r:,.1f} mld Kč",
              delta=f"{total_r/gdp*100:.1f} % HDP")
    c2.metric(f"Výdaje {label}", f"{total_e:,.1f} mld Kč",
              delta=f"{total_e/gdp*100:.1f} % HDP")
    c3.metric("Saldo", f"{bal:,.1f} mld Kč",
              delta=f"{bal/gdp*100:+.1f} % HDP",
              delta_color="normal" if bal >= 0 else "inverse")
    c4.metric("Dluh", f"{debt:,.0f} mld Kč",
              delta=f"{debt/gdp*100:.1f} % HDP", delta_color="off")
    c5.metric("Dluh za rok", f"{debt_next:,.0f} mld Kč",
              delta=f"{(debt_next-debt)/gdp*100:+.1f} p.b.",
              delta_color="inverse" if debt_next > debt else "normal")
    return total_r, total_e, bal

def charts(rev: dict, exp: dict, title_r: str, title_e: str):
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(title_r)
        df_r = pd.DataFrame({"Položka": list(rev.keys()), "Hodnota": list(rev.values())})
        fig = px.pie(df_r, names="Položka", values="Hodnota", hole=0.42,
                     color_discrete_sequence=px.colors.qualitative.Set3)
        fig.update_layout(height=460, margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader(title_e)
        df_e = pd.DataFrame({"Položka": list(exp.keys()), "Hodnota": list(exp.values())})
        fig = px.pie(df_e, names="Položka", values="Hodnota", hole=0.42,
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(height=460, margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        df_r2 = df_r.sort_values("Hodnota")
        df_r2["% HDP"] = df_r2["Hodnota"].apply(lambda x: f"{x/gdp*100:.1f} %")
        fig2 = px.bar(df_r2, y="Položka", x="Hodnota", orientation="h",
                      text=df_r2["Hodnota"].map(lambda x: f"{x:,.0f}"),
                      color="Hodnota", color_continuous_scale="Greens",
                      labels={"Hodnota": "mld Kč"})
        fig2.update_layout(height=420, showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)
    with col4:
        df_e2 = df_e.sort_values("Hodnota")
        fig3 = px.bar(df_e2, y="Položka", x="Hodnota", orientation="h",
                      text=df_e2["Hodnota"].map(lambda x: f"{x:,.0f}"),
                      color="Hodnota", color_continuous_scale="Reds",
                      labels={"Hodnota": "mld Kč"})
        fig3.update_layout(height=520, showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig3, use_container_width=True)

def detail_table(rev, exp):
    rows = []
    for k, v in rev.items():
        rows.append({"Sekce": "📥 Příjmy", "Položka": k,
                     "Hodnota (mld Kč)": f"{v:,.1f}", "% HDP": f"{v/gdp*100:.2f} %"})
    rows.append({"Sekce": "📥 Příjmy", "Položka": "━━ CELKEM PŘÍJMY",
                 "Hodnota (mld Kč)": f"{sum(rev.values()):,.1f}",
                 "% HDP": f"{sum(rev.values())/gdp*100:.1f} %"})
    for k, v in exp.items():
        rows.append({"Sekce": "📤 Výdaje", "Položka": k,
                     "Hodnota (mld Kč)": f"{v:,.1f}", "% HDP": f"{v/gdp*100:.2f} %"})
    bal = sum(rev.values()) - sum(exp.values())
    rows.append({"Sekce": "📤 Výdaje", "Položka": "━━ CELKEM VÝDAJE",
                 "Hodnota (mld Kč)": f"{sum(exp.values()):,.1f}",
                 "% HDP": f"{sum(exp.values())/gdp*100:.1f} %"})
    rows.append({"Sekce": "⚖️ Saldo", "Položka": "SALDO",
                 "Hodnota (mld Kč)": f"{bal:,.1f}",
                 "% HDP": f"{bal/gdp*100:+.1f} %"})
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

def debt_projection(debt_start, rev, exp, label):
    st.subheader(f"📈 10letá projekce dluhu – {label}")
    primary = sum(exp.values()) - debt_start * (interest_sr if "SR" in label else interest_gs) / 100
    d, d_pct = [debt_start], [debt_start/gdp*100]
    for _ in range(10):
        interest = d[-1] * (interest_sr if "SR" in label else interest_gs) / 100
        bal_y = sum(rev.values()) - (primary + interest)
        d.append(d[-1] - bal_y)
        d_pct.append(d[-1] / gdp * 100)
    cl, cr = st.columns(2)
    with cl:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=list(range(11)), y=d_pct, mode="lines+markers",
                                 line=dict(color="#e74c3c", width=3)))
        fig.add_hline(y=60, line_dash="dash", line_color="orange",
                      annotation_text="Maastricht 60 %")
        fig.update_layout(height=300, xaxis_title="Rok", yaxis_title="Dluh / HDP (%)")
        st.plotly_chart(fig, use_container_width=True)
    with cr:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=list(range(11)), y=d, mode="lines+markers",
                                  fill="tozeroy", line=dict(color="#f59e0b", width=3)))
        fig2.update_layout(height=300, xaxis_title="Rok", yaxis_title="Dluh (mld Kč)")
        st.plotly_chart(fig2, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# HLAVNÍ OBSAH – TABY
# ─────────────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["📋 Státní rozpočet", "🏛️ Vládní sektor"])

# ── TAB 1: STÁTNÍ ROZPOČET ───────────────────────────────────────────────────
with tab1:
    st.caption(
        "**Státní rozpočet (centrální vláda)** – nezahrnuje rozpočty krajů, obcí ani zdravotní pojišťovny. "
        "Základní hodnoty = **plán SR 2025** dle zákona č. 434/2024 Sb.  "
        "Příjmy 2 086,1 mld Kč | Výdaje 2 327,1 mld Kč | Saldo −241,0 mld Kč. "
        "Zdroj: MFČR, Státní rozpočet 2025 v kostce (aktualizace 11. 3. 2025)."
    )

    sr_rev, sr_exp = scale_from_sazby(SR_REV_DEFAULT, SR_EXP_DEFAULT)
    metrics_row(sr_rev, sr_exp, debt_sr_mld, interest_sr, "SR")

    st.markdown("---")
    st.subheader("👥 Populační ukazatele")
    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Zaměstnaní", f"{workforce:.2f} mil.", delta=f"mzda {avg_wage:,} Kč/měs.")
    p2.metric("Důchodci", f"{pensioners:.2f} mil.", delta=f"důchod {avg_pension:,} Kč/měs.")
    p3.metric("Nezaměstnaní", f"{unemployed:.2f} mil.", delta=f"podpora {avg_unemp:,} Kč/měs.")
    p4.metric("HDP na obyvatele", f"{gdp/(workforce+pensioners+unemployed)*1000:.0f} tis. Kč",
              delta_color="off")

    st.markdown("---")
    charts(sr_rev, sr_exp, "Struktura příjmů SR", "Struktura výdajů SR")
    st.markdown("---")
    with st.expander("📋 Detailní tabulka"):
        detail_table(sr_rev, sr_exp)
    st.markdown("---")
    debt_projection(debt_sr_mld, sr_rev, sr_exp, "Státní rozpočet")

    st.markdown("---")
    st.info(
        "💡 **Jak číst koeficienty?**  "
        "Pojistné (809 mld) = zaměstnavatel 34 % + zaměstnanec 12 % z hrubých mezd, ale do SR jde jen "
        "část (~59 %) – zbytek jde do systému zdravotního pojištění (VZP a ostatní pojišťovny). "
        "DPH (414 mld) je po sdílení s obcemi a kraji. DPFO (185 mld) je po sdílení ~74 % do SR."
    )

# ── TAB 2: VLÁDNÍ SEKTOR ────────────────────────────────────────────────────
with tab2:
    st.caption(
        "**Vládní sektor (general government)** = státní rozpočet + státní fondy + kraje + obce + "
        "zdravotní pojišťovny + mimorozpočtové fondy. "
        "Základní hodnoty = **odhad 2025** dle MFČR a Eurostatu.  "
        "Příjmy ~43,5 % HDP | Výdaje ~45,8 % HDP | Saldo −2,3 % HDP | Dluh 44,3 % HDP. "
        "Zdroj: MFČR SR v kostce 2025, Eurostat GFS."
    )

    gs_rev, gs_exp = scale_gs(GS_REV_PCT, GS_EXP_PCT)
    metrics_row(gs_rev, gs_exp, debt_gs_mld, interest_gs, "Vládní sektor")

    st.markdown("---")
    charts(gs_rev, gs_exp, "Struktura příjmů – vládní sektor", "Struktura výdajů – vládní sektor")

    st.markdown("---")
    st.subheader("🔍 Srovnání: Státní rozpočet vs. Vládní sektor")
    sr_r_tot = sum(sr_rev.values())
    sr_e_tot = sum(sr_exp.values())
    gs_r_tot = sum(gs_rev.values())
    gs_e_tot = sum(gs_exp.values())
    comp = pd.DataFrame({
        "Ukazatel": ["Příjmy (mld Kč)", "Výdaje (mld Kč)", "Saldo (mld Kč)",
                     "Příjmy (% HDP)", "Výdaje (% HDP)", "Saldo (% HDP)",
                     "Dluh (mld Kč)", "Dluh (% HDP)"],
        "Státní rozpočet": [
            f"{sr_r_tot:,.1f}", f"{sr_e_tot:,.1f}", f"{sr_r_tot-sr_e_tot:,.1f}",
            f"{sr_r_tot/gdp*100:.1f} %", f"{sr_e_tot/gdp*100:.1f} %",
            f"{(sr_r_tot-sr_e_tot)/gdp*100:+.1f} %",
            f"{debt_sr_mld:,.0f}", f"{debt_sr_mld/gdp*100:.1f} %"
        ],
        "Vládní sektor": [
            f"{gs_r_tot:,.1f}", f"{gs_e_tot:,.1f}", f"{gs_r_tot-gs_e_tot:,.1f}",
            f"{gs_r_tot/gdp*100:.1f} %", f"{gs_e_tot/gdp*100:.1f} %",
            f"{(gs_r_tot-gs_e_tot)/gdp*100:+.1f} %",
            f"{debt_gs_mld:,.0f}", f"{debt_gs_mld/gdp*100:.1f} %"
        ],
    })
    st.dataframe(comp, use_container_width=True, hide_index=True)

    st.markdown("---")
    with st.expander("📋 Detailní tabulka – vládní sektor"):
        detail_table(gs_rev, gs_exp)
    st.markdown("---")
    debt_projection(debt_gs_mld, gs_rev, gs_exp, "Vládní sektor")

    st.markdown("---")
    st.info(
        "💡 **Rozdíl SR vs. vládní sektor:**  "
        "Zdravotnictví v SR = jen platba státu za pojištěnce státu (154,6 mld); "
        "v vládním sektoru = celkové výdaje zdravotních pojišťoven (~8 % HDP = 672 mld). "
        "Vzdělávání v SR zahrnuje platy pedagogů + dotace ÚSC; "
        "vládní sektor navíc zahrnuje výdaje obcí a krajů na školy."
    )

st.markdown("---")
st.caption(
    "⚠️ **Výukový simulátor** – hodnoty jsou lineárně škálovány dle nastavených parametrů od základu 2025. "
    "Skutečnost závisí na mnoha dalších faktorech (daňová morálka, hospodářský cyklus, jednorázová opatření). "
    "Příjmová strana SR 2025 (plán): pojistné 809,4 | DPH 414,0 | DPPO 244,3 | DPFO 184,7 | "
    "spotřební 161,1 | transfery EU 172,5 | ostatní 99,1 = **2 086,1 mld Kč**. "
    "Skutečnost 2025: schodek 290,7 mld Kč (leden 2026, MFČR)."
)
