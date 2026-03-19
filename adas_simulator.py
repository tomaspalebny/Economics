import streamlit as st
import plotly.graph_objects as go
import numpy as np
import random
import json

st.set_page_config(page_title="AD-AS Simulátor s náhodnými šoky", layout="wide")
st.title("📈 AD-AS Model: Simulátor s náhodnými šoky")
st.markdown("*Interaktivní hra pro výuku makroekonomie – reagujte na ekonomické šoky fiskální a monetární politikou*")

# ========== SESSION STATE ==========
if "round" not in st.session_state:
    st.session_state.round = 0
    st.session_state.history = []
    st.session_state.shock = None
    st.session_state.shock_applied = False
    st.session_state.score = 0
    st.session_state.game_active = False
    # Baseline equilibrium
    st.session_state.Y_n = 100       # potential output (LRAS)
    st.session_state.Y = 100         # current real GDP
    st.session_state.P = 100         # current price level
    st.session_state.pi = 2.0        # inflation %
    st.session_state.u = 5.0         # unemployment %
    st.session_state.u_n = 5.0       # natural unemployment
    st.session_state.i = 3.0         # interest rate %
    # AD-AS shift accumulators
    st.session_state.ad_shift = 0
    st.session_state.sras_shift = 0

# ========== SHOCK LIBRARY ==========
SHOCKS = [
    {"name": "🛢️ Ropná krize", "desc": "Cena ropy vzrostla o 80%. Náklady firem prudce rostou.", "type": "supply", "sras": +12, "ad": -3, "icon": "🛢️"},
    {"name": "🦠 Pandemie", "desc": "Nová vlna pandemie uzavírá ekonomiku. Klesá spotřeba i výroba.", "type": "both", "sras": +8, "ad": -15, "icon": "🦠"},
    {"name": "🚀 Technologický boom", "desc": "Průlomová technologie zvyšuje produktivitu o 20%.", "type": "supply", "sras": -10, "ad": +5, "icon": "🚀"},
    {"name": "💰 Spotřebitelský optimismus", "desc": "Důvěra spotřebitelů na historickém maximu. Rostou výdaje domácností.", "type": "demand", "sras": 0, "ad": +12, "icon": "💰"},
    {"name": "📉 Finanční krize", "desc": "Krach na burze, banky omezují úvěry. Investice dramaticky klesají.", "type": "demand", "sras": +3, "ad": -18, "icon": "📉"},
    {"name": "🌾 Neúroda a potravinová krize", "desc": "Extrémní sucho zdražuje potraviny a zvyšuje výrobní náklady.", "type": "supply", "sras": +9, "ad": -2, "icon": "🌾"},
    {"name": "🏗️ Investiční boom", "desc": "Masivní příliv zahraničních investic do ekonomiky.", "type": "demand", "sras": -2, "ad": +14, "icon": "🏗️"},
    {"name": "⚔️ Geopolitická krize", "desc": "Válečný konflikt narušuje dodavatelské řetězce a zvyšuje nejistotu.", "type": "both", "sras": +10, "ad": -8, "icon": "⚔️"},
    {"name": "💶 Měnová krize", "desc": "Domácí měna oslabila o 25%. Import dramaticky zdražuje.", "type": "both", "sras": +7, "ad": -5, "icon": "💶"},
    {"name": "🎓 Reforma vzdělávání", "desc": "Masivní investice do vzdělávání zvyšují kvalifikaci pracovní síly.", "type": "supply", "sras": -6, "ad": +3, "icon": "🎓"},
    {"name": "🏠 Prasknutí realitní bubliny", "desc": "Ceny nemovitostí padají o 30%. Domácnosti omezují spotřebu.", "type": "demand", "sras": 0, "ad": -14, "icon": "🏠"},
    {"name": "⚡ Energetická transformace", "desc": "Přechod na OZE dočasně zvyšuje náklady, ale roste produktivita.", "type": "both", "sras": +4, "ad": +6, "icon": "⚡"},
]

