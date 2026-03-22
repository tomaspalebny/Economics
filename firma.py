import datetime
current_year = datetime.datetime.now().year
# ... na konec souboru
import streamlit as st
st.markdown(f"<hr style='margin-top:2em;margin-bottom:0.5em;'>", unsafe_allow_html=True)
st.markdown(f"<div style='text-align:center; color:gray; font-size:0.95em;'>© {current_year} Tomáš Paleta, Masarykova univerzita, Ekonomicko-správní fakulta, Brno</div>", unsafe_allow_html=True)
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Firm Equilibrium V4", layout="wide", page_icon="📈")

# ═══════════════════════════════════════════════════
#  LANGUAGE
# ═══════════════════════════════════════════════════
T = {
    "title":          ("📈 Firm Equilibrium Simulator V4",     "📈 Simulátor rovnováhy firmy V4"),
    "subtitle":       ("Interactive model — market events feed directly into firm equilibrium.",
                       "Interaktivní model — tržní události se přímo promítají do rovnováhy firmy."),
    "s_lang":         ("🌐 Language",                          "🌐 Jazyk"),
    "s_structure":    ("⚙️ Market Structure",                  "⚙️ Tržní struktura"),
    "s_cost":         ("💰 Cost Parameters",                   "💰 Nákladové parametry"),
    "s_demand":       ("🏪 Demand / Market",                   "🏪 Poptávka / Trh"),
    "perf_comp":      ("Perfect Competition",                  "Dokonalá konkurence"),
    "monopoly":       ("Monopoly",                             "Monopol"),
    "mono_comp":      ("Monopolistic Competition",             "Monopolistická konkurence"),
    "duopoly":        ("Duopoly (Cournot)",                    "Duopol (Cournot)"),
    "lr_toggle":      ("🔄 Long-Run Equilibrium",             "🔄 Dlouhodobá rovnováha"),
    "lr_help":        ("Snap to long-run equilibrium",         "Přepnout do dlouhodobé rovnováhy"),
    "fc":             ("Fixed Cost (FC)",                      "Fixní náklady (FC)"),
    "var_c":          ("Variable cost coeff (c)",              "Variabilní nákl. (c)"),
    "var_d":          ("Variable cost coeff (d)",              "Variabilní nákl. (d)"),
    "vc_help":        ("VC = c·Q + d·Q²",                     "VC = c·Q + d·Q²"),
    "intercept_a":    ("Demand intercept (a)",                 "Intercept poptávky (a)"),
    "slope_b":        ("Demand slope (b)",                     "Sklon poptávky (b)"),
    "market_price":   ("Market Price (P)",                     "Tržní cena (P)"),
    "n_firms":        ("Number of firms (n)",                  "Počet firem (n)"),
    "firm2_c":        ("Firm 2 cost c₂",                      "Firma 2 nákl. c₂"),
    "firm2_d":        ("Firm 2 cost d₂",                      "Firma 2 nákl. d₂"),
    # Events
    "events_header":  ("📰 Market Event",                      "📰 Tržní událost"),
    "event_none":     ("— No event —",                         "— Žádná událost —"),
    "event_group_d":  ("── Demand-side ──",                    "── Strana poptávky ──"),
    "event_group_s":  ("── Supply-side ──",                    "── Strana nabídky ──"),
    "ev_pref_up":     ("📈 Preferences ↑ (product becomes trendy)",
                       "📈 Preference ↑ (produkt se stal módním)"),
    "ev_pref_down":   ("📉 Preferences ↓ (product falls out of favour)",
                       "📉 Preference ↓ (produkt vyšel z módy)"),
    "ev_consumers_up":("👥 More consumers enter market",       "👥 Více spotřebitelů vstoupilo na trh"),
    "ev_consumers_dn":("👤 Fewer consumers (market shrinks)",  "👤 Méně spotřebitelů (trh se zmenšil)"),
    "ev_income_up":   ("💰 Consumer income rises",             "💰 Příjmy spotřebitelů rostou"),
    "ev_income_dn":   ("💸 Consumer income falls (recession)", "💸 Příjmy spotřebitelů klesají (recese)"),
    "ev_subst_up":    ("🔄 Price of substitute rises",         "🔄 Cena substitutu roste"),
    "ev_subst_dn":    ("🔄 Price of substitute falls",         "🔄 Cena substitutu klesá"),
    "ev_input_up":    ("🛢️ Input costs rise (e.g. energy crisis)",
                       "🛢️ Náklady vstupů rostou (např. energetická krize)"),
    "ev_input_dn":    ("📦 Input costs fall (cheaper materials)",
                       "📦 Náklady vstupů klesají (levnější materiály)"),
    "ev_tech_up":     ("🔬 New technology (efficiency ↑)",     "🔬 Nová technologie (efektivita ↑)"),
    "ev_firms_enter": ("🏗️ New firms enter the market",        "🏗️ Nové firmy vstoupily na trh"),
    "ev_firms_exit":  ("🚪 Firms exit the market",             "🚪 Firmy opouštějí trh"),
    "ev_tax":         ("🏛️ Government imposes tax",            "🏛️ Vláda zavádí daň"),
    "ev_subsidy":     ("🎁 Government grants subsidy",         "🎁 Vláda poskytuje dotaci"),
    # Explanations (short)
    "ex_pref_up":     ("Consumer tastes shifted in favour of this product → **demand increases** (a ↑). "
                       "The demand curve shifts right, raising equilibrium price and quantity.",
                       "Spotřebitelské preference se posunuly ve prospěch produktu → **poptávka roste** (a ↑). "
                       "Křivka poptávky se posune vpravo, zvyšuje rovnovážnou cenu a množství."),
    "ex_pref_down":   ("Product lost appeal → **demand decreases** (a ↓). "
                       "Demand curve shifts left, reducing price and quantity.",
                       "Produkt ztratil atraktivitu → **poptávka klesá** (a ↓). "
                       "Křivka poptávky se posune vlevo, snižuje cenu a množství."),
    "ex_consumers_up":("More buyers entered the market → **demand increases** (a ↑). "
                       "Higher market demand raises the price firms can charge.",
                       "Více kupujících vstoupilo na trh → **poptávka roste** (a ↑). "
                       "Vyšší tržní poptávka zvyšuje cenu, kterou mohou firmy účtovat."),
    "ex_consumers_dn":("Market is shrinking → **demand decreases** (a ↓). "
                       "Fewer buyers reduce total demand and equilibrium output.",
                       "Trh se zmenšuje → **poptávka klesá** (a ↓). "
                       "Méně kupujících snižuje celkovou poptávku a rovnovážný výstup."),
    "ex_income_up":   ("Rising incomes increase purchasing power → **demand for normal goods rises** (a ↑). "
                       "Consumers are willing to pay more at every quantity.",
                       "Rostoucí příjmy zvyšují kupní sílu → **poptávka po normálních statcích roste** (a ↑). "
                       "Spotřebitelé jsou ochotni platit více při každém množství."),
    "ex_income_dn":   ("Falling incomes reduce purchasing power → **demand falls** (a ↓). "
                       "Consumers cut back spending, shifting demand left.",
                       "Klesající příjmy snižují kupní sílu → **poptávka klesá** (a ↓). "
                       "Spotřebitelé omezují výdaje, poptávka se posouvá vlevo."),
    "ex_subst_up":    ("A substitute became more expensive → consumers switch to this product → **demand rises** (a ↑).",
                       "Substitut zdražil → spotřebitelé přecházejí k tomuto produktu → **poptávka roste** (a ↑)."),
    "ex_subst_dn":    ("A substitute became cheaper → consumers switch away → **demand falls** (a ↓).",
                       "Substitut zlevnil → spotřebitelé přecházejí k němu → **poptávka klesá** (a ↓)."),
    "ex_input_up":    ("Input prices (energy, materials, wages) rose → **costs increase** (c ↑). "
                       "MC and ATC shift up, reducing profit and optimal output.",
                       "Ceny vstupů (energie, materiály, mzdy) vzrostly → **náklady rostou** (c ↑). "
                       "MC a ATC se posunou nahoru, snižují zisk a optimální výstup."),
    "ex_input_dn":    ("Cheaper inputs → **costs decrease** (c ↓). "
                       "MC and ATC shift down, increasing profit and output.",
                       "Levnější vstupy → **náklady klesají** (c ↓). "
                       "MC a ATC se posunou dolů, zvyšují zisk a výstup."),
    "ex_tech_up":     ("New technology improves production efficiency → **costs fall** (c ↓, d ↓). "
                       "MC curve shifts down, firm produces more at lower cost.",
                       "Nová technologie zlepšuje efektivitu → **náklady klesají** (c ↓, d ↓). "
                       "Křivka MC se posune dolů, firma vyrábí více s nižšími náklady."),
    "ex_firms_enter": ("New competitors enter → in perfect/monopolistic competition the **market price falls** "
                       "or each firm's demand shrinks. Profit is squeezed.",
                       "Noví konkurenti vstupují → v dokonalé/monopolistické konkurenci **tržní cena klesá** "
                       "nebo se poptávka po produktu firmy zmenšuje. Zisk je stlačen."),
    "ex_firms_exit":  ("Competitors leave → remaining firms face **higher demand / price**. Profit rises.",
                       "Konkurenti odcházejí → zbývající firmy čelí **vyšší poptávce / ceně**. Zisk roste."),
    "ex_tax":         ("Per-unit tax raises production cost → **c increases**. "
                       "MC shifts up, output falls, price rises for consumers.",
                       "Jednotková daň zvyšuje výrobní náklady → **c roste**. "
                       "MC se posouvá nahoru, výstup klesá, cena pro spotřebitele roste."),
    "ex_subsidy":     ("Per-unit subsidy lowers production cost → **c decreases**. "
                       "MC shifts down, output rises, price falls.",
                       "Jednotková dotace snižuje výrobní náklady → **c klesá**. "
                       "MC se posouvá dolů, výstup roste, cena klesá."),
    # Chart
    "ch_mc":"MC","ch_atc":"ATC","ch_avc":"AVC","ch_demand":"Demand/Poptávka",
    "ch_mr":"MR","ch_quantity":("Quantity (Q)","Množství (Q)"),
    "ch_price":("Price / Cost","Cena / Náklady"),
    "ch_profit":("Profit","Zisk"),
    "ch_base_mc":("MC (before)","MC (před)"), "ch_base_atc":("ATC (before)","ATC (před)"),
    "ch_base_d":("Demand (before)","Poptávka (před)"), "ch_base_mr":("MR (before)","MR (před)"),
    "ch_firm_d":("Firm Demand (d)","Poptávka firmy (d)"),
    "ch_dwl":("Deadweight Loss","Ztráta mrtvé váhy"),
    # Metrics
    "m_eq":("Equilibrium","Rovnováha"), "m_q_star":"Q*", "m_p_star":"P*",
    "m_atc_q":("ATC at Q*","ATC při Q*"), "m_tr":("Total Revenue","Celkový příjem"),
    "m_tc":("Total Cost","Celkové náklady"),
    "m_profit":("Profit (P−ATC)·Q","Zisk (P−ATC)·Q"),
    "m_positive":("Positive","Kladný"), "m_zero":"≈ 0 ✓",
    "m_loss":("Loss","Ztráta"), "m_supernormal":("Supernormal","Nadnormální"),
    "m_lerner":("Lerner Index","Lernerův index"),
    "m_excess":("Excess Capacity","Nadbytečná kapacita"),
    "m_n_firms":("Firms (n)","Počet firem (n)"),
    "m_shutdown":("🛑 Shutdown: P < min AVC","🛑 Uzavření: P < min AVC"),
    "m_total_q":("Total Q","Celkové Q"), "m_mkt_price":("Market Price","Tržní cena"),
    # LR
    "lr_pc": ("**LR:** P = min ATC → π = 0, allocative + productive efficiency",
              "**DR:** P = min ATC → π = 0, alokační + produktivní efektivita"),
    "lr_mono":("**LR:** MR = MC, barriers → supernormal profit persists, DWL",
               "**DR:** MR = MC, bariéry → nadnormální zisk přetrvává, DWL"),
    "lr_mc":  ("**LR:** Tangency P = ATC → π = 0, excess capacity",
               "**DR:** Tangence P = ATC → π = 0, nadbytečná kapacita"),
    "lr_duo": ("**LR:** Nash eq., barriers → profit may persist",
               "**DR:** Nashova rovnováha, bariéry → zisk může přetrvávat"),
    # Statics
    "tab_firm":("🏢 Firm Equilibrium","🏢 Rovnováha firmy"),
    "tab_statics":("📊 Comparative Statics","📊 Komparativní statika"),
    "vary_param":("Vary parameter:","Měnit parametr:"),
    "statics_title":("Comparative Statics","Komparativní statika"),
    "ref_title":("📖 Model Equations","📖 Rovnice modelu"),
    "footer":("Firm Equilibrium Simulator V4","Simulátor rovnováhy firmy V4"),
    "event_impact":("Impact","Dopad"),
    "delta_q":("ΔQ*","ΔQ*"), "delta_p":("ΔP*","ΔP*"), "delta_pi":("Δπ","Δπ"),
    "before_after":("Before → After event","Před → Po události"),
    "intensity":("Event intensity","Intenzita události"),
}

