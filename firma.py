import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Firm Equilibrium V3", layout="wide", page_icon="📈")

# ═══════════════════════════════════════════════════
#  LANGUAGE SYSTEM
# ═══════════════════════════════════════════════════
T = {
    "title":          ("📈 Firm Equilibrium Simulator V3",     "📈 Simulátor rovnováhy firmy V3"),
    "subtitle":       ("Interactive simulation of firm equilibrium across market structures.",
                       "Interaktivní simulace rovnováhy firmy v různých tržních strukturách."),
    # Sidebar headers
    "s_lang":         ("🌐 Language",                          "🌐 Jazyk"),
    "s_structure":    ("⚙️ Market Structure",                  "⚙️ Tržní struktura"),
    "s_cost":         ("💰 Cost Parameters",                   "💰 Nákladové parametry"),
    "s_demand":       ("🏪 Demand / Market",                   "🏪 Poptávka / Trh"),
    "s_shifts":       ("📈 Market Shift Factors",              "📈 Faktory posunu trhu"),
    # Market structures
    "perf_comp":      ("Perfect Competition",                  "Dokonalá konkurence"),
    "monopoly":       ("Monopoly",                             "Monopol"),
    "mono_comp":      ("Monopolistic Competition",             "Monopolistická konkurence"),
    "duopoly":        ("Duopoly (Cournot)",                    "Duopol (Cournot)"),
    # LR toggle
    "lr_toggle":      ("🔄 Long-Run Equilibrium",             "🔄 Dlouhodobá rovnováha"),
    "lr_help":        ("Snap to long-run equilibrium",         "Přepnout do dlouhodobé rovnováhy"),
    # Cost sliders
    "fc":             ("Fixed Cost (FC)",                      "Fixní náklady (FC)"),
    "var_c":          ("Variable cost coeff (c)",              "Variabilní náklad koef. (c)"),
    "var_d":          ("Variable cost coeff (d)",              "Variabilní náklad koef. (d)"),
    "vc_help":        ("VC = c·Q + d·Q²",                     "VC = c·Q + d·Q²"),
    # Demand sliders
    "intercept_a":    ("Demand intercept (a)",                 "Intercept poptávky (a)"),
    "slope_b":        ("Demand slope (b)",                     "Sklon poptávky (b)"),
    "market_price":   ("Market Price (P)",                     "Tržní cena (P)"),
    "n_firms":        ("Number of firms (n)",                  "Počet firem (n)"),
    "firm2_c":        ("Firm 2 cost coeff c₂",                "Firma 2 koef. c₂"),
    "firm2_d":        ("Firm 2 cost coeff d₂",                "Firma 2 koef. d₂"),
    # Shift factors - Demand
    "dem_factors":    ("**Demand Shifters**",                  "**Posuny poptávky**"),
    "pref":           ("Consumer Preferences",                 "Preference spotřebitelů"),
    "pref_help":      ("Taste/fashion shifts demand",          "Změna preferencí posune D"),
    "consumers":      ("Number of Consumers",                  "Počet spotřebitelů"),
    "consumers_help": ("More buyers shift D right",            "Více kupujících posune D vpravo"),
    "income":         ("Income Change",                        "Změna příjmu"),
    "income_help":    ("Higher income shifts D (normal good)", "Vyšší příjem posune D (normální statek)"),
    "substitutes":    ("Price of Substitutes",                 "Cena substitutů"),
    "subst_help":     ("Higher sub. price shifts D right",     "Vyšší cena sub. posune D vpravo"),
    # Shift factors - Supply
    "sup_factors":    ("**Supply / Cost Shifters**",           "**Posuny nabídky / nákladů**"),
    "input_cost":     ("Input Costs",                          "Náklady vstupů"),
    "input_help":     ("Higher input costs shift S left",      "Vyšší náklady vstupů posune S vlevo"),
    "technology":     ("Technology Level",                     "Úroveň technologie"),
    "tech_help":      ("Better tech lowers costs, shifts S right","Lepší technologie sníží náklady"),
    "tax":            ("Tax (+) / Subsidy (−)",                "Daň (+) / Dotace (−)"),
    "tax_help":       ("Per-unit tax or subsidy on cost",      "Jednotková daň nebo dotace"),
    "reset_shifts":   ("Reset all shifts",                     "Resetovat posuny"),
    # Tabs
    "tab_market":     ("🏪 Market Overview",                   "🏪 Přehled trhu"),
    "tab_firm":       ("🏢 Firm Equilibrium",                  "🏢 Rovnováha firmy"),
    "tab_statics":    ("📊 Comparative Statics",               "📊 Komparativní statika"),
    # Chart labels
    "ch_mc":          ("MC",                                   "MC"),
    "ch_atc":         ("ATC",                                  "ATC"),
    "ch_avc":         ("AVC",                                  "AVC"),
    "ch_demand":      ("Demand",                               "Poptávka"),
    "ch_mr":          ("MR",                                   "MR"),
    "ch_quantity":    ("Quantity (Q)",                         "Množství (Q)"),
    "ch_price":       ("Price / Cost",                         "Cena / Náklady"),
    "ch_profit":      ("Profit",                               "Zisk"),
    "ch_price_only":  ("Price",                                "Cena"),
    "ch_mkt_demand":  ("Market Demand",                        "Tržní poptávka"),
    "ch_mkt_supply":  ("Market Supply",                        "Tržní nabídka"),
    "ch_base":        ("Base (before shift)",                  "Základ (před posunem)"),
    "ch_shifted":     ("After shift",                          "Po posunu"),
    "ch_firm_d":      ("Firm Demand (d)",                      "Poptávka firmy (d)"),
    "ch_dwl":         ("Deadweight Loss",                      "Ztráta mrtvé váhy"),
    # Metrics
    "m_eq":           ("Equilibrium",                          "Rovnováha"),
    "m_q_star":       ("Q*",                                   "Q*"),
    "m_p_star":       ("P*",                                   "P*"),
    "m_atc_q":        ("ATC at Q*",                            "ATC při Q*"),
    "m_tr":           ("Total Revenue",                        "Celkový příjem"),
    "m_tc":           ("Total Cost",                           "Celkové náklady"),
    "m_profit":       ("Profit (P−ATC)·Q",                    "Zisk (P−ATC)·Q"),
    "m_positive":     ("Positive",                             "Kladný"),
    "m_zero":         ("≈ 0 ✓",                                "≈ 0 ✓"),
    "m_loss":         ("Loss",                                 "Ztráta"),
    "m_supernormal":  ("Supernormal",                          "Nadnormální"),
    "m_lerner":       ("Lerner Index",                         "Lernerův index"),
    "m_excess":       ("Excess Capacity",                      "Nadbytečná kapacita"),
    "m_n_firms":      ("Firms (n)",                            "Počet firem (n)"),
    "m_shutdown":     ("🛑 Shutdown: P < min AVC",             "🛑 Uzavření: P < min AVC"),
    "m_total_q":      ("Total Q",                              "Celkové Q"),
    "m_mkt_price":    ("Market Price",                         "Tržní cena"),
    # LR properties
    "lr_pc":          ("**LR:** P = min ATC → π = 0, allocative + productive efficiency",
                       "**DR:** P = min ATC → π = 0, alokační + produktivní efektivita"),
    "lr_mono":        ("**LR:** MR = MC, barriers → supernormal profit persists, DWL",
                       "**DR:** MR = MC, bariéry → nadnormální zisk přetrvává, DWL"),
    "lr_mc":          ("**LR:** Tangency P = ATC → π = 0, excess capacity",
                       "**DR:** Tangence P = ATC → π = 0, nadbytečná kapacita"),
    "lr_duo":         ("**LR:** Nash eq., barriers → profit may persist",
                       "**DR:** Nashova rovnováha, bariéry → zisk může přetrvávat"),
    # Market tab titles
    "mkt_title_pc":   ("Market: Aggregate Supply & Demand",    "Trh: Agregátní nabídka a poptávka"),
    "mkt_title_mon":  ("Market: Monopoly Demand & Costs",      "Trh: Monopolní poptávka a náklady"),
    "mkt_title_mc":   ("Market: Monopolistic Competition",     "Trh: Monopolistická konkurence"),
    "mkt_title_duo":  ("Market: Cournot Duopoly",              "Trh: Cournotův duopol"),
    "mkt_eff_params": ("Effective Parameters (after shifts)",   "Efektivní parametry (po posunech)"),
    "mkt_base_params":("Base Parameters",                      "Základní parametry"),
    # Statics
    "vary_param":     ("Vary parameter:",                      "Měnit parametr:"),
    "statics_title":  ("Comparative Statics",                  "Komparativní statika"),
    # Reference
    "ref_title":      ("📖 Model Equations",                   "📖 Rovnice modelu"),
    "footer":         ("Firm Equilibrium Simulator V3",        "Simulátor rovnováhy firmy V3"),
}