# ========== MODEL EQUATIONS ==========
def compute_equilibrium(Y_n, ad_shift, sras_shift):
    """
    Simple linear AD-AS model:
    AD: P = (200 + ad_shift) - Y        (downward sloping)
    SRAS: P = (0 + sras_shift) + 0.5*Y  (upward sloping)
    LRAS: Y = Y_n (vertical)

    Short-run EQ: solve AD = SRAS
    200 + ad_shift - Y = sras_shift + 0.5*Y
    200 + ad_shift - sras_shift = 1.5*Y
    Y = (200 + ad_shift - sras_shift) / 1.5
    P = sras_shift + 0.5 * Y
    """
    Y_eq = (200 + ad_shift - sras_shift) / 1.5
    P_eq = sras_shift + 0.5 * Y_eq

    # Derived macro variables
    output_gap = (Y_eq - Y_n) / Y_n * 100  # %
    inflation = 2.0 + output_gap * 0.4 + sras_shift * 0.15  # simplified Phillips curve
    unemployment = 5.0 - output_gap * 0.5  # Okun's law approx
    unemployment = max(0.5, unemployment)

    return Y_eq, P_eq, output_gap, inflation, unemployment

def compute_score(output_gap, inflation):
    """Score: penalize deviation from targets (Y_gap=0, inflation=2%)"""
    gap_penalty = abs(output_gap) * 3
    inflation_penalty = abs(inflation - 2.0) * 5
    score = max(0, 100 - gap_penalty - inflation_penalty)
    return round(score)

def plot_adas(Y_n, ad_shift, sras_shift, Y_eq, P_eq, prev_ad=None, prev_sras=None):
    """Plot AD, SRAS, LRAS curves and equilibrium"""
    Y_range = np.linspace(40, 160, 200)

    # Current curves
    AD = (200 + ad_shift) - Y_range
    SRAS = (sras_shift) + 0.5 * Y_range

    fig = go.Figure()

    # Previous curves (faded) if provided
    if prev_ad is not None:
        AD_prev = (200 + prev_ad) - Y_range
        SRAS_prev = (prev_sras) + 0.5 * Y_range
        fig.add_trace(go.Scatter(x=Y_range, y=AD_prev, mode="lines", name="AD (před)", line=dict(color="rgba(99,102,241,0.25)", width=2, dash="dot")))
        fig.add_trace(go.Scatter(x=Y_range, y=SRAS_prev, mode="lines", name="SRAS (před)", line=dict(color="rgba(239,68,68,0.25)", width=2, dash="dot")))

    # LRAS
    fig.add_trace(go.Scatter(x=[Y_n, Y_n], y=[40, 170], mode="lines", name=f"LRAS (Yₙ={Y_n:.0f})", line=dict(color="#22c55e", width=3, dash="dash")))

    # Current AD & SRAS
    fig.add_trace(go.Scatter(x=Y_range, y=AD, mode="lines", name="AD", line=dict(color="#6366f1", width=3)))
    fig.add_trace(go.Scatter(x=Y_range, y=SRAS, mode="lines", name="SRAS", line=dict(color="#ef4444", width=3)))

    # Equilibrium point
    fig.add_trace(go.Scatter(x=[Y_eq], y=[P_eq], mode="markers+text", name="Rovnováha",
                             marker=dict(size=14, color="#f59e0b", symbol="diamond"),
                             text=[f"Y={Y_eq:.1f}, P={P_eq:.1f}"], textposition="top right",
                             textfont=dict(size=13, color="#f59e0b")))

    # Dashed lines to axes
    fig.add_trace(go.Scatter(x=[Y_eq, Y_eq], y=[40, P_eq], mode="lines", showlegend=False, line=dict(color="#f59e0b", width=1, dash="dot")))
    fig.add_trace(go.Scatter(x=[40, Y_eq], y=[P_eq, P_eq], mode="lines", showlegend=False, line=dict(color="#f59e0b", width=1, dash="dot")))

    # Shade recession / overheating
    if Y_eq < Y_n - 1:
        fig.add_vrect(x0=Y_eq, x1=Y_n, fillcolor="rgba(239,68,68,0.08)", line_width=0, annotation_text="Recesní mezera", annotation_position="top")
    elif Y_eq > Y_n + 1:
        fig.add_vrect(x0=Y_n, x1=Y_eq, fillcolor="rgba(249,115,22,0.08)", line_width=0, annotation_text="Inflační mezera", annotation_position="top")

    fig.update_layout(
        height=500,
        xaxis=dict(title="Reálný HDP (Y)", range=[40, 160], gridcolor="rgba(100,100,100,0.2)"),
        yaxis=dict(title="Cenová hladina (P)", range=[40, 170], gridcolor="rgba(100,100,100,0.2)"),
        plot_bgcolor="rgba(15,23,42,0.5)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=60, b=60)
    )
    return fig