lang_sel = st.sidebar.radio("🌐", ["EN", "CZ"], horizontal=True, label_visibility="collapsed")
LI = 0 if lang_sel == "EN" else 1
def t(k):
    v = T[k]
    return v[LI] if isinstance(v, tuple) else v

st.title(t("title"))
st.markdown(t("subtitle"))

# ═══════════════════════════════════════════════════
#  SIDEBAR — structure, cost, demand
# ═══════════════════════════════════════════════════
structs = [t("perf_comp"), t("monopoly"), t("mono_comp"), t("duopoly")]
skeys = ["pc","mon","mc","duo"]
st.sidebar.header(t("s_structure"))
market_label = st.sidebar.selectbox("str", structs, label_visibility="collapsed")
mk = skeys[structs.index(market_label)]

lr = st.sidebar.toggle(t("lr_toggle"), value=False, help=t("lr_help"))

st.sidebar.header(t("s_cost"))
FC  = st.sidebar.slider(t("fc"), 0, 500, 100, 10)
c1  = st.sidebar.slider(t("var_c"), 1.0, 50.0, 10.0, 0.5, help=t("vc_help"))
d1  = st.sidebar.slider(t("var_d"), 0.01, 2.0, 0.50, 0.01, help=t("vc_help"))

st.sidebar.header(t("s_demand"))
if mk == "pc":
    P_input = st.sidebar.slider(t("market_price"), 5.0, 150.0, 40.0, 0.5)
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
#  SIDEBAR — Market Events
# ═══════════════════════════════════════════════════
st.sidebar.header(t("events_header"))
ev_keys = [
    "event_none",
    "event_group_d",
    "ev_pref_up","ev_pref_down",
    "ev_consumers_up","ev_consumers_dn",
    "ev_income_up","ev_income_dn",
    "ev_subst_up","ev_subst_dn",
    "event_group_s",
    "ev_input_up","ev_input_dn",
    "ev_tech_up",
    "ev_firms_enter","ev_firms_exit",
    "ev_tax","ev_subsidy",
]
ev_labels = [t(k) for k in ev_keys]
disabled_idx = {1, 10}  # group headers
ev_sel = st.sidebar.selectbox("event", ev_labels, label_visibility="collapsed")
ev_idx = ev_labels.index(ev_sel)
ev_key = ev_keys[ev_idx] if ev_idx not in disabled_idx else "event_none"