# ─── Language selector ───
lang_sel = st.sidebar.radio("🌐", ["EN", "CZ"], horizontal=True, label_visibility="collapsed")
LI = 0 if lang_sel == "EN" else 1
def t(k): return T[k][LI]

# ───────────────────────────────────────────────────
st.title(t("title"))
st.markdown(t("subtitle"))

# ═══════════════════════════════════════════════════
#  SIDEBAR: Structure, LR, Cost, Demand
# ═══════════════════════════════════════════════════
structs = [t("perf_comp"), t("monopoly"), t("mono_comp"), t("duopoly")]
struct_keys = ["pc", "mon", "mc", "duo"]
st.sidebar.header(t("s_structure"))
market_label = st.sidebar.selectbox(t("s_structure"), structs, label_visibility="collapsed")
mk = struct_keys[structs.index(market_label)]

lr = st.sidebar.toggle(t("lr_toggle"), value=False, help=t("lr_help"))

st.sidebar.header(t("s_cost"))
FC = st.sidebar.slider(t("fc"), 0, 500, 100, 10)
c1 = st.sidebar.slider(t("var_c"), 1.0, 50.0, 10.0, 0.5, help=t("vc_help"))
d1 = st.sidebar.slider(t("var_d"), 0.01, 2.0, 0.50, 0.01, help=t("vc_help"))

st.sidebar.header(t("s_demand"))
if mk == "pc":
    P_input = st.sidebar.slider(t("market_price"), 5.0, 100.0, 40.0, 0.5)
    a_base = 100.0; b_base = 1.0
else:
    a_base = st.sidebar.slider(t("intercept_a"), 20.0, 200.0, 100.0, 1.0)
    b_base = st.sidebar.slider(t("slope_b"), 0.1, 5.0, 1.0, 0.05)
if mk == "mc":
    n_input = st.sidebar.slider(t("n_firms"), 2, 20, 5)
if mk == "duo":
    c2 = st.sidebar.slider(t("firm2_c"), 1.0, 50.0, 10.0, 0.5)
    d2 = st.sidebar.slider(t("firm2_d"), 0.01, 2.0, 0.50, 0.01)

# ═══════════════════════════════════════════════════
#  SIDEBAR: Market Shift Factors
# ═══════════════════════════════════════════════════
st.sidebar.header(t("s_shifts"))
with st.sidebar.expander(t("dem_factors"), expanded=False):
    pref_mult = st.slider(t("pref"), 0.5, 1.5, 1.0, 0.05, help=t("pref_help"))
    cons_mult = st.slider(t("consumers"), 0.5, 2.0, 1.0, 0.05, help=t("consumers_help"))
    income_sh = st.slider(t("income"), -30.0, 30.0, 0.0, 1.0, help=t("income_help"))
    subst_sh  = st.slider(t("substitutes"), -20.0, 20.0, 0.0, 1.0, help=t("subst_help"))

