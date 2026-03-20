import streamlit as st
import plotly.graph_objects as go
import numpy as np
import random

st.set_page_config(page_title="AD-AS Simulátor s náhodnými šoky", layout="wide")
st.title("📈 AD-AS Model: Simulátor s náhodnými šoky")
st.markdown("*Interaktivní hra pro výuku makroekonomie - reagujte na ekonomické šoky fiskální a monetární politikou*")

# ========== SESSION STATE INIT ==========
DEFAULTS = dict(
    round=0, history=[], score=0, game_active=False,
    Y_n=100, ad_shift=0, sras_shift=0,
    phase="idle",  # idle → shock_shown → responded
    shock=None, n_rounds=8, difficulty=1.0,
    prev_ad=0, prev_sras=0,
)
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

ss = st.session_state

# ========== SHOCK LIBRARY ==========
SHOCKS = [
    {"name": "Ropná krize", "desc": "Cena ropy vzrostla o 80 %. Firmy čelí prudce rostoucím nákladům na dopravu a výrobu.", "type": "supply", "sras": +12, "ad": -3, "icon": "🛢️",
     "explain": "Růst cen energie **zvyšuje výrobní náklady** → křivka SRAS se posouvá nahoru (doleva). Drahá energie částečně tlumí i poptávku."},
    {"name": "Pandemie", "desc": "Nová vlna pandemie uzavírá ekonomiku. Klesá spotřeba domácností i výroba firem.", "type": "both", "sras": +8, "ad": -15, "icon": "🦠",
     "explain": "Lockdowny **snižují poptávku** (AD doleva) a zároveň **narušují výrobu** (SRAS nahoru). Kombinovaný šok je nejtěžší na řešení."},
    {"name": "Technologický boom", "desc": "Průlomová technologie (AI) zvyšuje produktivitu firem o 20 %.", "type": "supply", "sras": -10, "ad": +5, "icon": "🚀",
     "explain": "Vyšší produktivita **snižuje jednotkové náklady** → SRAS se posouvá dolů (doprava). Optimismus firem mírně zvyšuje investice (AD doprava)."},
    {"name": "Spotřebitelský optimismus", "desc": "Důvěra spotřebitelů na historickém maximu - domácnosti utrácejí a berou si úvěry.", "type": "demand", "sras": 0, "ad": +12, "icon": "💰",
     "explain": "Rostoucí spotřeba a investice **zvyšují agregátní poptávku** → AD se posouvá doprava. SRAS se nemění - náklady firem zůstávají stejné."},
    {"name": "Finanční krize", "desc": "Krach na burze, banky omezují úvěry. Firmy i domácnosti odkládají investice a nákupy.", "type": "demand", "sras": +3, "ad": -18, "icon": "📉",
     "explain": "Pokles investic a spotřeby **prudce snižuje AD** (doleva). Zpřísnění úvěrů mírně zvyšuje náklady financování firem (SRAS mírně nahoru)."},
    {"name": "Neúroda a potravinová krize", "desc": "Extrémní sucho zdražuje potraviny a zvyšuje výrobní náklady v potravinářství.", "type": "supply", "sras": +9, "ad": -2, "icon": "🌾",
     "explain": "Dražší vstupy **zvyšují náklady výrobců** → SRAS nahoru. Dražší potraviny mírně snižují reálné příjmy domácností (AD mírně doleva)."},
    {"name": "Investiční boom", "desc": "Masivní příliv zahraničních investic - otevírají se nové továrny a centra.", "type": "demand", "sras": -2, "ad": +14, "icon": "🏗️",
     "explain": "Investice **zvyšují poptávku** (AD doprava) a zároveň mírně rozšiřují výrobní kapacity (SRAS mírně dolů)."},
    {"name": "Geopolitická krize", "desc": "Válečný konflikt v blízkém regionu narušuje dodavatelské řetězce a zvyšuje nejistotu.", "type": "both", "sras": +10, "ad": -8, "icon": "⚔️",
     "explain": "Narušení dodávek **zvyšuje náklady** (SRAS nahoru). Nejistota **snižuje spotřebu a investice** (AD doleva). Klasický stagflační scénář."},
    {"name": "Měnová krize", "desc": "Domácí měna oslabila o 25 %. Veškerý import dramaticky zdražuje.", "type": "both", "sras": +7, "ad": -5, "icon": "💶",
     "explain": "Dražší import **zvyšuje výrobní náklady** (SRAS nahoru) a zároveň **snižuje kupní sílu** domácností (AD doleva)."},
    {"name": "Reforma vzdělávání", "desc": "Masivní investice do vzdělávání zvyšují kvalifikaci a produktivitu pracovní síly.", "type": "supply", "sras": -6, "ad": +3, "icon": "🎓",
     "explain": "Kvalifikovanější pracovníci **snižují jednotkové náklady** (SRAS dolů). Vyšší příjmy mírně zvyšují spotřebu (AD doprava). Pozitivní nabídkový šok."},
    {"name": "Prasknutí realitní bubliny", "desc": "Ceny nemovitostí padají o 30 %. Domácnosti se cítí chudší a omezují spotřebu.", "type": "demand", "sras": 0, "ad": -14, "icon": "🏠",
     "explain": "Efekt bohatství: pokles hodnoty majetku **snižuje spotřebu** → AD prudce doleva. Výrobní náklady se nemění, SRAS zůstává."},
    {"name": "Energetická transformace", "desc": "Přechod na obnovitelné zdroje: krátkodobě rostou náklady, ale klesá závislost na dovozu.", "type": "both", "sras": +4, "ad": +6, "icon": "⚡",
     "explain": "Investice do OZE **zvyšují poptávku** (AD doprava), ale přechodné náklady **zvyšují ceny** (SRAS mírně nahoru)."},
]