intensity = 1.0
if ev_key != "event_none":
    intensity = st.sidebar.slider(t("intensity"), 0.1, 3.0, 1.0, 0.1)

# ─── Compute shifts from event ───
da = 0.0   # additive shift to a / P_market
dc = 0.0   # additive shift to c
dd = 0.0   # additive shift to d
dn = 0     # additive shift to n_firms

EV_MAP = {
    "ev_pref_up":      (15, 0, 0, 0),
    "ev_pref_down":    (-15, 0, 0, 0),
    "ev_consumers_up": (20, 0, 0, 0),
    "ev_consumers_dn": (-20, 0, 0, 0),
    "ev_income_up":    (15, 0, 0, 0),
    "ev_income_dn":    (-15, 0, 0, 0),
    "ev_subst_up":     (12, 0, 0, 0),
    "ev_subst_dn":     (-12, 0, 0, 0),
    "ev_input_up":     (0, 5, 0.1, 0),
    "ev_input_dn":     (0, -4, -0.08, 0),
    "ev_tech_up":      (0, -4, -0.12, 0),
    "ev_firms_enter":  (-8, 0, 0, 3),
    "ev_firms_exit":   (10, 0, 0, -2),
    "ev_tax":          (0, 5, 0, 0),
    "ev_subsidy":      (0, -5, 0, 0),
}