with st.sidebar.expander(t("sup_factors"), expanded=False):
    input_mult = st.slider(t("input_cost"), 0.5, 2.0, 1.0, 0.05, help=t("input_help"))
    tech_mult  = st.slider(t("technology"), 0.5, 1.5, 1.0, 0.05, help=t("tech_help"))
    tax_sh     = st.slider(t("tax"), -10.0, 10.0, 0.0, 0.5, help=t("tax_help"))

if st.sidebar.button(t("reset_shifts")):
    st.rerun()

# ─── Compute effective parameters ───
a_eff = a_base * pref_mult * cons_mult + income_sh + subst_sh
c_eff = c1 * input_mult / tech_mult + tax_sh
d_eff = d1 / tech_mult
c_eff = max(c_eff, 0.1)
d_eff = max(d_eff, 0.01)

has_shift = (pref_mult!=1.0 or cons_mult!=1.0 or income_sh!=0 or subst_sh!=0
             or input_mult!=1.0 or tech_mult!=1.0 or tax_sh!=0)

# ═══════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════
QR = np.linspace(0.1, 150, 800)
COL = dict(demand="#2196F3", mr="#FF9800", mc="#E53935", atc="#4CAF50",
           avc="#8BC34A", eq="#FFD600", dwl="#FF9800", firm2="#9C27B0",
           base_d="#90CAF9", base_s="#EF9A9A", shift_d="#1565C0", shift_s="#B71C1C",
           react1="#2196F3", react2="#E53935",
           profit_fill="rgba(129,212,250,0.35)", profit_line="rgba(33,150,243,0.6)",
           loss_fill="rgba(239,154,154,0.35)", loss_line="rgba(229,57,53,0.6)")

def cc(Q, fc, c, d):
    TC = fc + c*Q + d*Q**2
    MC = c + 2*d*Q
    with np.errstate(divide="ignore", invalid="ignore"):
        ATC = np.where(Q>0, TC/Q, np.nan)
        AVC = np.where(Q>0, (c*Q + d*Q**2)/Q, np.nan)
    return TC, MC, ATC, AVC

def min_atc(fc, c, d):
    Qe = np.sqrt(fc/d) if fc>0 and d>0 else 1.0
    return Qe, fc/Qe + c + d*Qe

def profit_rect(fig, Qs, Ps, ATCs, row=None, col=None):
    pi = (Ps - ATCs)*Qs
    if Qs <= 0: return pi
    xs = [0, Qs, Qs, 0, 0]
    if pi >= 0:
        ys = [Ps, Ps, ATCs, ATCs, Ps]
        fc, lc = COL["profit_fill"], COL["profit_line"]
    else:
        ys = [ATCs, ATCs, Ps, Ps, ATCs]
        fc, lc = COL["loss_fill"], COL["loss_line"]
    tr = go.Scatter(x=xs, y=ys, fill="toself", fillcolor=fc,
                    line=dict(width=1.5, color=lc),
                    name=f"{t('ch_profit')} = {pi:.1f}")
    if row: fig.add_trace(tr, row=row, col=col)
    else: fig.add_trace(tr)
    return pi

def eqm(fig, x, y, label, row=None, col=None, sym="circle"):
    kw = dict(x=[x], y=[y], mode="markers+text", text=[f"  {label}"],
              textposition="top right",
              marker=dict(size=12, color=COL["eq"], symbol=sym,
                          line=dict(width=2, color="black")),
              name=label)
    if row: fig.add_trace(go.Scatter(**kw), row=row, col=col)
    else: fig.add_trace(go.Scatter(**kw))

# ─── Precompute ───
TC_e, MC_e, ATC_e, AVC_e = cc(QR, FC, c_eff, d_eff)
TC_b, MC_b, ATC_b, AVC_b = cc(QR, FC, c1, d1)
Qe_eff, ATCmin_eff = min_atc(FC, c_eff, d_eff)
Qe_base, ATCmin_base = min_atc(FC, c1, d1)

# ─── LR adjustments ───
if mk == "pc":
    P_m = ATCmin_eff if lr else P_input
    if lr: st.sidebar.info(f"🔄 LR: P → min ATC = {ATCmin_eff:.2f}")
if mk == "mc":
    if lr:
        best_n, best_err = 1.0, 1e15
        for nt in np.arange(1.0, 200, 0.05):
            bf = b_base*(1+0.3*(nt-1)); af = a_eff/(nt**0.4)
            qs = (af - c_eff)/(2*bf + 2*d_eff)
            if qs <= 0: break
            ps = af - bf*qs
            err = abs(ps*qs - (FC + c_eff*qs + d_eff*qs**2))
            if err < best_err: best_err=err; best_n=nt
        n_f = best_n
        st.sidebar.info(f"🔄 LR: n ≈ {best_n:.1f}")
    else:
        n_f = n_input

# ═══════════════════════════════════════════════════
#  TABS
# ═══════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs([t("tab_market"), t("tab_firm"), t("tab_statics")])