# ========== MODEL ==========
def compute_eq(Y_n, ad_shift, sras_shift):
    Y = (200 + ad_shift - sras_shift) / 1.5
    P = sras_shift + 0.5 * Y
    og = (Y - Y_n) / Y_n * 100
    inf = 2.0 + og * 0.4 + sras_shift * 0.15
    un = max(0.5, 5.0 - og * 0.5)
    return Y, P, og, inf, un

def score(og, inf):
    return round(max(0, 100 - abs(og) * 3 - abs(inf - 2.0) * 5))

def plot_adas(Y_n, ad_shift, sras_shift, Y_eq, P_eq, prev_ad=None, prev_sras=None, title=""):
    Yr = np.linspace(40, 160, 200)
    AD = (200 + ad_shift) - Yr
    SRAS = sras_shift + 0.5 * Yr
    fig = go.Figure()

    if prev_ad is not None:
        AD0 = (200 + prev_ad) - Yr
        SRAS0 = prev_sras + 0.5 * Yr
        Y0 = (200 + prev_ad - prev_sras) / 1.5
        P0 = prev_sras + 0.5 * Y0
        fig.add_trace(go.Scatter(x=Yr, y=AD0, mode="lines", name="AD předtím", line=dict(color="rgba(99,102,241,0.25)", width=2, dash="dot")))
        fig.add_trace(go.Scatter(x=Yr, y=SRAS0, mode="lines", name="SRAS předtím", line=dict(color="rgba(239,68,68,0.25)", width=2, dash="dot")))
        fig.add_trace(go.Scatter(x=[Y0], y=[P0], mode="markers", name="Předchozí rovnováha",
                                 marker=dict(size=10, color="rgba(245,158,11,0.35)", symbol="diamond")))

    fig.add_trace(go.Scatter(x=[Y_n, Y_n], y=[40, 170], mode="lines", name=f"LRAS (Yₙ={Y_n:.0f})", line=dict(color="#22c55e", width=3, dash="dash")))
    fig.add_trace(go.Scatter(x=Yr, y=AD, mode="lines", name="AD", line=dict(color="#6366f1", width=3)))
    fig.add_trace(go.Scatter(x=Yr, y=SRAS, mode="lines", name="SRAS", line=dict(color="#ef4444", width=3)))
    fig.add_trace(go.Scatter(x=[Y_eq], y=[P_eq], mode="markers+text", name="Rovnováha",
                             marker=dict(size=14, color="#f59e0b", symbol="diamond"),
                             text=[f"Y={Y_eq:.1f}, P={P_eq:.1f}"], textposition="top right",
                             textfont=dict(size=13, color="#f59e0b")))
    fig.add_trace(go.Scatter(x=[Y_eq, Y_eq], y=[40, P_eq], mode="lines", showlegend=False, line=dict(color="#f59e0b", width=1, dash="dot")))
    fig.add_trace(go.Scatter(x=[40, Y_eq], y=[P_eq, P_eq], mode="lines", showlegend=False, line=dict(color="#f59e0b", width=1, dash="dot")))

    if Y_eq < Y_n - 1:
        fig.add_vrect(x0=Y_eq, x1=Y_n, fillcolor="rgba(239,68,68,0.08)", line_width=0, annotation_text="Recesní mezera", annotation_position="top")
    elif Y_eq > Y_n + 1:
        fig.add_vrect(x0=Y_n, x1=Y_eq, fillcolor="rgba(249,115,22,0.08)", line_width=0, annotation_text="Inflační mezera", annotation_position="top")

    fig.update_layout(
        title=dict(text=title, font=dict(size=16)),
        height=480, xaxis=dict(title="Reálný HDP (Y)", range=[40, 160], gridcolor="rgba(100,100,100,0.2)"),
        yaxis=dict(title="Cenová hladina (P)", range=[40, 170], gridcolor="rgba(100,100,100,0.2)"),
        plot_bgcolor="rgba(15,23,42,0.5)", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#e2e8f0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02), margin=dict(t=60, b=60))
    return fig

def plot_history(history):
    if len(history) < 2:
        return None
    rounds = [h["round"] for h in history]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=rounds, y=[h["Y"] for h in history], mode="lines+markers", name="HDP (Y)", line=dict(color="#6366f1", width=2)))
    fig.add_trace(go.Scatter(x=rounds, y=[h["P"] for h in history], mode="lines+markers", name="Cen. hladina (P)", line=dict(color="#ef4444", width=2)))
    fig.add_trace(go.Scatter(x=rounds, y=[h["inflation"] for h in history], mode="lines+markers", name="Inflace (%)", line=dict(color="#f59e0b", width=2)))
    fig.add_trace(go.Scatter(x=rounds, y=[h["unemployment"] for h in history], mode="lines+markers", name="Nezaměstnanost (%)", line=dict(color="#22c55e", width=2)))
    fig.add_hline(y=100, line_dash="dash", line_color="rgba(255,255,255,0.2)", annotation_text="Potenciální produkt")
    fig.add_hline(y=2, line_dash="dash", line_color="rgba(255,255,255,0.15)", annotation_text="Inflační cíl 2 %")
    fig.update_layout(height=320, plot_bgcolor="rgba(15,23,42,0.5)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"), xaxis=dict(title="Kolo", dtick=1, gridcolor="rgba(100,100,100,0.2)"),
        yaxis=dict(gridcolor="rgba(100,100,100,0.2)"), legend=dict(orientation="h", yanchor="bottom", y=1.02), margin=dict(t=50, b=40))
    return fig