if ev_key in EV_MAP:
    _da, _dc, _dd, _dn = EV_MAP[ev_key]
    da = _da * intensity
    dc = _dc * intensity
    dd = _dd * intensity
    dn = int(round(_dn * intensity))

# Effective parameters
a_eff = max(a_base + da, 5)
c_eff = max(c1 + dc, 0.1)
d_eff = max(d1 + dd, 0.01)
P_eff = max((P_input + da) if mk == "pc" else 0, 1) if mk == "pc" else 0

if mk == "mc":
    n_eff = max(n_input + dn, 2)
else:
    n_eff = 0

has_event = ev_key != "event_none"

# ═══════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════
QR = np.linspace(0.1, 150, 800)
COL = dict(
    demand="#2196F3", mr="#FF9800", mc="#E53935", atc="#4CAF50",
    avc="#8BC34A", eq="#FFD600", dwl="#FF9800",
    base_d="#90CAF9", base_mc="#EF9A9A", base_atc="#A5D6A7", base_mr="#FFE0B2",
    react1="#2196F3", react2="#E53935",
    pf="rgba(129,212,250,0.35)", pl="rgba(33,150,243,0.6)",
    lf="rgba(239,154,154,0.35)", ll="rgba(229,57,53,0.6)",
)

def cc(Q, fc, c, d):
    TC = fc + c*Q + d*Q**2; MC = c + 2*d*Q
    with np.errstate(divide="ignore", invalid="ignore"):
        ATC = np.where(Q>0, TC/Q, np.nan)
        AVC = np.where(Q>0, (c*Q + d*Q**2)/Q, np.nan)
    return TC, MC, ATC, AVC

def min_atc(fc, c, d):
    Qe = np.sqrt(fc/d) if fc>0 and d>0 else 1.0
    return Qe, fc/Qe + c + d*Qe

def prect(fig, Qs, Ps, ATCs, row=None, col=None):
    pi = (Ps-ATCs)*Qs
    if Qs <= 0: return pi
    xs = [0, Qs, Qs, 0, 0]
    if pi >= 0:
        ys=[Ps,Ps,ATCs,ATCs,Ps]; fc_,lc_=COL["pf"],COL["pl"]
    else:
        ys=[ATCs,ATCs,Ps,Ps,ATCs]; fc_,lc_=COL["lf"],COL["ll"]
    tr = go.Scatter(x=xs,y=ys,fill="toself",fillcolor=fc_,
                    line=dict(width=1.5,color=lc_),name=f"{t('ch_profit')}={pi:.1f}")
    if row: fig.add_trace(tr,row=row,col=col)
    else: fig.add_trace(tr)
    return pi

def eqm(fig, x, y, label, row=None, col=None, sym="circle"):
    kw=dict(x=[x],y=[y],mode="markers+text",text=[f"  {label}"],textposition="top right",
            marker=dict(size=12,color=COL["eq"],symbol=sym,line=dict(width=2,color="black")),name=label)
    if row: fig.add_trace(go.Scatter(**kw),row=row,col=col)
    else: fig.add_trace(go.Scatter(**kw))

# Base & effective cost arrays
TC_b, MC_b, ATC_b, AVC_b = cc(QR, FC, c1, d1)
TC_e, MC_e, ATC_e, AVC_e = cc(QR, FC, c_eff, d_eff)
Qe_eff, ATCmin_eff = min_atc(FC, c_eff, d_eff)

# ─── LR adjustments ───
if mk == "pc":
    P_m = ATCmin_eff if lr else P_eff
    if lr: st.sidebar.info(f"🔄 LR: P → min ATC = {ATCmin_eff:.2f}")
if mk == "mc":
    if lr:
        best_n, best_err = 1.0, 1e15
        for nt in np.arange(1.0, 200, 0.05):
            bf=b_base*(1+0.3*(nt-1)); af=a_eff/(nt**0.4)
            qs=(af-c_eff)/(2*bf+2*d_eff)
            if qs<=0: break
            ps=af-bf*qs; err=abs(ps*qs-(FC+c_eff*qs+d_eff*qs**2))
            if err<best_err: best_err=err; best_n=nt
        n_f = best_n
        st.sidebar.info(f"🔄 LR: n ≈ {best_n:.1f}")
    else:
        n_f = n_eff
if mk == "duo":
    c2_eff = max(c2 + dc, 0.1)
    d2_eff = max(d2 + dd, 0.01)

# ═══════════════════════════════════════════════════
#  COMPUTE EQUILIBRIA (base & shifted)
# ═══════════════════════════════════════════════════
def solve_eq(a, b, c, d, fc, mk, P_market=None, n=None, c2_=None, d2_=None):
    """Return dict with Q*, P*, ATC*, profit for given params."""
    if mk == "pc":
        Qs = max((P_market - c)/(2*d), 0)
        Ps = P_market
    elif mk == "mon":
        Qs = max((a - c)/(2*b + 2*d), 0)
        Ps = a - b*Qs
    elif mk == "mc":
        bf = b*(1+0.3*(n-1)); af = a/(n**0.4)
        Qs = max((af - c)/(2*bf + 2*d), 0)
        Ps = af - bf*Qs
    elif mk == "duo":
        A1=(a-c)/(2*b+2*d); B1=b/(2*b+2*d)
        A2=(a-c2_)/(2*b+2*d2_); B2=b/(2*b+2*d2_)
        det=1-B1*B2
        Q1=max((A1-B1*A2)/det,0) if abs(det)>1e-10 else 0
        Q2=max((A2-B2*A1)/det,0) if abs(det)>1e-10 else 0
        Qs=Q1+Q2; Ps=max(a-b*Qs,0)
        tc1=fc+c*Q1+d*Q1**2; tc2=fc+c2_*Q2+d2_*Q2**2
        atc1=tc1/Q1 if Q1>0 else 0; atc2=tc2/Q2 if Q2>0 else 0
        return dict(Q1=Q1,Q2=Q2,Qt=Qs,P=Ps,ATC1=atc1,ATC2=atc2,
                    pi1=(Ps-atc1)*Q1, pi2=(Ps-atc2)*Q2)
    TCs = fc + c*Qs + d*Qs**2
    ATCs = TCs/Qs if Qs>0 else 0
    return dict(Q=Qs, P=Ps, ATC=ATCs, pi=(Ps-ATCs)*Qs, TC=TCs)