def plot_history(history):
    if len(history) < 2:
        return None
    rounds = [h["round"] for h in history]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=rounds, y=[h["Y"] for h in history], mode="lines+markers", name="HDP (Y)", line=dict(color="#6366f1", width=2)))
    fig.add_trace(go.Scatter(x=rounds, y=[h["P"] for h in history], mode="lines+markers", name="Cenová hladina (P)", line=dict(color="#ef4444", width=2)))
    fig.add_trace(go.Scatter(x=rounds, y=[h["inflation"] for h in history], mode="lines+markers", name="Inflace (%)", line=dict(color="#f59e0b", width=2)))
    fig.add_trace(go.Scatter(x=rounds, y=[h["unemployment"] for h in history], mode="lines+markers", name="Nezaměstnanost (%)", line=dict(color="#22c55e", width=2)))
    fig.add_hline(y=100, line_dash="dash", line_color="rgba(255,255,255,0.2)", annotation_text="Potenciální produkt")
    fig.add_hline(y=2, line_dash="dash", line_color="rgba(255,255,255,0.15)", annotation_text="Inflační cíl 2%")
    fig.update_layout(
        height=350,
        plot_bgcolor="rgba(15,23,42,0.5)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"),
        xaxis=dict(title="Kolo", dtick=1, gridcolor="rgba(100,100,100,0.2)"),
        yaxis=dict(gridcolor="rgba(100,100,100,0.2)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=60, b=40)
    )
    return fig

# ========== GAME FLOW ==========
st.sidebar.header("🎮 Ovládání hry")

if not st.session_state.game_active:
    st.sidebar.markdown("### Pravidla")
    st.sidebar.markdown("""
    1. Každé kolo přijde **náhodný ekonomický šok**
    2. Vidíte posun křivek AD/SRAS v grafu
    3. Reagujete **fiskální a monetární politikou**
    4. Cíl: udržet HDP blízko potenciálu a inflaci kolem 2%
    5. Za každé kolo dostanete **skóre 0–100**
    """)
    difficulty = st.sidebar.selectbox("Obtížnost", ["🟢 Lehká (malé šoky)", "🟡 Střední", "🔴 Těžká (velké šoky)"])
    n_rounds = st.sidebar.selectbox("Počet kol", [5, 8, 10, 15], index=1)

    if st.sidebar.button("🚀 Začít novou hru", use_container_width=True):
        st.session_state.round = 0
        st.session_state.history = []
        st.session_state.shock = None
        st.session_state.shock_applied = False
        st.session_state.score = 0
        st.session_state.game_active = True
        st.session_state.ad_shift = 0
        st.session_state.sras_shift = 0
        st.session_state.n_rounds = n_rounds
        diff_map = {"🟢 Lehká (malé šoky)": 0.5, "🟡 Střední": 1.0, "🔴 Těžká (velké šoky)": 1.5}
        st.session_state.difficulty = diff_map[difficulty]
        # Record baseline
        Y_eq, P_eq, og, inf, un = compute_equilibrium(100, 0, 0)
        st.session_state.history.append({"round": 0, "Y": Y_eq, "P": P_eq, "inflation": inf, "unemployment": un, "output_gap": og, "score": 100, "shock": "Výchozí stav", "policy": "-"})
        st.rerun()