# ========== SIDEBAR ==========
st.sidebar.header("🎮 Ovládání hry")

# --- PHASE: IDLE (no game) ---
if not ss.game_active and ss.phase == "idle":
    st.sidebar.markdown("### Nastavení hry")
    difficulty = st.sidebar.selectbox("Obtížnost", ["🟢 Lehká (malé šoky)", "🟡 Střední", "🔴 Těžká (velké šoky)"])
    n_rounds = st.sidebar.selectbox("Počet kol", [5, 8, 10, 15], index=1)

    if st.sidebar.button("🚀 Začít novou hru", use_container_width=True):
        diff_map = {"🟢 Lehká (malé šoky)": 0.5, "🟡 Střední": 1.0, "🔴 Těžká (velké šoky)": 1.5}
        for k, v in DEFAULTS.items():
            ss[k] = v
        ss.game_active = True
        ss.n_rounds = n_rounds
        ss.difficulty = diff_map[difficulty]
        ss.phase = "pre_shock"
        ss.round = 0
        Y0, P0, og0, inf0, un0 = compute_eq(100, 0, 0)
        ss.history = [dict(round=0, Y=Y0, P=P0, inflation=inf0, unemployment=un0, output_gap=og0, score=100, shock="-", policy="-")]
        st.rerun()

# --- PHASE: PRE_SHOCK → generate shock ---
if ss.game_active and ss.phase == "pre_shock":
    ss.round += 1
    shock = random.choice(SHOCKS).copy()
    shock["sras"] = round(shock["sras"] * ss.difficulty + random.gauss(0, 1.5), 1)
    shock["ad"] = round(shock["ad"] * ss.difficulty + random.gauss(0, 1.5), 1)
    ss.shock = shock
    ss.prev_ad = ss.ad_shift
    ss.prev_sras = ss.sras_shift
    ss.ad_shift += shock["ad"]
    ss.sras_shift += shock["sras"]
    ss.phase = "shock_shown"
    st.rerun()