# Base equilibrium (before event)
if mk == "pc":
    P_base_m = min_atc(FC,c1,d1)[1] if lr else P_input
    eq_base = solve_eq(a_base, b_base, c1, d1, FC, mk, P_market=P_base_m)
    eq_now  = solve_eq(a_eff,  b_base, c_eff, d_eff, FC, mk, P_market=P_m)
elif mk == "mon":
    eq_base = solve_eq(a_base, b_base, c1, d1, FC, mk)
    eq_now  = solve_eq(a_eff,  b_base, c_eff, d_eff, FC, mk)
elif mk == "mc":
    n_base = min_atc(FC,c1,d1) and n_input  # just n_input for base
    if lr:
        # also compute base LR n
        bn_b, bn_err = 1.0, 1e15
        for nt in np.arange(1.0, 200, 0.05):
            bf_=b_base*(1+0.3*(nt-1)); af_=a_base/(nt**0.4)
            qs_=(af_-c1)/(2*bf_+2*d1)
            if qs_<=0: break
            ps_=af_-bf_*qs_; err_=abs(ps_*qs_-(FC+c1*qs_+d1*qs_**2))
            if err_<bn_err: bn_err=err_; bn_b=nt
        n_base = bn_b
    eq_base = solve_eq(a_base, b_base, c1, d1, FC, mk, n=n_base)
    eq_now  = solve_eq(a_eff,  b_base, c_eff, d_eff, FC, mk, n=n_f)
elif mk == "duo":
    eq_base = solve_eq(a_base, b_base, c1, d1, FC, mk, c2_=c2, d2_=d2)
    eq_now  = solve_eq(a_eff,  b_base, c_eff, d_eff, FC, mk, c2_=c2_eff, d2_=d2_eff)

# ═══════════════════════════════════════════════════
#  EVENT EXPLANATION BANNER
# ═══════════════════════════════════════════════════
if has_event:
    ex_key = ev_key.replace("ev_", "ex_")
    explanation = t(ex_key) if ex_key in T else ""
    st.info(f"**{ev_sel}** (×{intensity:.1f})\n\n{explanation}")

    # Delta metrics
    if mk != "duo":
        dQ = eq_now["Q"] - eq_base["Q"]
        dP = eq_now["P"] - eq_base["P"]
        dpi = eq_now["pi"] - eq_base["pi"]
    else:
        dQ = eq_now["Qt"] - eq_base["Qt"]
        dP = eq_now["P"]  - eq_base["P"]
        dpi = (eq_now["pi1"]+eq_now["pi2"]) - (eq_base["pi1"]+eq_base["pi2"])
    dc1,dc2,dc3 = st.columns(3)
    dc1.metric(t("delta_q"), f"{dQ:+.2f}")
    dc2.metric(t("delta_p"), f"{dP:+.2f}")
    dc3.metric(t("delta_pi"), f"{dpi:+.2f}")

# ═══════════════════════════════════════════════════
#  TABS
# ═══════════════════════════════════════════════════
tab1, tab2 = st.tabs([t("tab_firm"), t("tab_statics")])