# ─────────────────────────────────────────────────
#  TAB 1: MARKET OVERVIEW
# ─────────────────────────────────────────────────
with tab1:
    if mk == "pc":
        # Aggregate S & D
        N_mkt = 50
        # Base curves
        Pd_b = a_base - b_base*QR
        Ps_b = c1 + 2*d1*QR/N_mkt
        Qeq_b = (a_base - c1)/(b_base + 2*d1/N_mkt)
        Peq_b = a_base - b_base*Qeq_b
        # Shifted curves
        Pd_s = a_eff - b_base*QR
        Ps_s = c_eff + 2*d_eff*QR/N_mkt
        Qeq_s = max((a_eff - c_eff)/(b_base + 2*d_eff/N_mkt), 0)
        Peq_s = a_eff - b_base*Qeq_s

        fig = go.Figure()
        m = Pd_b >= 0
        if has_shift:
            fig.add_trace(go.Scatter(x=QR[m], y=Pd_b[m], name=f"D {t('ch_base')}",
                line=dict(color=COL["base_d"], width=2, dash="dash")))
            fig.add_trace(go.Scatter(x=QR, y=Ps_b, name=f"S {t('ch_base')}",
                line=dict(color=COL["base_s"], width=2, dash="dash")))
            eqm(fig, Qeq_b, Peq_b, f"E₀ ({Qeq_b:.0f}, {Peq_b:.1f})", sym="diamond")
        ms = Pd_s >= 0
        fig.add_trace(go.Scatter(x=QR[ms], y=Pd_s[ms], name=t("ch_mkt_demand"),
            line=dict(color=COL["shift_d"], width=2.5)))
        fig.add_trace(go.Scatter(x=QR, y=Ps_s, name=t("ch_mkt_supply"),
            line=dict(color=COL["shift_s"], width=2.5)))
        eqm(fig, Qeq_s, Peq_s, f"E₁ ({Qeq_s:.0f}, {Peq_s:.1f})", sym="star")

        fig.update_layout(title=t("mkt_title_pc"), xaxis_title=t("ch_quantity"),
                          yaxis_title=t("ch_price_only"),
                          yaxis=dict(range=[0, max(a_base, a_eff)*1.1]),
                          xaxis=dict(range=[0, max(Qeq_b, Qeq_s)*2.5]),
                          template="plotly_white", height=500)
        st.plotly_chart(fig, use_container_width=True)

    elif mk == "mon":
        Pd_b = a_base - b_base*QR; MRb = a_base - 2*b_base*QR
        Pd_s = a_eff  - b_base*QR; MRs = a_eff  - 2*b_base*QR
        fig = go.Figure()
        if has_shift:
            m=Pd_b>=0; fig.add_trace(go.Scatter(x=QR[m],y=Pd_b[m],name=f"D {t('ch_base')}",line=dict(color=COL["base_d"],width=2,dash="dash")))
            m=MRb>=-10; fig.add_trace(go.Scatter(x=QR[m],y=MRb[m],name=f"MR {t('ch_base')}",line=dict(color="#FFE0B2",width=2,dash="dash")))
            fig.add_trace(go.Scatter(x=QR,y=MC_b,name=f"MC {t('ch_base')}",line=dict(color=COL["base_s"],width=2,dash="dash")))
        m=Pd_s>=0; fig.add_trace(go.Scatter(x=QR[m],y=Pd_s[m],name=t("ch_demand"),line=dict(color=COL["shift_d"],width=2.5)))
        m=MRs>=-10; fig.add_trace(go.Scatter(x=QR[m],y=MRs[m],name=t("ch_mr"),line=dict(color=COL["mr"],width=2.5)))
        fig.add_trace(go.Scatter(x=QR,y=MC_e,name=t("ch_mc"),line=dict(color=COL["mc"],width=2.5)))

        Qs_m = max((a_eff-c_eff)/(2*b_base+2*d_eff),0)
        Ps_m = a_eff - b_base*Qs_m
        eqm(fig, Qs_m, Ps_m, f"E ({Qs_m:.1f}, {Ps_m:.1f})", sym="star")
        fig.update_layout(title=t("mkt_title_mon"), xaxis_title=t("ch_quantity"),
                          yaxis_title=t("ch_price_only"),
                          yaxis=dict(range=[0, max(a_base,a_eff)*1.1]),
                          xaxis=dict(range=[0, max(a_base,a_eff)/b_base*1.1]),
                          template="plotly_white", height=500)
        st.plotly_chart(fig, use_container_width=True)

    elif mk == "mc":
        bf = b_base*(1+0.3*(n_f-1)); af = a_eff/(n_f**0.4)
        Pd_f = af - bf*QR; MR_f = af - 2*bf*QR
        fig = go.Figure()
        m=Pd_f>=0; fig.add_trace(go.Scatter(x=QR[m],y=Pd_f[m],name=t("ch_firm_d"),line=dict(color=COL["demand"],width=2.5)))
        m=MR_f>=-10; fig.add_trace(go.Scatter(x=QR[m],y=MR_f[m],name=t("ch_mr"),line=dict(color=COL["mr"],width=2.5)))
        fig.add_trace(go.Scatter(x=QR,y=MC_e,name=t("ch_mc"),line=dict(color=COL["mc"],width=2.5)))
        fig.add_trace(go.Scatter(x=QR,y=ATC_e,name=t("ch_atc"),line=dict(color=COL["atc"],width=2,dash="dash")))
        Qs_mc = max((af-c_eff)/(2*bf+2*d_eff),0)
        Ps_mc = af - bf*Qs_mc
        eqm(fig, Qs_mc, Ps_mc, f"E ({Qs_mc:.1f}, {Ps_mc:.1f})", sym="star")
        fig.update_layout(title=t("mkt_title_mc"), xaxis_title=t("ch_quantity"),
                          yaxis_title=t("ch_price_only"),
                          yaxis=dict(range=[0, max(af*1.2,80)]),
                          xaxis=dict(range=[0, af/bf*1.2 if bf>0 else 100]),
                          template="plotly_white", height=500)
        st.plotly_chart(fig, use_container_width=True)

    else:  # duopoly
        Pd_s = a_eff - b_base*QR
        fig = go.Figure()
        if has_shift:
            Pd_b2 = a_base - b_base*QR; m=Pd_b2>=0
            fig.add_trace(go.Scatter(x=QR[m],y=Pd_b2[m],name=f"D {t('ch_base')}",line=dict(color=COL["base_d"],width=2,dash="dash")))
        m=Pd_s>=0; fig.add_trace(go.Scatter(x=QR[m],y=Pd_s[m],name=t("ch_mkt_demand"),line=dict(color=COL["shift_d"],width=2.5)))
        c2_eff = c2*input_mult/tech_mult+tax_sh; c2_eff=max(c2_eff,0.1)
        d2_eff = d2/tech_mult; d2_eff=max(d2_eff,0.01)
        A1=(a_eff-c_eff)/(2*b_base+2*d_eff); B1=b_base/(2*b_base+2*d_eff)
        A2=(a_eff-c2_eff)/(2*b_base+2*d2_eff); B2=b_base/(2*b_base+2*d2_eff)
        det=1-B1*B2
        Q1s=max((A1-B1*A2)/det,0) if abs(det)>1e-10 else 0
        Q2s=max((A2-B2*A1)/det,0) if abs(det)>1e-10 else 0
        Qt=Q1s+Q2s; Ps_duo=max(a_eff-b_base*Qt,0)
        eqm(fig, Qt, Ps_duo, f"Cournot ({Qt:.1f}, {Ps_duo:.1f})", sym="star")
        fig.update_layout(title=t("mkt_title_duo"), xaxis_title=t("ch_quantity"),
                          yaxis_title=t("ch_price_only"),
                          yaxis=dict(range=[0, max(a_base,a_eff)*1.1]),
                          xaxis=dict(range=[0, max(a_base,a_eff)/b_base]),
                          template="plotly_white", height=500)
        st.plotly_chart(fig, use_container_width=True)

    # Show effective vs base parameters
    if has_shift:
        cl, cr = st.columns(2)
        with cl:
            st.markdown(f"**{t('mkt_base_params')}**: a={a_base:.1f}, c={c1:.2f}, d={d1:.3f}")
        with cr:
            st.markdown(f"**{t('mkt_eff_params')}**: a={a_eff:.1f}, c={c_eff:.2f}, d={d_eff:.3f}")