# --- PHASE: SHOCK_SHOWN → student responds ---
if ss.game_active and ss.phase == "shock_shown":
    sh = ss.shock
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"### Kolo {ss.round} / {ss.n_rounds}")
    st.sidebar.markdown(f"## {sh['icon']} {sh['name']}")

    st.sidebar.markdown("### 🏛️ Fiskální politika")
    fiscal = st.sidebar.number_input("Změna vládních výdajů (% HDP)", -15.0, 15.0, 0.0, 0.5, format="%.1f",
        help="Kladné = expanze (více utrácíte), záporné = úspory")
    tax_ch = st.sidebar.number_input("Změna daní (% HDP)", -10.0, 10.0, 0.0, 0.5, format="%.1f",
        help="Kladné = vyšší daně (restriktivní), záporné = nižší daně (expanzivní)")

    st.sidebar.markdown("### 🏦 Monetární politika")
    rate_ch = st.sidebar.number_input("Změna úrokové sazby (p.b.)", -5.0, 5.0, 0.0, 0.25, format="%.2f",
        help="Kladné = vyšší sazby (restriktivní), záporné = nižší (expanzivní)")

    if st.sidebar.button("✅ Potvrdit rozhodnutí", use_container_width=True):
        pol_ad = fiscal * 1.2 - tax_ch * 0.8 - rate_ch * 2.5
        pol_sras = tax_ch * 0.3 + rate_ch * 0.2
        ss.ad_shift += pol_ad
        ss.sras_shift += pol_sras
        ss.ad_shift *= 0.85
        ss.sras_shift *= 0.85

        Y, P, og, inf, un = compute_eq(ss.Y_n, ss.ad_shift, ss.sras_shift)
        sc = score(og, inf)
        ss.score += sc

        pdesc = []
        if fiscal != 0: pdesc.append(f"Výdaje {fiscal:+.1f} %")
        if tax_ch != 0: pdesc.append(f"Daně {tax_ch:+.1f} %")
        if rate_ch != 0: pdesc.append(f"Úrok {rate_ch:+.2f} p.b.")
        if not pdesc: pdesc = ["Bez zásahu"]

        ss.history.append(dict(round=ss.round, Y=round(Y, 1), P=round(P, 1), inflation=round(inf, 1),
            unemployment=round(un, 1), output_gap=round(og, 1), score=sc,
            shock=f"{sh['icon']} {sh['name']}", policy=", ".join(pdesc)))

        if ss.round >= ss.n_rounds:
            ss.phase = "game_over"
            ss.game_active = False
        else:
            ss.phase = "pre_shock"
        st.rerun()

# ========== MAIN CONTENT ==========

# ---------- INTRO SCREEN ----------
if ss.phase == "idle":
    st.info("👈 Nastavte obtížnost a počet kol v postranním panelu a klikněte **Začít novou hru**.")
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🎯 Jak hra funguje")
        st.markdown("""
        Hra simuluje roli **ekonomického poradce vlády**. Každé kolo:

        1. 📢 **Přijde šok** - náhodná ekonomická událost posune křivky AD nebo SRAS
        2. 📊 **Vidíte dopad** - v diagramu se zobrazí nová rovnováha po šoku
        3. 🎛️ **Reagujete** - nastavíte fiskální politiku (výdaje, daně) a monetární politiku (úrokové sazby)
        4. ✅ **Vyhodnocení** - model spočítá výsledek vaší reakce, dostanete skóre 0-100

        **Cíl:** udržet ekonomiku co nejblíže potenciálnímu produktu (Y = 100) a inflaci kolem 2 %.
        """)
    with c2:
        st.subheader("📚 Co se naučíte")
        st.markdown("""
        - Jak **poptávkové šoky** (finanční krize, investiční boom) posouvají křivku AD
        - Jak **nabídkové šoky** (ropná krize, technologie) posouvají SRAS
        - Proč je **stagflace** obtížná - nabídkový šok vytváří dilema mezi inflací a recesí
        - Jak funguje **fiskální politika** (vládní výdaje a daně)
        - Jak funguje **monetární politika** (úrokové sazby centrální banky)
        - Proč **kombinované šoky** (pandemie) vyžadují sofistikovanou reakci
        """)

    st.subheader("Ukázkový AD-AS diagram - výchozí rovnováha")
    Y0, P0, _, _, _ = compute_eq(100, 0, 0)
    st.plotly_chart(plot_adas(100, 0, 0, Y0, P0, title="Výchozí stav: Y = Yₙ = 100, π = 2 %"), use_container_width=True)
    st.caption("""
    **Jak číst diagram:** Svislá osa = cenová hladina (P), vodorovná = reálný HDP (Y).  
    **AD** (modrá) = agregátní poptávka - klesající, protože vyšší ceny snižují reálnou kupní sílu.  
    **SRAS** (červená) = krátkodobá agregátní nabídka - rostoucí, protože vyšší ceny motivují firmy více vyrábět.  
    **LRAS** (zelená čárkovaná) = dlouhodobá nabídka - potenciální produkt ekonomiky.  
    **Žlutý diamant** = průsečík AD a SRAS = krátkodobá rovnováha.
    """)