# ─────────────────────────────────────────────────
#  TAB 1: FIRM EQUILIBRIUM
# ─────────────────────────────────────────────────
with tab1:
  if mk == "pc":
    Qs=eq_now["Q"]; Ps=P_m; ATCs=eq_now["ATC"]; pi=eq_now["pi"]
    shutdown = Ps < c_eff
    c1c, c2c = st.columns([2,1])
    with c1c:
        fig = go.Figure()
        # Ghost base curves if event active
        if has_event:
            fig.add_trace(go.Scatter(x=QR,y=MC_b,name=t("ch_base_mc"),line=dict(color=COL["base_mc"],width=1.5,dash="dash")))
            fig.add_trace(go.Scatter(x=QR,y=ATC_b,name=t("ch_base_atc"),line=dict(color=COL["base_atc"],width=1.5,dash="dash")))
            fig.add_hline(y=P_base_m,line=dict(color=COL["base_d"],width=1.5,dash="dash"),
                          annotation_text=f"P₀={P_base_m:.1f}")
        fig.add_trace(go.Scatter(x=QR,y=MC_e,name="MC",line=dict(color=COL["mc"],width=2.5)))
        fig.add_trace(go.Scatter(x=QR,y=ATC_e,name="ATC",line=dict(color=COL["atc"],width=2,dash="dash")))
        fig.add_trace(go.Scatter(x=QR,y=AVC_e,name="AVC",line=dict(color=COL["avc"],width=2,dash="dot")))
        fig.add_hline(y=Ps,line=dict(color=COL["demand"],width=2),annotation_text=f"P={Ps:.1f}")
        if Qs>0 and not shutdown:
            prect(fig, Qs, Ps, ATCs)
            eqm(fig, Qs, Ps, f"Q*={Qs:.1f}")
            if lr: eqm(fig, Qe_eff, ATCmin_eff, f"min ATC={ATCmin_eff:.1f}", sym="diamond")
        fig.update_layout(title=t("perf_comp")+(" — LR" if lr else ""),
            xaxis_title=t("ch_quantity"),yaxis_title=t("ch_price"),
            yaxis=dict(range=[0,max(Ps*2.5,80)]),xaxis=dict(range=[0,min(Qs*3+15,150)]),
            template="plotly_white",height=540,legend=dict(x=0.58,y=0.98))
        st.plotly_chart(fig, use_container_width=True)
    with c2c:
        st.subheader(t("m_eq"))
        if shutdown: st.error(t("m_shutdown"))
        else:
            st.metric(t("m_q_star"),f"{Qs:.2f}"); st.metric(t("m_mkt_price"),f"{Ps:.2f}")
            st.metric(t("m_atc_q"),f"{ATCs:.2f}")
            st.metric(t("m_tr"),f"{Ps*Qs:.2f}"); st.metric(t("m_tc"),f"{eq_now['TC']:.2f}")
            st.metric(t("m_profit"),f"{pi:.2f}",
                delta=t("m_positive") if pi>0.5 else (t("m_zero") if abs(pi)<0.5 else t("m_loss")),
                delta_color="normal" if pi>=-0.5 else "inverse")
        st.markdown("---")
        if lr: st.success(t("lr_pc"))

  elif mk == "mon":
    Qs=eq_now["Q"]; Ps=eq_now["P"]; ATCs=eq_now["ATC"]; pi=eq_now["pi"]
    MCs=c_eff+2*d_eff*Qs; MRs=a_eff-2*b_base*Qs
    Qcomp=max((a_eff-c_eff)/(b_base+2*d_eff),0); Pcomp=a_eff-b_base*Qcomp
    Pd=a_eff-b_base*QR; MRc=a_eff-2*b_base*QR
    c1c, c2c = st.columns([2,1])
    with c1c:
        fig = go.Figure()
        if has_event:
            Pd_b=a_base-b_base*QR; MR_b=a_base-2*b_base*QR
            m=Pd_b>=0; fig.add_trace(go.Scatter(x=QR[m],y=Pd_b[m],name=t("ch_base_d"),line=dict(color=COL["base_d"],width=1.5,dash="dash")))
            m=MR_b>=-20; fig.add_trace(go.Scatter(x=QR[m],y=MR_b[m],name=t("ch_base_mr"),line=dict(color=COL["base_mr"],width=1.5,dash="dash")))
            fig.add_trace(go.Scatter(x=QR,y=MC_b,name=t("ch_base_mc"),line=dict(color=COL["base_mc"],width=1.5,dash="dash")))
        m=Pd>=0; fig.add_trace(go.Scatter(x=QR[m],y=Pd[m],name=t("ch_demand"),line=dict(color=COL["demand"],width=2.5)))
        m=MRc>=-20; fig.add_trace(go.Scatter(x=QR[m],y=MRc[m],name="MR",line=dict(color=COL["mr"],width=2.5)))
        fig.add_trace(go.Scatter(x=QR,y=MC_e,name="MC",line=dict(color=COL["mc"],width=2.5)))
        fig.add_trace(go.Scatter(x=QR,y=ATC_e,name="ATC",line=dict(color=COL["atc"],width=2,dash="dash")))
        fig.add_trace(go.Scatter(x=QR,y=AVC_e,name="AVC",line=dict(color=COL["avc"],width=2,dash="dot")))
        if Qs>0:
            prect(fig, Qs, Ps, ATCs)
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
            template="plotly_white",height=540,legend=dict(x=0.55,y=0.98))
        st.plotly_chart(fig, use_container_width=True)
    with c2c:
        st.subheader(t("m_eq"))
        st.metric(t("m_q_star"),f"{Qs:.2f}"); st.metric(t("m_p_star"),f"{Ps:.2f}")
        st.metric("MR = MC",f"{MCs:.2f}"); st.metric(t("m_atc_q"),f"{ATCs:.2f}")
        st.metric(t("m_profit"),f"{pi:.2f}",
            delta=t("m_supernormal") if pi>0.5 else (t("m_zero") if abs(pi)<0.5 else t("m_loss")),
            delta_color="normal" if pi>=-0.5 else "inverse")
        lerner=(Ps-MCs)/Ps if Ps>0 else 0
        st.metric(t("m_lerner"),f"{lerner:.3f}")
        st.markdown("---")
        if lr: st.success(t("lr_mono"))

  elif mk == "mc":
    bf=b_base*(1+0.3*(n_f-1)); af=a_eff/(n_f**0.4)
    Qs=eq_now["Q"]; Ps=eq_now["P"]; ATCs=eq_now["ATC"]; pi=eq_now["pi"]
    Pdf=af-bf*QR; MRf=af-2*bf*QR
    c1c, c2c = st.columns([2,1])
    with c1c:
        fig = go.Figure()
        if has_event:
            bf_b=b_base*(1+0.3*(n_base-1)); af_b=a_base/(n_base**0.4)
            Pd_b=af_b-bf_b*QR; MR_b=af_b-2*bf_b*QR
            m=Pd_b>=0; fig.add_trace(go.Scatter(x=QR[m],y=Pd_b[m],name=t("ch_base_d"),line=dict(color=COL["base_d"],width=1.5,dash="dash")))
            m=MR_b>=-10; fig.add_trace(go.Scatter(x=QR[m],y=MR_b[m],name=t("ch_base_mr"),line=dict(color=COL["base_mr"],width=1.5,dash="dash")))
            fig.add_trace(go.Scatter(x=QR,y=MC_b,name=t("ch_base_mc"),line=dict(color=COL["base_mc"],width=1.5,dash="dash")))
        m=Pdf>=0; fig.add_trace(go.Scatter(x=QR[m],y=Pdf[m],name=t("ch_firm_d"),line=dict(color=COL["demand"],width=2.5)))
        m=MRf>=-10; fig.add_trace(go.Scatter(x=QR[m],y=MRf[m],name="MR",line=dict(color=COL["mr"],width=2.5)))
        fig.add_trace(go.Scatter(x=QR,y=MC_e,name="MC",line=dict(color=COL["mc"],width=2.5)))
        fig.add_trace(go.Scatter(x=QR,y=ATC_e,name="ATC",line=dict(color=COL["atc"],width=2,dash="dash")))
        if Qs>0:
            prect(fig, Qs, Ps, ATCs)
            sym="star" if lr else "circle"
            eqm(fig, Qs, Ps, f"Q*={Qs:.1f}, P*={Ps:.1f}", sym=sym)
            fig.add_hline(y=Ps,line=dict(color="grey",width=1,dash="dot"))
            fig.add_vline(x=Qs,line=dict(color="grey",width=1,dash="dot"))
            if lr:
                eqm(fig, Qe_eff, ATCmin_eff, f"min ATC={ATCmin_eff:.1f}", sym="diamond")
                if Qs<Qe_eff:
                    fig.add_annotation(x=(Qs+Qe_eff)/2,y=ATCmin_eff*0.88,
                        text="← excess capacity →",showarrow=False,font=dict(size=11,color=COL["atc"]))
        lbl="LR" if lr else f"SR (n={n_f:.0f})"
        fig.update_layout(title=f"{t('mono_comp')} — {lbl}",
            xaxis_title=t("ch_quantity"),yaxis_title=t("ch_price"),
            yaxis=dict(range=[0,max(af*1.2,80)]),
            xaxis=dict(range=[0,af/bf*1.2 if bf>0 else 100]),
            template="plotly_white",height=540,legend=dict(x=0.55,y=0.98))
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

  elif mk == "duo":
    Q1s=eq_now["Q1"]; Q2s=eq_now["Q2"]; Qt=eq_now["Qt"]; Ps=eq_now["P"]
    ATC1=eq_now["ATC1"]; ATC2=eq_now["ATC2"]
    pi1=eq_now["pi1"]; pi2=eq_now["pi2"]
    A1=(a_eff-c_eff)/(2*b_base+2*d_eff); B1_=b_base/(2*b_base+2*d_eff)
    A2=(a_eff-c2_eff)/(2*b_base+2*d2_eff); B2_=b_base/(2*b_base+2*d2_eff)
    Qmono=max((a_eff-c_eff)/(2*b_base+2*d_eff),0); Pmono=a_eff-b_base*Qmono
    Qcomp=max((a_eff-c_eff)/(b_base+2*d_eff),0); Pcomp=max(a_eff-b_base*Qcomp,0)
    c1c, c2c = st.columns([2,1])
    with c1c:
        fig = make_subplots(rows=1,cols=2,subplot_titles=["Reaction Functions","Market"],horizontal_spacing=0.12)
        qr2=np.linspace(0,max(A1,A2)*1.5,300)
        rf1=np.maximum(A1-B1_*qr2,0); rf2=np.maximum(A2-B2_*qr2,0)
        fig.add_trace(go.Scatter(x=qr2,y=rf1,name="BR₁",line=dict(color=COL["react1"],width=2.5)),row=1,col=1)
        fig.add_trace(go.Scatter(x=rf2,y=qr2,name="BR₂",line=dict(color=COL["react2"],width=2.5)),row=1,col=1)
        if has_event:
            A1b=(a_base-c1)/(2*b_base+2*d1); B1b=b_base/(2*b_base+2*d1)
            A2b=(a_base-c2)/(2*b_base+2*d2); B2b=b_base/(2*b_base+2*d2)
            rf1b=np.maximum(A1b-B1b*qr2,0); rf2b=np.maximum(A2b-B2b*qr2,0)
            fig.add_trace(go.Scatter(x=qr2,y=rf1b,name="BR₁₀",line=dict(color=COL["base_d"],width=1.5,dash="dash"),showlegend=False),row=1,col=1)
            fig.add_trace(go.Scatter(x=rf2b,y=qr2,name="BR₂₀",line=dict(color=COL["base_mc"],width=1.5,dash="dash"),showlegend=False),row=1,col=1)
        eqm(fig,Q2s,Q1s,f"Nash ({Q1s:.1f},{Q2s:.1f})",row=1,col=1,sym="star")
        fig.update_xaxes(title_text="Q₂",row=1,col=1); fig.update_yaxes(title_text="Q₁",row=1,col=1)
        Qp=np.linspace(0.1,a_eff/b_base,300); Pp=a_eff-b_base*Qp
        fig.add_trace(go.Scatter(x=Qp,y=Pp,name=t("ch_demand"),line=dict(color=COL["demand"],width=2.5)),row=1,col=2)
        if Q1s>0:
            tp1,bt1=(Ps,ATC1) if pi1>=0 else (ATC1,Ps)
            fig.add_trace(go.Scatter(x=[0,Q1s,Q1s,0,0],y=[tp1,tp1,bt1,bt1,tp1],
                fill="toself",fillcolor="rgba(33,150,243,0.18)",
                line=dict(width=1,color="rgba(33,150,243,0.5)"),name=f"π₁={pi1:.1f}"),row=1,col=2)
        if Q2s>0:
            tp2,bt2=(Ps,ATC2) if pi2>=0 else (ATC2,Ps)
            fig.add_trace(go.Scatter(x=[Q1s,Qt,Qt,Q1s,Q1s],y=[tp2,tp2,bt2,bt2,tp2],
                fill="toself",fillcolor="rgba(156,39,176,0.18)",
                line=dict(width=1,color="rgba(156,39,176,0.5)"),name=f"π₂={pi2:.1f}"),row=1,col=2)
        eqm(fig,Qt,Ps,f"Q={Qt:.1f}",row=1,col=2)
        fig.add_trace(go.Scatter(x=[Qmono],y=[Pmono],mode="markers",marker=dict(size=9,color="purple",symbol="diamond"),name="Monopoly"),row=1,col=2)
        if Qcomp<=a_eff/b_base:
            fig.add_trace(go.Scatter(x=[Qcomp],y=[Pcomp],mode="markers",marker=dict(size=9,color="green",symbol="triangle-up"),name="Competitive"),row=1,col=2)
        fig.update_xaxes(title_text=t("m_total_q"),row=1,col=2); fig.update_yaxes(title_text=t("ch_price"),row=1,col=2)
        fig.update_layout(template="plotly_white",height=560,
            title=t("duopoly")+(" — LR" if lr else ""),legend=dict(x=0.01,y=-0.18,orientation="h"))
        st.plotly_chart(fig, use_container_width=True)
    with c2c:
        st.subheader("Cournot")
        st.markdown("**Firm 1**"); st.metric("Q₁*",f"{Q1s:.2f}"); st.metric("π₁",f"{pi1:.2f}")
        st.markdown("**Firm 2**"); st.metric("Q₂*",f"{Q2s:.2f}"); st.metric("π₂",f"{pi2:.2f}")
        st.markdown("**Market**"); st.metric(t("m_total_q"),f"{Qt:.2f}"); st.metric(t("m_p_star"),f"{Ps:.2f}")
        st.markdown("---")
        if lr: st.success(t("lr_duo"))