# ─────────────────────────────────────────────────
#  TAB 2: FIRM EQUILIBRIUM
# ─────────────────────────────────────────────────
with tab2:
    if mk == "pc":
        Qs = max((P_m - c_eff)/(2*d_eff), 0)
        shutdown = P_m < c_eff
        TCs = FC + c_eff*Qs + d_eff*Qs**2
        ATCs = TCs/Qs if Qs>0 else 0
        pi = (P_m - ATCs)*Qs if Qs>0 else 0

        c1c, c2c = st.columns([2,1])
        with c1c:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=QR,y=MC_e,name=t("ch_mc"),line=dict(color=COL["mc"],width=2.5)))
            fig.add_trace(go.Scatter(x=QR,y=ATC_e,name=t("ch_atc"),line=dict(color=COL["atc"],width=2,dash="dash")))
            fig.add_trace(go.Scatter(x=QR,y=AVC_e,name=t("ch_avc"),line=dict(color=COL["avc"],width=2,dash="dot")))
            fig.add_hline(y=P_m,line=dict(color=COL["demand"],width=2),
                          annotation_text=f"P = MR = AR = {P_m:.1f}")
            if Qs>0 and not shutdown:
                profit_rect(fig, Qs, P_m, ATCs)
                eqm(fig, Qs, P_m, f"Q*={Qs:.1f}")
                if lr: eqm(fig, Qe_eff, ATCmin_eff, f"min ATC={ATCmin_eff:.1f}", sym="diamond")
            fig.update_layout(title=t("perf_comp")+(" — LR" if lr else ""),
                              xaxis_title=t("ch_quantity"), yaxis_title=t("ch_price"),
                              yaxis=dict(range=[0,max(P_m*2.2,80)]),
                              xaxis=dict(range=[0,min(Qs*3+10,150)]),
                              template="plotly_white",height=520)
            st.plotly_chart(fig, use_container_width=True)
        with c2c:
            st.subheader(t("m_eq"))
            if shutdown: st.error(t("m_shutdown"))
            else:
                st.metric(t("m_q_star"), f"{Qs:.2f}")
                st.metric(t("m_mkt_price"), f"{P_m:.2f}")
                st.metric(t("m_atc_q"), f"{ATCs:.2f}")
                st.metric(t("m_tr"), f"{P_m*Qs:.2f}")
                st.metric(t("m_tc"), f"{TCs:.2f}")
                st.metric(t("m_profit"), f"{pi:.2f}",
                          delta=t("m_positive") if pi>0.5 else (t("m_zero") if abs(pi)<0.5 else t("m_loss")),
                          delta_color="normal" if pi>=-0.5 else "inverse")
            st.markdown("---")
            if lr: st.success(t("lr_pc"))

    elif mk == "mon":
        Qs = max((a_eff-c_eff)/(2*b_base+2*d_eff),0)
        Ps = a_eff - b_base*Qs
        TCs = FC+c_eff*Qs+d_eff*Qs**2; ATCs=TCs/Qs if Qs>0 else 0
        MCs = c_eff+2*d_eff*Qs; MRs = a_eff-2*b_base*Qs
        pi = (Ps-ATCs)*Qs
        Qcomp = max((a_eff-c_eff)/(b_base+2*d_eff),0)
        Pcomp = a_eff-b_base*Qcomp
        Pd = a_eff-b_base*QR; MRc = a_eff-2*b_base*QR

        c1c, c2c = st.columns([2,1])
        with c1c:
            fig = go.Figure()
            m=Pd>=0; fig.add_trace(go.Scatter(x=QR[m],y=Pd[m],name=t("ch_demand"),line=dict(color=COL["demand"],width=2.5)))
            m=MRc>=-20; fig.add_trace(go.Scatter(x=QR[m],y=MRc[m],name=t("ch_mr"),line=dict(color=COL["mr"],width=2.5)))
            fig.add_trace(go.Scatter(x=QR,y=MC_e,name=t("ch_mc"),line=dict(color=COL["mc"],width=2.5)))
            fig.add_trace(go.Scatter(x=QR,y=ATC_e,name=t("ch_atc"),line=dict(color=COL["atc"],width=2,dash="dash")))
            fig.add_trace(go.Scatter(x=QR,y=AVC_e,name=t("ch_avc"),line=dict(color=COL["avc"],width=2,dash="dot")))
            if Qs>0:
                profit_rect(fig, Qs, Ps, ATCs)
                fig.add_trace(go.Scatter(x=[Qs,Qs,Qcomp,Qs],y=[Ps,MRs,Pcomp,Ps],
                    fill="toself",fillcolor="rgba(255,152,0,0.18)",
                    line=dict(width=1,color=COL["dwl"],dash="dot"),name=t("ch_dwl")))
                eqm(fig, Qs, Ps, f"Q*={Qs:.1f}, P*={Ps:.1f}")
                fig.add_hline(y=Ps,line=dict(color="grey",width=1,dash="dot"))
                fig.add_vline(x=Qs,line=dict(color="grey",width=1,dash="dot"))
            fig.update_layout(title=t("monopoly")+(" — LR" if lr else ""),
                              xaxis_title=t("ch_quantity"),yaxis_title=t("ch_price"),
                              yaxis=dict(range=[0,max(a_eff*1.1,80)]),
                              xaxis=dict(range=[0,min(a_eff/b_base*1.1,150)]),
                              template="plotly_white",height=520)
            st.plotly_chart(fig, use_container_width=True)
        with c2c:
            st.subheader(t("m_eq"))
            st.metric(t("m_q_star"),f"{Qs:.2f}"); st.metric(t("m_p_star"),f"{Ps:.2f}")
            st.metric("MR = MC",f"{MCs:.2f}"); st.metric(t("m_atc_q"),f"{ATCs:.2f}")
            st.metric(t("m_tr"),f"{Ps*Qs:.2f}"); st.metric(t("m_tc"),f"{TCs:.2f}")
            st.metric(t("m_profit"),f"{pi:.2f}",
                      delta=t("m_supernormal") if pi>0.5 else (t("m_zero") if abs(pi)<0.5 else t("m_loss")),
                      delta_color="normal" if pi>=-0.5 else "inverse")
            lerner=(Ps-MCs)/Ps if Ps>0 else 0
            st.metric(t("m_lerner"),f"{lerner:.3f}")
            st.markdown("---")
            if lr: st.success(t("lr_mono"))

    elif mk == "mc":
        bf = b_base*(1+0.3*(n_f-1)); af = a_eff/(n_f**0.4)
        Qs = max((af-c_eff)/(2*bf+2*d_eff),0)
        Ps = af - bf*Qs
        TCs = FC+c_eff*Qs+d_eff*Qs**2; ATCs=TCs/Qs if Qs>0 else 0
        pi = (Ps-ATCs)*Qs
        Pdf = af-bf*QR; MRf = af-2*bf*QR

        c1c, c2c = st.columns([2,1])
        with c1c:
            fig = go.Figure()
            m=Pdf>=0; fig.add_trace(go.Scatter(x=QR[m],y=Pdf[m],name=t("ch_firm_d"),line=dict(color=COL["demand"],width=2.5)))
            m=MRf>=-10; fig.add_trace(go.Scatter(x=QR[m],y=MRf[m],name=t("ch_mr"),line=dict(color=COL["mr"],width=2.5)))
            fig.add_trace(go.Scatter(x=QR,y=MC_e,name=t("ch_mc"),line=dict(color=COL["mc"],width=2.5)))
            fig.add_trace(go.Scatter(x=QR,y=ATC_e,name=t("ch_atc"),line=dict(color=COL["atc"],width=2,dash="dash")))
            if Qs>0:
                profit_rect(fig, Qs, Ps, ATCs)
                sym="star" if lr else "circle"
                eqm(fig, Qs, Ps, f"Q*={Qs:.1f}, P*={Ps:.1f}", sym=sym)
                fig.add_hline(y=Ps,line=dict(color="grey",width=1,dash="dot"))
                fig.add_vline(x=Qs,line=dict(color="grey",width=1,dash="dot"))
                if lr:
                    eqm(fig, Qe_eff, ATCmin_eff, f"min ATC={ATCmin_eff:.1f}", sym="diamond")
                    if Qs < Qe_eff:
                        fig.add_annotation(x=(Qs+Qe_eff)/2, y=ATCmin_eff*0.88,
                            text="← excess capacity →", showarrow=False,
                            font=dict(size=11,color=COL["atc"]))
            lbl = "LR Tangency" if lr else f"SR (n={n_f:.0f})"
            fig.update_layout(title=f"{t('mono_comp')} — {lbl}",
                              xaxis_title=t("ch_quantity"),yaxis_title=t("ch_price"),
                              yaxis=dict(range=[0,max(af*1.2,80)]),
                              xaxis=dict(range=[0,af/bf*1.2 if bf>0 else 100]),
                              template="plotly_white",height=520)
            st.plotly_chart(fig, use_container_width=True)
        with c2c:
            st.subheader(t("m_eq"))
            st.metric(t("m_n_firms"),f"{n_f:.1f}")
            st.metric(t("m_q_star"),f"{Qs:.2f}"); st.metric(t("m_p_star"),f"{Ps:.2f}")
            st.metric(t("m_atc_q"),f"{ATCs:.2f}")
            st.metric(t("m_profit"),f"{pi:.2f}",
                      delta=t("m_positive") if pi>0.5 else (t("m_zero") if abs(pi)<0.5 else t("m_loss")),
                      delta_color="normal" if pi>=-0.5 else "inverse")
            if Qs<Qe_eff: st.metric(t("m_excess"),f"{Qe_eff-Qs:.2f}")
            st.markdown("---")
            if lr: st.success(t("lr_mc"))

    else:  # duopoly
        c2_eff = c2*input_mult/tech_mult+tax_sh; c2_eff=max(c2_eff,0.1)
        d2_eff = d2/tech_mult; d2_eff=max(d2_eff,0.01)
        A1=(a_eff-c_eff)/(2*b_base+2*d_eff); B1_=b_base/(2*b_base+2*d_eff)
        A2=(a_eff-c2_eff)/(2*b_base+2*d2_eff); B2_=b_base/(2*b_base+2*d2_eff)
        det=1-B1_*B2_
        Q1s=max((A1-B1_*A2)/det,0) if abs(det)>1e-10 else 0
        Q2s=max((A2-B2_*A1)/det,0) if abs(det)>1e-10 else 0
        Qt=Q1s+Q2s; Ps=max(a_eff-b_base*Qt,0)
        TC1=FC+c_eff*Q1s+d_eff*Q1s**2; TC2=FC+c2_eff*Q2s+d2_eff*Q2s**2
        ATC1=TC1/Q1s if Q1s>0 else 0; ATC2=TC2/Q2s if Q2s>0 else 0
        pi1=(Ps-ATC1)*Q1s; pi2=(Ps-ATC2)*Q2s

        Qmono=max((a_eff-c_eff)/(2*b_base+2*d_eff),0); Pmono=a_eff-b_base*Qmono
        Qcomp=max((a_eff-c_eff)/(b_base+2*d_eff),0); Pcomp=max(a_eff-b_base*Qcomp,0)

        c1c, c2c = st.columns([2,1])
        with c1c:
            fig = make_subplots(rows=1,cols=2,
                subplot_titles=["Reaction Functions","Market & Profit"],
                horizontal_spacing=0.12)
            qr2 = np.linspace(0,max(A1,A2)*1.5,300)
            rf1=np.maximum(A1-B1_*qr2,0); rf2=np.maximum(A2-B2_*qr2,0)
            fig.add_trace(go.Scatter(x=qr2,y=rf1,name="BR₁: Q₁(Q₂)",line=dict(color=COL["react1"],width=2.5)),row=1,col=1)
            fig.add_trace(go.Scatter(x=rf2,y=qr2,name="BR₂: Q₂(Q₁)",line=dict(color=COL["react2"],width=2.5)),row=1,col=1)
            eqm(fig,Q2s,Q1s,f"Nash ({Q1s:.1f},{Q2s:.1f})",row=1,col=1,sym="star")
            for mult in [0.5,1.0,1.5]:
                pt=pi1*mult if pi1!=0 else mult*10
                q2i,q1i=[],[]
                for q1t in np.linspace(0.5,A1*2,200):
                    num=(a_eff-c_eff)*q1t-b_base*q1t**2-d_eff*q1t**2-FC-pt
                    dn=b_base*q1t
                    if dn!=0:
                        q2v=num/dn
                        if 0<=q2v<=max(A1,A2)*1.5: q1i.append(q1t); q2i.append(q2v)
                if q1i:
                    fig.add_trace(go.Scatter(x=q2i,y=q1i,line=dict(color=COL["react1"],width=1,dash="dot"),
                        showlegend=False,hoverinfo="skip"),row=1,col=1)
            fig.update_xaxes(title_text="Q₂",row=1,col=1); fig.update_yaxes(title_text="Q₁",row=1,col=1)

            Qp=np.linspace(0.1,a_eff/b_base,300); Pp=a_eff-b_base*Qp
            fig.add_trace(go.Scatter(x=Qp,y=Pp,name=t("ch_mkt_demand"),line=dict(color=COL["demand"],width=2.5)),row=1,col=2)
            if Q1s>0:
                tp1,bt1=(Ps,ATC1) if pi1>=0 else (ATC1,Ps)
                fig.add_trace(go.Scatter(x=[0,Q1s,Q1s,0,0],y=[tp1,tp1,bt1,bt1,tp1],
                    fill="toself",fillcolor="rgba(33,150,243,0.18)",
                    line=dict(width=1,color="rgba(33,150,243,0.5)"),
                    name=f"π₁={pi1:.1f}"),row=1,col=2)
            if Q2s>0:
                tp2,bt2=(Ps,ATC2) if pi2>=0 else (ATC2,Ps)
                fig.add_trace(go.Scatter(x=[Q1s,Qt,Qt,Q1s,Q1s],y=[tp2,tp2,bt2,bt2,tp2],
                    fill="toself",fillcolor="rgba(156,39,176,0.18)",
                    line=dict(width=1,color="rgba(156,39,176,0.5)"),
                    name=f"π₂={pi2:.1f}"),row=1,col=2)
            eqm(fig,Qt,Ps,f"Q={Qt:.1f}",row=1,col=2)
            fig.add_trace(go.Scatter(x=[Qmono],y=[Pmono],mode="markers",
                marker=dict(size=9,color="purple",symbol="diamond"),name="Monopoly"),row=1,col=2)
            if Qcomp<=a_eff/b_base:
                fig.add_trace(go.Scatter(x=[Qcomp],y=[Pcomp],mode="markers",
                    marker=dict(size=9,color="green",symbol="triangle-up"),name="Competitive"),row=1,col=2)
            fig.update_xaxes(title_text=t("m_total_q"),row=1,col=2)
            fig.update_yaxes(title_text=t("ch_price_only"),row=1,col=2)
            fig.update_layout(template="plotly_white",height=560,
                title=t("duopoly")+(" — LR" if lr else ""),
                legend=dict(x=0.01,y=-0.18,orientation="h"))
            st.plotly_chart(fig, use_container_width=True)

        with c2c:
            st.subheader("Cournot")
            st.markdown("**Firm 1**"); st.metric("Q₁*",f"{Q1s:.2f}"); st.metric("ATC₁",f"{ATC1:.2f}"); st.metric("π₁",f"{pi1:.2f}")
            st.markdown("**Firm 2**"); st.metric("Q₂*",f"{Q2s:.2f}"); st.metric("ATC₂",f"{ATC2:.2f}"); st.metric("π₂",f"{pi2:.2f}")
            st.markdown("**Market**"); st.metric(t("m_total_q"),f"{Qt:.2f}"); st.metric(t("m_p_star"),f"{Ps:.2f}")
            st.markdown("---")
            if lr: st.success(t("lr_duo"))