# ---------- ACTIVE GAME ----------
if ss.phase in ("shock_shown", "pre_shock"):
    sh = ss.shock
    Y_eq, P_eq, og, inf, un = compute_eq(ss.Y_n, ss.ad_shift, ss.sras_shift)

    # ---- TOP METRICS ----
    mc = st.columns(6)
    mc[0].metric("Kolo", f"{ss.round} / {ss.n_rounds}")
    mc[1].metric("HDP (Y)", f"{Y_eq:.1f}", delta=f"{og:+.1f} % gap")
    mc[2].metric("Cenová hladina", f"{P_eq:.1f}")
    mc[3].metric("Inflace", f"{inf:.1f} %", delta=f"{inf - 2:+.1f} od cíle")
    mc[4].metric("Nezaměstnanost", f"{un:.1f} %")
    mc[5].metric("Skóre", f"{ss.score}", delta=f"ø {ss.score / max(1, len(ss.history) - 1):.0f}/kolo" if len(ss.history) > 1 else "")

    st.markdown("---")

    # ---- STEP 1: SHOCK ANNOUNCEMENT ----
    st.markdown("## 📢 Krok 1 - Co se stalo")
    col_ev, col_mech = st.columns([3, 2])
    with col_ev:
        st.error(f"### {sh['icon']} {sh['name']}")
        st.markdown(f"**{sh['desc']}**")
    with col_mech:
        st.warning("#### ⚙️ Ekonomický mechanismus")
        st.markdown(sh["explain"])

    # ---- STEP 2: IMPACT ON CURVES ----
    st.markdown("## 📊 Krok 2 - Dopad na ekonomiku")
    st.markdown("Níže vidíte, jak se šok projevil v AD-AS diagramu. **Průsvitné čárkované křivky** = stav před šokem. **Plné křivky** = stav po šoku.")

    col_graph, col_status = st.columns([3, 1])
    with col_graph:
        fig = plot_adas(ss.Y_n, ss.ad_shift, ss.sras_shift, Y_eq, P_eq, ss.prev_ad, ss.prev_sras,
                        title=f"Kolo {ss.round}: Po šoku '{sh['name']}" - PŘED vaší reakcí")
        st.plotly_chart(fig, use_container_width=True)

    with col_status:
        st.markdown("### Posuny křivek")
        if sh["ad"] > 0:
            st.markdown(f"➡️ AD doprava: **+{sh['ad']:.1f}**")
            st.caption("Poptávka roste → HDP roste, ceny rostou")
        elif sh["ad"] < 0:
            st.markdown(f"⬅️ AD doleva: **{sh['ad']:.1f}**")
            st.caption("Poptávka klesá → HDP klesá, ceny klesají")
        else:
            st.markdown("↔️ AD beze změny")

        if sh["sras"] > 0:
            st.markdown(f"⬆️ SRAS nahoru: **+{sh['sras']:.1f}**")
            st.caption("Náklady rostou → firmy vyrábějí méně za vyšší ceny")
        elif sh["sras"] < 0:
            st.markdown(f"⬇️ SRAS dolů: **{sh['sras']:.1f}**")
            st.caption("Náklady klesají → firmy vyrábějí více za nižší ceny")
        else:
            st.markdown("↔️ SRAS beze změny")

        st.markdown("---")
        st.markdown("### Stav ekonomiky")
        if og < -3:
            st.error(f"🔴 Hluboká recese ({og:+.1f} %)")
        elif og < -1:
            st.warning(f"🟡 Mírná recese ({og:+.1f} %)")
        elif og > 3:
            st.error(f"🔴 Přehřátí ({og:+.1f} %)")
        elif og > 1:
            st.warning(f"🟡 Mírné přehřátí ({og:+.1f} %)")
        else:
            st.success(f"🟢 Blízko potenciálu ({og:+.1f} %)")

        if inf > 5:
            st.error(f"🔴 Vysoká inflace ({inf:.1f} %)")
        elif inf > 3:
            st.warning(f"🟡 Zvýšená inflace ({inf:.1f} %)")
        elif inf < 0:
            st.error(f"🔴 Deflace ({inf:.1f} %)")
        elif inf < 1:
            st.warning(f"🟡 Nízká inflace ({inf:.1f} %)")
        else:
            st.success(f"🟢 Inflace v cíli ({inf:.1f} %)")

    # ---- STEP 3: POLICY HINT ----
    st.markdown("## 🎛️ Krok 3 - Vaše reakce")
    st.markdown("Nastavte svou fiskální a monetární politiku **v postranním panelu vlevo** a klikněte **Potvrdit rozhodnutí**.")

    with st.expander("💡 Nápověda: Jak reagovat na tento typ šoku?", expanded=False):
        if sh["type"] == "demand":
            st.markdown("""
            **Poptávkový šok** - relativně přímočaré řešení:
            - Pokud AD klesla (recese): zvyšte výdaje, snižte daně, snižte úrokovou sazbu → posunete AD zpět doprava
            - Pokud AD vzrostla (přehřátí): škrtěte výdaje, zvyšte daně, zvyšte sazbu → AD zpět doleva
            - U čistě poptávkového šoku můžete stabilizovat **zároveň** výstup i ceny
            """)
        elif sh["type"] == "supply":
            st.markdown("""
            **Nabídkový šok** - dilema!
            - SRAS se posunula → výstup a ceny se pohybují **protisměrně**
            - Pokud stimulujete poptávku (AD doprava), zvýšíte výstup, ale zároveň ještě víc roste inflace
            - Pokud tlumíte inflaci (AD doleva), prohloubíte recesi
            - Musíte zvolit **kompromis** - co je priorita: ceny, nebo zaměstnanost?
            """)
        else:
            st.markdown("""
            **Kombinovaný šok** - nejtěžší situace:
            - AD i SRAS se posunuly současně
            - Zvažte, který efekt je silnější, a reagujte primárně na něj
            - Často není možné dosáhnout dokonalé stabilizace - minimalizujte celkovou škodu
            """)

    # ---- HISTORY ----
    if len(ss.history) > 1:
        st.markdown("---")
        st.subheader("📈 Dosavadní vývoj")
        fig_h = plot_history(ss.history)
        if fig_h:
            st.plotly_chart(fig_h, use_container_width=True)
        with st.expander("📋 Tabulka předchozích kol"):
            for h in reversed(ss.history):
                if h["round"] == 0: continue
                emoji = "🟢" if h["score"] >= 70 else ("🟡" if h["score"] >= 40 else "🔴")
                st.markdown(f"**Kolo {h['round']}** {emoji} Skóre: {h['score']}/100 | Šok: {h['shock']} | Reakce: {h['policy']} | Y={h['Y']}, π={h['inflation']} %, u={h['unemployment']} %")

# ---------- GAME OVER ----------
if ss.phase == "game_over":
    st.balloons()
    avg = ss.score / max(1, ss.round)

    st.success(f"## 🏁 Hra skončila! Celkové skóre: **{ss.score} bodů** (průměr **{avg:.0f}**/kolo)")
    if avg >= 80:
        st.markdown("### 🏆 Vynikající! Jste skvělý ekonomický stratég.")
    elif avg >= 60:
        st.markdown("### 🥈 Dobrá práce! Ekonomika přežila v rozumném stavu.")
    elif avg >= 40:
        st.markdown("### 🥉 Uspokojivé. Ekonomika zažila turbulence.")
    else:
        st.markdown("### 😰 Ekonomika je v krizi. Zkuste jinou strategii!")

    st.markdown("---")
    st.subheader("📈 Celkový vývoj")
    fig_h = plot_history(ss.history)
    if fig_h:
        st.plotly_chart(fig_h, use_container_width=True)

    st.subheader("📋 Přehled všech kol")
    import pandas as pd
    df = pd.DataFrame(ss.history[1:])
    df.columns = ["Kolo", "HDP", "Cen. hladina", "Inflace %", "Nezam. %", "Output gap %", "Skóre", "Šok", "Reakce"]
    st.dataframe(df, use_container_width=True, hide_index=True)

    if st.button("🔄 Nová hra", use_container_width=True):
        for k, v in DEFAULTS.items():
            ss[k] = v
        st.rerun()

st.markdown("---")
st.caption("⚠️ Zjednodušený lineární AD-AS model pro výukové účely. Reálná ekonomika je podstatně složitější.")