# ─────────────────────────────────────────────────
#  TAB 2: COMPARATIVE STATICS
# ─────────────────────────────────────────────────
with tab2:
    param=st.selectbox(t("vary_param"),[t("fc"),t("var_c"),t("intercept_a"),t("slope_b")])
    pk={t("fc"):"fc",t("var_c"):"vc",t("intercept_a"):"a",t("slope_b"):"b"}[param]
    rng={"fc":np.linspace(0,500,60),"vc":np.linspace(1,50,60),
         "a":np.linspace(20,200,60),"b":np.linspace(0.1,5,60)}[pk]
    rQ,rP,rPi=[],[],[]
    for v in rng:
        fc_v=v if pk=="fc" else FC
        c_v=max(v+dc,0.1) if pk=="vc" else c_eff
        a_v=max(v+da,5) if pk=="a" else a_eff
        b_v=v if pk=="b" else b_base
        d_v=d_eff
        if mk=="pc":
            pm_v=min_atc(fc_v,c_v,d_v)[1] if lr else max(P_input+da,1)
            r=solve_eq(a_v,b_v,c_v,d_v,fc_v,"pc",P_market=pm_v)
        elif mk=="mon":
            r=solve_eq(a_v,b_v,c_v,d_v,fc_v,"mon")
        elif mk=="mc":
            r=solve_eq(a_v,b_v,c_v,d_v,fc_v,"mc",n=n_f)
        else:
            r=solve_eq(a_v,b_v,c_v,d_v,fc_v,"duo",c2_=c2_eff,d2_=d2_eff)
        if mk=="duo":
            rQ.append(r["Qt"]); rP.append(r["P"]); rPi.append(r["pi1"]+r["pi2"])
        else:
            rQ.append(r["Q"]); rP.append(r["P"]); rPi.append(r["pi"])

    fcs=make_subplots(rows=1,cols=3,subplot_titles=[t("ch_quantity"),t("ch_price"),t("ch_profit")])
    fcs.add_trace(go.Scatter(x=rng,y=rQ,line=dict(color=COL["demand"],width=2.5),name="Q*"),row=1,col=1)
    fcs.add_trace(go.Scatter(x=rng,y=rP,line=dict(color=COL["mc"],width=2.5),name="P*"),row=1,col=2)
    fcs.add_trace(go.Scatter(x=rng,y=rPi,line=dict(color=COL["atc"],width=2.5),name="π"),row=1,col=3)
    fcs.add_hline(y=0,line=dict(color="grey",dash="dash"),row=1,col=3)
    cur={"fc":FC,"vc":c1,"a":a_base,"b":b_base}[pk]
    for i in range(1,4):
        fcs.update_xaxes(title_text=param,row=1,col=i)
        fcs.add_vline(x=cur,line=dict(color=COL["eq"],width=2,dash="dash"),row=1,col=i)
    fcs.update_yaxes(title_text="Q*",row=1,col=1); fcs.update_yaxes(title_text="P*",row=1,col=2)
    fcs.update_yaxes(title_text="π",row=1,col=3)
    fcs.update_layout(template="plotly_white",height=380,showlegend=False,title=f"{t('statics_title')} — {market_label}")
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
| Profit | $\pi = (P - ATC) \times Q$ |

| Structure | Equilibrium | Long Run |
|-----------|-------------|----------|
| Perfect Comp. | $P = MC$ | $P = \min ATC \Rightarrow \pi = 0$ |
| Monopoly | $MR = MC$ | Barriers $\Rightarrow \pi > 0$ |
| Monopolistic | $MR = MC$ | Tangency $P = ATC \Rightarrow \pi = 0$ |
| Cournot | Nash: best responses | Barriers $\Rightarrow \pi \geq 0$ |
    """)
st.caption(t("footer") + " • Streamlit & Plotly")