# ─────────────────────────────────────────────────
#  TAB 3: COMPARATIVE STATICS
# ─────────────────────────────────────────────────
with tab3:
    param = st.selectbox(t("vary_param"),
        [t("fc"), t("var_c"), t("intercept_a"), t("slope_b")])
    param_keys = {t("fc"):"fc", t("var_c"):"vc", t("intercept_a"):"a", t("slope_b"):"b"}
    pk = param_keys[param]
    rng = {"fc":np.linspace(0,500,60),"vc":np.linspace(1,50,60),
           "a":np.linspace(20,200,60),"b":np.linspace(0.1,5,60)}[pk]

    rQ,rP,rPi = [],[],[]
    for v in rng:
        fc_v = v if pk=="fc" else FC
        c_v  = (v*input_mult/tech_mult+tax_sh if pk=="vc" else c_eff)
        c_v  = max(c_v, 0.1)
        a_v  = (v*pref_mult*cons_mult+income_sh+subst_sh if pk=="a" else a_eff)
        b_v  = v if pk=="b" else b_base
        d_v  = d_eff
        if mk=="pc":
            pm=min_atc(fc_v,c_v,d_v)[1] if lr else P_input
            qs=max((pm-c_v)/(2*d_v),0); ps=pm
        elif mk=="mon":
            qs=max((a_v-c_v)/(2*b_v+2*d_v),0); ps=a_v-b_v*qs
        elif mk=="mc":
            bf_=b_v*(1+0.3*(n_f-1)); af_=a_v/(n_f**0.4)
            qs=max((af_-c_v)/(2*bf_+2*d_v),0); ps=af_-bf_*qs
        else:
            c2v=c2*input_mult/tech_mult+tax_sh; c2v=max(c2v,0.1)
            d2v=d2/tech_mult; d2v=max(d2v,0.01)
            _A1=(a_v-c_v)/(2*b_v+2*d_v); _B1=b_v/(2*b_v+2*d_v)
            _A2=(a_v-c2v)/(2*b_v+2*d2v); _B2=b_v/(2*b_v+2*d2v)
            _det=1-_B1*_B2
            _q1=max((_A1-_B1*_A2)/_det,0) if abs(_det)>1e-10 else 0
            _q2=max((_A2-_B2*_A1)/_det,0) if abs(_det)>1e-10 else 0
            qs=_q1+_q2; ps=max(a_v-b_v*qs,0)
        tc_v=fc_v+c_v*qs+d_v*qs**2
        atc_v=tc_v/qs if qs>0 else 0
        rQ.append(qs); rP.append(ps); rPi.append((ps-atc_v)*qs)

    fcs = make_subplots(rows=1,cols=3,subplot_titles=[t("ch_quantity"),t("ch_price_only"),t("ch_profit")])
    fcs.add_trace(go.Scatter(x=rng,y=rQ,line=dict(color=COL["demand"],width=2.5),name="Q*"),row=1,col=1)
    fcs.add_trace(go.Scatter(x=rng,y=rP,line=dict(color=COL["mc"],width=2.5),name="P*"),row=1,col=2)
    fcs.add_trace(go.Scatter(x=rng,y=rPi,line=dict(color=COL["atc"],width=2.5),name="π"),row=1,col=3)
    fcs.add_hline(y=0,line=dict(color="grey",dash="dash"),row=1,col=3)

    cur={"fc":FC,"vc":c1,"a":a_base,"b":b_base}[pk]
    for i in range(1,4):
        fcs.update_xaxes(title_text=param,row=1,col=i)
        fcs.add_vline(x=cur,line=dict(color=COL["eq"],width=2,dash="dash"),row=1,col=i)
    fcs.update_yaxes(title_text="Q*",row=1,col=1)
    fcs.update_yaxes(title_text="P*",row=1,col=2)
    fcs.update_yaxes(title_text="π",row=1,col=3)
    fcs.update_layout(template="plotly_white",height=380,showlegend=False,
                      title=f"{t('statics_title')} — {market_label}")
    st.plotly_chart(fcs, use_container_width=True)

# ─── Reference ───
st.markdown("---")
with st.expander(t("ref_title")):
    st.markdown(r"""
| Symbol | Formula |
|--------|---------|
| TC | $FC + c \cdot Q + d \cdot Q^2$ |
| MC | $c + 2d \cdot Q$ |
| ATC | $FC/Q + c + d \cdot Q$ |
| min ATC | $Q_{eff} = \sqrt{FC/d}$ |
| Profit | $\pi = (P - ATC) \times Q$ |

| Structure | Equilibrium | Long Run |
|-----------|-------------|----------|
| Perfect Competition | $P = MC$ | $P = \min ATC \Rightarrow \pi = 0$ |
| Monopoly | $MR = MC$ | Barriers $\Rightarrow \pi > 0$ |
| Monopolistic Comp. | $MR = MC$ | Tangency $P = ATC \Rightarrow \pi = 0$ |
| Cournot Duopoly | Nash: $Q_i^* = \frac{a-c_i}{2b+2d_i} - \frac{b}{2b+2d_i}Q_j$ | Barriers $\Rightarrow \pi \geq 0$ |
    """)
st.caption(t("footer") + " • Streamlit & Plotly")