if st.session_state.game_active:
    ss = st.session_state
    n_rounds = ss.n_rounds

    # Generate shock if needed
    if ss.shock is None and ss.round < n_rounds:
        ss.round += 1
        shock = random.choice(SHOCKS).copy()
        shock["sras"] = round(shock["sras"] * ss.difficulty + random.gauss(0, 2), 1)
        shock["ad"] = round(shock["ad"] * ss.difficulty + random.gauss(0, 2), 1)
        ss.shock = shock
        ss.shock_applied = False
        # Apply shock
        ss.ad_shift += shock["ad"]
        ss.sras_shift += shock["sras"]
        ss.prev_ad = ss.ad_shift - shock["ad"]
        ss.prev_sras = ss.sras_shift - shock["sras"]

    # Current state
    Y_eq, P_eq, og, inf, un = compute_equilibrium(ss.Y_n, ss.ad_shift, ss.sras_shift)

    # SIDEBAR: Policy response
    if ss.shock and not ss.shock_applied and ss.round <= n_rounds:
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"### Kolo {ss.round}/{n_rounds}")
        st.sidebar.markdown(f"## {ss.shock['icon']} {ss.shock['name']}")
        st.sidebar.info(ss.shock["desc"])

        st.sidebar.markdown("### 🏛️ Vaše reakce – fiskální politika")
        fiscal = st.sidebar.number_input("Změna vládních výdajů (% HDP)", min_value=-15.0, max_value=15.0, value=0.0, step=0.5, format="%.1f",
                                          help="+ = expanzivní (více výdajů), - = restriktivní (škrty)")
        tax_change = st.sidebar.number_input("Změna daní (% HDP)", min_value=-10.0, max_value=10.0, value=0.0, step=0.5, format="%.1f",
                                              help="+ = zvýšení daní (restriktivní), - = snížení (expanzivní)")

        st.sidebar.markdown("### 🏦 Monetární politika")
        rate_change = st.sidebar.number_input("Změna úrokové sazby (p.b.)", min_value=-5.0, max_value=5.0, value=0.0, step=0.25, format="%.2f",
                                               help="+ = restriktivní, - = expanzivní")

        if st.sidebar.button("✅ Potvrdit rozhodnutí", use_container_width=True):
            # Policy effects on AD and SRAS
            policy_ad = fiscal * 1.2 - tax_change * 0.8 - rate_change * 2.5
            policy_sras = tax_change * 0.3 + rate_change * 0.2

            ss.ad_shift += policy_ad
            ss.sras_shift += policy_sras

            # Partial mean reversion (economy self-corrects slowly)
            ss.ad_shift *= 0.85
            ss.sras_shift *= 0.85

            # Recalculate
            Y_eq, P_eq, og, inf, un = compute_equilibrium(ss.Y_n, ss.ad_shift, ss.sras_shift)
            round_score = compute_score(og, inf)
            ss.score += round_score

            policy_desc = []
            if fiscal != 0: policy_desc.append(f"Výdaje {fiscal:+.1f}%")
            if tax_change != 0: policy_desc.append(f"Daně {tax_change:+.1f}%")
            if rate_change != 0: policy_desc.append(f"Úrok {rate_change:+.2f} p.b.")
            if not policy_desc: policy_desc = ["Bez zásahu"]

            ss.history.append({
                "round": ss.round, "Y": round(Y_eq, 1), "P": round(P_eq, 1),
                "inflation": round(inf, 1), "unemployment": round(un, 1),
                "output_gap": round(og, 1), "score": round_score,
                "shock": ss.shock["name"], "policy": ", ".join(policy_desc)
            })
            ss.shock_applied = True
            ss.shock = None

            if ss.round >= n_rounds:
                ss.game_active = False
            st.rerun()

    # ========== MAIN DISPLAY ==========
    # Metrics
    mc = st.columns(6)
    mc[0].metric("Kolo", f"{ss.round}/{n_rounds}")
    mc[1].metric("HDP (Y)", f"{Y_eq:.1f}", delta=f"{og:+.1f}% gap", delta_color="inverse" if og < -1 else ("inverse" if og > 3 else "normal"))
    mc[2].metric("Cenová hladina", f"{P_eq:.1f}")
    mc[3].metric("Inflace", f"{inf:.1f}%", delta=f"{inf-2:+.1f} od cíle", delta_color="inverse" if abs(inf-2) > 1 else "normal")
    mc[4].metric("Nezaměstnanost", f"{un:.1f}%", delta=f"{un-5:+.1f} od přirozené", delta_color="inverse" if un > 6 else "normal")
    mc[5].metric("Celkové skóre", f"{ss.score}", delta=f"ø {ss.score/max(1,len(ss.history)-1):.0f}/kolo" if len(ss.history) > 1 else "")

    st.markdown("---")

    # Current shock banner
    if ss.shock and not ss.shock_applied:
        col_shock, col_hint = st.columns([2, 1])
        with col_shock:
            st.error(f"### {ss.shock['icon']} ŠOK: {ss.shock['name']}")
            st.markdown(f"**{ss.shock['desc']}**")
            effect_parts = []
            if ss.shock["ad"] != 0:
                direction = "doprava ↗" if ss.shock["ad"] > 0 else "doleva ↙"
                effect_parts.append(f"AD se posouvá **{direction}** ({ss.shock['ad']:+.1f})")
            if ss.shock["sras"] != 0:
                direction = "nahoru ↑" if ss.shock["sras"] > 0 else "dolů ↓"
                effect_parts.append(f"SRAS se posouvá **{direction}** ({ss.shock['sras']:+.1f})")
            st.markdown(" | ".join(effect_parts))
        with col_hint:
            st.info("💡 **Nápověda:** Použijte šoupátka v postranním panelu k nastavení vaší fiskální a monetární reakce. Pak potvrďte rozhodnutí.")
            if ss.shock["type"] == "demand":
                st.caption("Tip: Poptávkový šok → reagujte protisměrnou poptávkovou politikou")
            elif ss.shock["type"] == "supply":
                st.caption("Tip: Nabídkový šok → dilema: stabilizovat ceny NEBO výstup?")
            else:
                st.caption("Tip: Kombinovaný šok → zvažte oba nástroje")

    # AD-AS Graph
    prev_ad = ss.prev_ad if hasattr(ss, "prev_ad") else None
    prev_sras = ss.prev_sras if hasattr(ss, "prev_sras") else None

    col_graph, col_info = st.columns([3, 1])
    with col_graph:
        st.subheader("AD-AS Diagram")
        fig = plot_adas(ss.Y_n, ss.ad_shift, ss.sras_shift, Y_eq, P_eq, prev_ad, prev_sras)
        st.plotly_chart(fig, use_container_width=True)

    with col_info:
        st.subheader("📊 Stav ekonomiky")
        if og < -3:
            st.error(f"🔴 Hluboká recese (mezera {og:.1f}%)")
        elif og < -1:
            st.warning(f"🟡 Mírná recese (mezera {og:.1f}%)")
        elif og > 3:
            st.error(f"🔴 Přehřátí ekonomiky (+{og:.1f}%)")
        elif og > 1:
            st.warning(f"🟡 Mírné přehřátí (+{og:.1f}%)")
        else:
            st.success(f"🟢 Blízko potenciálu ({og:+.1f}%)")

        if inf > 5:
            st.error(f"🔴 Vysoká inflace ({inf:.1f}%)")
        elif inf > 3:
            st.warning(f"🟡 Zvýšená inflace ({inf:.1f}%)")
        elif inf < 0:
            st.error(f"🔴 Deflace ({inf:.1f}%)")
        elif inf < 1:
            st.warning(f"🟡 Nízká inflace ({inf:.1f}%)")
        else:
            st.success(f"🟢 Inflace v cíli ({inf:.1f}%)")

        if un > 8:
            st.error(f"🔴 Vysoká nezaměstnanost ({un:.1f}%)")
        elif un > 6:
            st.warning(f"🟡 Zvýšená nezaměstnanost ({un:.1f}%)")
        else:
            st.success(f"🟢 Nezaměstnanost OK ({un:.1f}%)")

        st.markdown("---")
        st.markdown("**Posun křivek:**")
        st.markdown(f"- AD shift: **{ss.ad_shift:+.1f}**")
        st.markdown(f"- SRAS shift: **{ss.sras_shift:+.1f}**")

    # History
    if len(ss.history) > 1:
        st.markdown("---")
        col_hist_chart, col_hist_table = st.columns([2, 1])
        with col_hist_chart:
            st.subheader("📈 Vývoj ekonomiky")
            fig_h = plot_history(ss.history)
            if fig_h:
                st.plotly_chart(fig_h, use_container_width=True)
        with col_hist_table:
            st.subheader("📋 Přehled kol")
            for h in reversed(ss.history):
                if h["round"] == 0:
                    continue
                emoji = "🟢" if h["score"] >= 70 else ("🟡" if h["score"] >= 40 else "🔴")
                st.markdown(f"**Kolo {h['round']}** {emoji} Skóre: {h['score']}/100")
                st.caption(f"Šok: {h['shock']} | Reakce: {h['policy']}")
                st.caption(f"Y={h['Y']}, P={h['P']}, π={h['inflation']}%, u={h['unemployment']}%")
                st.markdown("---")

    # GAME OVER
    if not ss.game_active and ss.round > 0:
        st.markdown("---")
        st.balloons()
        avg_score = ss.score / max(1, ss.round)
        st.success(f"## 🏁 Hra skončila! Celkové skóre: {ss.score} bodů (průměr {avg_score:.0f}/kolo)")

        if avg_score >= 80:
            st.markdown("### 🏆 Vynikající! Jste skvělý centrální bankéř i ministr financí.")
        elif avg_score >= 60:
            st.markdown("### 🥈 Dobrá práce! Ekonomika přežila v rozumném stavu.")
        elif avg_score >= 40:
            st.markdown("### 🥉 Uspokojivé. Ekonomika zažila turbulence, ale přežila.")
        else:
            st.markdown("### 😰 Ekonomika je v krizi. Zkuste to znovu s jinou strategií!")

        if st.button("🔄 Nová hra"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# Fallback: show intro if no game
if not st.session_state.game_active and st.session_state.round == 0:
    st.markdown("---")
    col_intro1, col_intro2 = st.columns(2)
    with col_intro1:
        st.subheader("🎯 Jak hra funguje")
        st.markdown("""
        1. **Každé kolo** přijde náhodný ekonomický šok (ropná krize, pandemie, investiční boom…)
        2. **Šok posune** křivky AD a/nebo SRAS v diagramu
        3. **Vy reagujete** fiskální politikou (výdaje, daně) a monetární politikou (úroková sazba)
        4. **Cíl:** udržet HDP blízko potenciálního produktu (Y = 100) a inflaci kolem 2%
        5. **Skóre** reflektuje, jak dobře jste ekonomiku stabilizovali
        """)
    with col_intro2:
        st.subheader("📚 Co se naučíte")
        st.markdown("""
        - Jak funguje **model AD-AS** a co posouvá křivky
        - Rozdíl mezi **poptávkovými a nabídkovými šoky**
        - Jak reagovat **fiskální politikou** (vládní výdaje, daně)
        - Jak reagovat **monetární politikou** (úrokové sazby)
        - Proč je **stagflace** (nabídkový šok) těžší řešit než recese z poklesu poptávky
        - **Trade-off** mezi stabilizací výstupu a cenové hladiny
        """)

    # Demo graph
    st.subheader("Ukázkový AD-AS diagram (výchozí rovnováha)")
    Y_eq, P_eq, _, _, _ = compute_equilibrium(100, 0, 0)
    fig_demo = plot_adas(100, 0, 0, Y_eq, P_eq)
    st.plotly_chart(fig_demo, use_container_width=True)

st.markdown("---")
st.caption("⚠️ Zjednodušený lineární AD-AS model pro výukové účely. Reálná ekonomika je složitější.")
