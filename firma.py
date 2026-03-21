
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Firm Equilibrium Simulator", layout="wide", page_icon="📈")

st.title("📈 Interactive Firm Equilibrium Simulator")
st.markdown("Explore how firms reach equilibrium under different market structures and respond to parameter changes.")

# ─── Sidebar: Market Structure & Parameters ───
st.sidebar.header("⚙️ Market Structure")
market = st.sidebar.selectbox("Select Market Structure",
    ["Perfect Competition", "Monopoly", "Monopolistic Competition", "Duopoly (Cournot)"])

st.sidebar.header("💰 Cost Parameters")
FC = st.sidebar.slider("Fixed Cost (FC)", 0, 500, 100, 10)
c_var = st.sidebar.slider("Variable Cost coefficient (c)", 1.0, 50.0, 10.0, 0.5,
                           help="Linear term in VC = c·Q + d·Q²")
d_var = st.sidebar.slider("Variable Cost coefficient (d)", 0.01, 2.0, 0.5, 0.01,
                           help="Quadratic term in VC = c·Q + d·Q²")

st.sidebar.header("🏪 Market / Demand Parameters")
if market == "Perfect Competition":
    P_market = st.sidebar.slider("Market Price (P)", 5.0, 100.0, 40.0, 0.5)
    a_demand = None
    b_demand = None
else:
    a_demand = st.sidebar.slider("Demand Intercept (a)", 20.0, 200.0, 100.0, 1.0,
                                  help="P = a − b·Q  →  max willingness to pay")
    b_demand = st.sidebar.slider("Demand Slope (b)", 0.1, 5.0, 1.0, 0.05,
                                  help="P = a − b·Q  →  price sensitivity")
    if market == "Monopolistic Competition":
        n_firms = st.sidebar.slider("Number of firms (n)", 2, 20, 5,
                                     help="More firms → more elastic individual demand")
    if market == "Duopoly (Cournot)":
        c_var2 = st.sidebar.slider("Firm 2: Variable Cost (c₂)", 1.0, 50.0, 10.0, 0.5)
        d_var2 = st.sidebar.slider("Firm 2: Quadratic Cost (d₂)", 0.01, 2.0, 0.5, 0.01)

# ─── Helper: Cost curves ───
def cost_curves(Q, fc, c, d):
    TC = fc + c * Q + d * Q**2
    MC = c + 2 * d * Q
    with np.errstate(divide='ignore', invalid='ignore'):
        ATC = np.where(Q > 0, TC / Q, np.nan)
        AVC = np.where(Q > 0, (c * Q + d * Q**2) / Q, np.nan)
    return TC, MC, ATC, AVC

Q_max_global = 150
Q = np.linspace(0.1, Q_max_global, 800)
TC, MC, ATC, AVC = cost_curves(Q, FC, c_var, d_var)

# ─── Color palette ───
COL = dict(demand="#2196F3", mr="#FF9800", mc="#E53935", atc="#4CAF50",
           avc="#8BC34A", profit="#81D4FA", loss="#EF9A9A",
           firm2="#9C27B0", react1="#2196F3", react2="#E53935",
           supply="#FF5722", eq="#FFD600")

# ═══════════════════════════════════════════════════
#  PERFECT COMPETITION
# ═══════════════════════════════════════════════════
if market == "Perfect Competition":
    # Equilibrium: P = MC  →  P = c + 2dQ  →  Q* = (P - c) / (2d)
    Q_star = max((P_market - c_var) / (2 * d_var), 0)
    TR_star = P_market * Q_star
    TC_star = FC + c_var * Q_star + d_var * Q_star**2
    profit = TR_star - TC_star
    ATC_star = TC_star / Q_star if Q_star > 0 else 0
    AVC_star = c_var + d_var * Q_star if Q_star > 0 else 0
    shutdown = P_market < (c_var)  # P < min AVC

    col1, col2 = st.columns([2, 1])

    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=Q, y=MC, name="MC", line=dict(color=COL["mc"], width=2.5)))
        fig.add_trace(go.Scatter(x=Q, y=ATC, name="ATC", line=dict(color=COL["atc"], width=2, dash="dash")))
        fig.add_trace(go.Scatter(x=Q, y=AVC, name="AVC", line=dict(color=COL["avc"], width=2, dash="dot")))
        fig.add_hline(y=P_market, line=dict(color=COL["demand"], width=2),
                      annotation_text=f"P = MR = AR = {P_market:.1f}")

        if Q_star > 0 and not shutdown:
            # Shade profit / loss
            q_fill = np.linspace(0.1, Q_star, 200)
            _, _, atc_fill, _ = cost_curves(q_fill, FC, c_var, d_var)
            if profit >= 0:
                fig.add_trace(go.Scatter(
                    x=np.concatenate([q_fill, q_fill[::-1]]),
                    y=np.concatenate([np.full_like(q_fill, P_market), atc_fill[::-1]]),
                    fill="toself", fillcolor="rgba(129,212,250,0.35)",
                    line=dict(width=0), name=f"Profit = {profit:.1f}", showlegend=True))
            else:
                fig.add_trace(go.Scatter(
                    x=np.concatenate([q_fill, q_fill[::-1]]),
                    y=np.concatenate([atc_fill, np.full_like(q_fill, P_market)[::-1]]),
                    fill="toself", fillcolor="rgba(239,154,154,0.35)",
                    line=dict(width=0), name=f"Loss = {profit:.1f}", showlegend=True))
            fig.add_trace(go.Scatter(x=[Q_star], y=[P_market], mode="markers",
                                     marker=dict(size=12, color=COL["eq"], line=dict(width=2, color="black")),
                                     name=f"Q* = {Q_star:.1f}"))

        fig.update_layout(title="Perfect Competition – Firm Equilibrium",
                          xaxis_title="Quantity (Q)", yaxis_title="Price / Cost",
                          yaxis=dict(range=[0, max(P_market * 2, 80)]),
                          xaxis=dict(range=[0, min(Q_star * 3 + 10, Q_max_global)]),
                          template="plotly_white", height=520, legend=dict(x=0.65, y=0.98))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Equilibrium Values")
        if shutdown:
            st.error("🛑 **Shutdown**: P < min AVC. The firm does not produce.")
        else:
            st.metric("Optimal Quantity (Q*)", f"{Q_star:.2f}")
            st.metric("Market Price", f"{P_market:.2f}")
            st.metric("ATC at Q*", f"{ATC_star:.2f}")
            st.metric("Total Revenue", f"{TR_star:.2f}")
            st.metric("Total Cost", f"{TC_star:.2f}")
            delta_col = "normal" if profit >= 0 else "inverse"
            st.metric("Economic Profit", f"{profit:.2f}", delta=f"{'Positive' if profit > 0 else 'Zero' if profit == 0 else 'Loss'}", delta_color=delta_col)

        st.markdown("---")
        st.markdown("""
        **Key rules**
        - Produce where **P = MC**
        - Shut down if **P < min AVC**
        - Long-run: P = min ATC → zero economic profit
        """)

# ═══════════════════════════════════════════════════
#  MONOPOLY
# ═══════════════════════════════════════════════════
elif market == "Monopoly":
    # Demand: P = a - bQ,  MR = a - 2bQ
    # MR = MC  →  a - 2bQ = c + 2dQ  →  Q* = (a - c) / (2b + 2d)
    Q_star = max((a_demand - c_var) / (2 * b_demand + 2 * d_var), 0)
    P_star = a_demand - b_demand * Q_star
    TR_star = P_star * Q_star
    TC_star = FC + c_var * Q_star + d_var * Q_star**2
    profit = TR_star - TC_star
    ATC_star = TC_star / Q_star if Q_star > 0 else 0
    MR_star = a_demand - 2 * b_demand * Q_star

    P_demand = a_demand - b_demand * Q
    MR_curve = a_demand - 2 * b_demand * Q
    Q_intercept = a_demand / b_demand

    col1, col2 = st.columns([2, 1])
    with col1:
        fig = go.Figure()
        mask = P_demand >= 0
        fig.add_trace(go.Scatter(x=Q[mask], y=P_demand[mask], name="Demand (AR)", line=dict(color=COL["demand"], width=2.5)))
        mask_mr = MR_curve >= -20
        fig.add_trace(go.Scatter(x=Q[mask_mr], y=MR_curve[mask_mr], name="MR", line=dict(color=COL["mr"], width=2.5)))
        fig.add_trace(go.Scatter(x=Q, y=MC, name="MC", line=dict(color=COL["mc"], width=2.5)))
        fig.add_trace(go.Scatter(x=Q, y=ATC, name="ATC", line=dict(color=COL["atc"], width=2, dash="dash")))
        fig.add_trace(go.Scatter(x=Q, y=AVC, name="AVC", line=dict(color=COL["avc"], width=2, dash="dot")))

        if Q_star > 0:
            q_fill = np.linspace(0.1, Q_star, 200)
            _, _, atc_fill, _ = cost_curves(q_fill, FC, c_var, d_var)
            if profit >= 0:
                fig.add_trace(go.Scatter(
                    x=np.concatenate([q_fill, q_fill[::-1]]),
                    y=np.concatenate([np.full_like(q_fill, P_star), atc_fill[::-1]]),
                    fill="toself", fillcolor="rgba(129,212,250,0.30)",
                    line=dict(width=0), name=f"Profit = {profit:.1f}"))
            else:
                fig.add_trace(go.Scatter(
                    x=np.concatenate([q_fill, q_fill[::-1]]),
                    y=np.concatenate([atc_fill, np.full_like(q_fill, P_star)[::-1]]),
                    fill="toself", fillcolor="rgba(239,154,154,0.30)",
                    line=dict(width=0), name=f"Loss = {profit:.1f}"))

            # DWL triangle
            Q_comp = max((a_demand - c_var) / (b_demand + 2 * d_var), 0)
            P_comp = a_demand - b_demand * Q_comp
            fig.add_trace(go.Scatter(
                x=[Q_star, Q_star, Q_comp, Q_star],
                y=[P_star, MR_star, P_comp, P_star],
                fill="toself", fillcolor="rgba(255,152,0,0.18)",
                line=dict(width=1, color=COL["mr"], dash="dot"),
                name="Deadweight Loss"))

            fig.add_trace(go.Scatter(x=[Q_star], y=[P_star], mode="markers+text",
                text=[f"  Q*={Q_star:.1f}, P*={P_star:.1f}"], textposition="top right",
                marker=dict(size=12, color=COL["eq"], line=dict(width=2, color="black")),
                name="Equilibrium"))
            fig.add_hline(y=P_star, line=dict(color="grey", width=1, dash="dot"))
            fig.add_vline(x=Q_star, line=dict(color="grey", width=1, dash="dot"))

        y_max = max(a_demand * 1.1, ATC[10] * 1.2)
        fig.update_layout(title="Monopoly – Firm Equilibrium (MR = MC)",
                          xaxis_title="Quantity (Q)", yaxis_title="Price / Cost",
                          yaxis=dict(range=[0, y_max]),
                          xaxis=dict(range=[0, min(Q_intercept * 1.1, Q_max_global)]),
                          template="plotly_white", height=520, legend=dict(x=0.65, y=0.98))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Equilibrium Values")
        st.metric("Optimal Quantity (Q*)", f"{Q_star:.2f}")
        st.metric("Price (P*)", f"{P_star:.2f}")
        st.metric("Marginal Revenue at Q*", f"{MR_star:.2f}")
        st.metric("Marginal Cost at Q*", f"{(c_var + 2*d_var*Q_star):.2f}")
        st.metric("ATC at Q*", f"{ATC_star:.2f}")
        st.metric("Total Revenue", f"{TR_star:.2f}")
        st.metric("Total Cost", f"{TC_star:.2f}")
        delta_col = "normal" if profit >= 0 else "inverse"
        st.metric("Economic Profit", f"{profit:.2f}",
                  delta=f"{'Supernormal' if profit > 0 else 'Zero' if profit == 0 else 'Loss'}",
                  delta_color=delta_col)
        lerner = (P_star - (c_var + 2*d_var*Q_star)) / P_star if P_star > 0 else 0
        st.metric("Lerner Index", f"{lerner:.3f}")
        st.markdown("---")
        st.markdown("""
        **Key rules**
        - Produce where **MR = MC**
        - Price read from **demand curve**
        - Deadweight loss (orange) = allocative inefficiency
        - Lerner Index measures market power
        """)

# ═══════════════════════════════════════════════════
#  MONOPOLISTIC COMPETITION
# ═══════════════════════════════════════════════════
elif market == "Monopolistic Competition":
    st.sidebar.header("📊 Run Type")
    run_type = st.sidebar.radio("Time Horizon", ["Short Run", "Long Run"])

    if run_type == "Short Run":
        # Individual firm demand is more elastic: slope = b * n (share of market)
        b_firm = b_demand * (1 + 0.3 * (n_firms - 1))
        a_firm = a_demand / (n_firms ** 0.4)
        Q_star = max((a_firm - c_var) / (2 * b_firm + 2 * d_var), 0)
        P_star = a_firm - b_firm * Q_star
        TR_star = P_star * Q_star
        TC_star = FC + c_var * Q_star + d_var * Q_star**2
        profit = TR_star - TC_star
        ATC_star = TC_star / Q_star if Q_star > 0 else 0
        MR_star = a_firm - 2 * b_firm * Q_star

        P_demand = a_firm - b_firm * Q
        MR_curve = a_firm - 2 * b_firm * Q

        col1, col2 = st.columns([2, 1])
        with col1:
            fig = go.Figure()
            mask = P_demand >= 0
            fig.add_trace(go.Scatter(x=Q[mask], y=P_demand[mask], name="Firm Demand (d)", line=dict(color=COL["demand"], width=2.5)))
            mask_mr = MR_curve >= -10
            fig.add_trace(go.Scatter(x=Q[mask_mr], y=MR_curve[mask_mr], name="MR", line=dict(color=COL["mr"], width=2.5)))
            fig.add_trace(go.Scatter(x=Q, y=MC, name="MC", line=dict(color=COL["mc"], width=2.5)))
            fig.add_trace(go.Scatter(x=Q, y=ATC, name="ATC", line=dict(color=COL["atc"], width=2, dash="dash")))

            if Q_star > 0:
                q_fill = np.linspace(0.1, Q_star, 200)
                _, _, atc_fill, _ = cost_curves(q_fill, FC, c_var, d_var)
                if profit >= 0:
                    fig.add_trace(go.Scatter(
                        x=np.concatenate([q_fill, q_fill[::-1]]),
                        y=np.concatenate([np.full_like(q_fill, P_star), atc_fill[::-1]]),
                        fill="toself", fillcolor="rgba(129,212,250,0.30)",
                        line=dict(width=0), name=f"Profit = {profit:.1f}"))
                else:
                    fig.add_trace(go.Scatter(
                        x=np.concatenate([q_fill, q_fill[::-1]]),
                        y=np.concatenate([atc_fill, np.full_like(q_fill, P_star)[::-1]]),
                        fill="toself", fillcolor="rgba(239,154,154,0.30)",
                        line=dict(width=0), name=f"Loss = {profit:.1f}"))

                fig.add_trace(go.Scatter(x=[Q_star], y=[P_star], mode="markers+text",
                    text=[f"  Q*={Q_star:.1f}, P*={P_star:.1f}"], textposition="top right",
                    marker=dict(size=12, color=COL["eq"], line=dict(width=2, color="black")),
                    name="Equilibrium"))

            y_max = max(a_firm * 1.1, 80)
            x_max = min(a_firm / b_firm * 1.2 if b_firm > 0 else 100, Q_max_global)
            fig.update_layout(title=f"Monopolistic Competition – Short Run (n={n_firms} firms)",
                              xaxis_title="Quantity (Q)", yaxis_title="Price / Cost",
                              yaxis=dict(range=[0, y_max]), xaxis=dict(range=[0, x_max]),
                              template="plotly_white", height=520)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Short-Run Equilibrium")
            st.metric("Q*", f"{Q_star:.2f}")
            st.metric("P*", f"{P_star:.2f}")
            st.metric("ATC at Q*", f"{ATC_star:.2f}")
            st.metric("Economic Profit", f"{profit:.2f}")
            st.markdown("---")
            st.markdown(f"""
            With **{n_firms} firms**, each firm's demand is
            more elastic than a monopolist's.  
            Supernormal profits attract entry → long run.
            """)

    else:  # Long Run
        # Long run: P = ATC at MR=MC point (tangency)
        # Numerically find n_eq where profit → 0
        # We iterate: given n, compute firm demand, find Q*, check profit
        best_n = 1
        best_profit_abs = 1e9
        for n_try in np.arange(1, 100, 0.1):
            b_f = b_demand * (1 + 0.3 * (n_try - 1))
            a_f = a_demand / (n_try ** 0.4)
            q_s = max((a_f - c_var) / (2 * b_f + 2 * d_var), 0)
            if q_s <= 0:
                break
            p_s = a_f - b_f * q_s
            tc_s = FC + c_var * q_s + d_var * q_s**2
            pi = p_s * q_s - tc_s
            if abs(pi) < best_profit_abs:
                best_profit_abs = abs(pi)
                best_n = n_try

        b_firm = b_demand * (1 + 0.3 * (best_n - 1))
        a_firm = a_demand / (best_n ** 0.4)
        Q_star = max((a_firm - c_var) / (2 * b_firm + 2 * d_var), 0)
        P_star = a_firm - b_firm * Q_star
        TC_star = FC + c_var * Q_star + d_var * Q_star**2
        ATC_star = TC_star / Q_star if Q_star > 0 else 0

        P_demand_lr = a_firm - b_firm * Q
        MR_curve_lr = a_firm - 2 * b_firm * Q

        col1, col2 = st.columns([2, 1])
        with col1:
            fig = go.Figure()
            mask = P_demand_lr >= 0
            fig.add_trace(go.Scatter(x=Q[mask], y=P_demand_lr[mask], name="Firm Demand (d)", line=dict(color=COL["demand"], width=2.5)))
            mask_mr = MR_curve_lr >= -10
            fig.add_trace(go.Scatter(x=Q[mask_mr], y=MR_curve_lr[mask_mr], name="MR", line=dict(color=COL["mr"], width=2.5)))
            fig.add_trace(go.Scatter(x=Q, y=MC, name="MC", line=dict(color=COL["mc"], width=2.5)))
            fig.add_trace(go.Scatter(x=Q, y=ATC, name="ATC", line=dict(color=COL["atc"], width=2, dash="dash")))

            if Q_star > 0:
                fig.add_trace(go.Scatter(x=[Q_star], y=[P_star], mode="markers+text",
                    text=[f"  Tangency: Q*={Q_star:.1f}, P*={P_star:.1f}"], textposition="top right",
                    marker=dict(size=14, color=COL["eq"], symbol="star",
                                line=dict(width=2, color="black")),
                    name="LR Equilibrium (P=ATC)"))
                fig.add_hline(y=P_star, line=dict(color="grey", width=1, dash="dot"))
                fig.add_vline(x=Q_star, line=dict(color="grey", width=1, dash="dot"))

                # Show min ATC for excess capacity
                Q_min_atc = np.sqrt(FC / d_var) if d_var > 0 else 0
                ATC_min = FC / Q_min_atc + c_var + d_var * Q_min_atc if Q_min_atc > 0 else 0
                if Q_min_atc > 0:
                    fig.add_trace(go.Scatter(x=[Q_min_atc], y=[ATC_min], mode="markers+text",
                        text=[f"  min ATC={ATC_min:.1f}"], textposition="bottom right",
                        marker=dict(size=10, color=COL["atc"], symbol="diamond"),
                        name="Min ATC (efficient scale)"))
                    fig.add_annotation(x=(Q_star + Q_min_atc)/2, y=ATC_min*0.92,
                        text="← excess capacity →", showarrow=False,
                        font=dict(size=11, color=COL["atc"]))

            y_max = max(a_firm * 1.1, 80)
            x_max = min(a_firm / b_firm * 1.2 if b_firm > 0 else 100, Q_max_global)
            fig.update_layout(title="Monopolistic Competition – Long-Run Equilibrium (Zero Profit Tangency)",
                              xaxis_title="Quantity (Q)", yaxis_title="Price / Cost",
                              yaxis=dict(range=[0, y_max]), xaxis=dict(range=[0, x_max]),
                              template="plotly_white", height=520)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Long-Run Equilibrium")
            st.metric("Equilibrium # firms", f"{best_n:.1f}")
            st.metric("Q* per firm", f"{Q_star:.2f}")
            st.metric("P* = ATC", f"{P_star:.2f}")
            st.metric("Economic Profit", "≈ 0 (normal profit)")
            if Q_min_atc > 0:
                excess = Q_min_atc - Q_star
                st.metric("Excess Capacity", f"{excess:.2f} units")
            st.markdown("---")
            st.markdown("""
            **Long-run tangency condition:**  
            Demand curve is tangent to ATC.  
            - P = ATC → zero economic profit  
            - P > MC → allocative inefficiency  
            - Q < Q_min_ATC → excess capacity
            """)

# ═══════════════════════════════════════════════════
#  DUOPOLY (COURNOT)
# ═══════════════════════════════════════════════════
elif market == "Duopoly (Cournot)":
    # Market demand: P = a - b(Q1+Q2)
    # Firm 1 profit: π1 = (a - b(Q1+Q2))Q1 - FC - c1·Q1 - d1·Q1²
    # FOC: a - 2bQ1 - bQ2 - c1 - 2d1·Q1 = 0
    # Q1 = (a - c1 - bQ2) / (2b + 2d1)
    # Similarly for firm 2
    # Solve system:
    # Q1 = (a - c_var) / (2b + 2d_var) - b/(2b + 2d_var) * Q2
    # Q2 = (a - c_var2) / (2b + 2d_var2) - b/(2b + 2d_var2) * Q1

    A1 = (a_demand - c_var) / (2 * b_demand + 2 * d_var)
    B1 = b_demand / (2 * b_demand + 2 * d_var)
    A2 = (a_demand - c_var2) / (2 * b_demand + 2 * d_var2)
    B2 = b_demand / (2 * b_demand + 2 * d_var2)

    # Q1 = A1 - B1*Q2,  Q2 = A2 - B2*Q1
    # Q1 = A1 - B1*(A2 - B2*Q1) = A1 - B1*A2 + B1*B2*Q1
    # Q1(1 - B1*B2) = A1 - B1*A2
    denom = 1 - B1 * B2
    if abs(denom) > 1e-10:
        Q1_star = (A1 - B1 * A2) / denom
        Q2_star = (A2 - B2 * A1) / denom
    else:
        Q1_star, Q2_star = 0, 0

    Q1_star = max(Q1_star, 0)
    Q2_star = max(Q2_star, 0)
    Q_total = Q1_star + Q2_star
    P_star = a_demand - b_demand * Q_total
    P_star = max(P_star, 0)

    pi1 = P_star * Q1_star - FC - c_var * Q1_star - d_var * Q1_star**2
    pi2 = P_star * Q2_star - FC - c_var2 * Q2_star - d_var2 * Q2_star**2

    # Monopoly benchmark
    Q_mono = max((a_demand - c_var) / (2 * b_demand + 2 * d_var), 0)
    P_mono = a_demand - b_demand * Q_mono

    # Perfect competition benchmark (P = MC for firm 1 costs)
    Q_comp = max((a_demand - c_var) / (b_demand + 2 * d_var), 0)
    P_comp = a_demand - b_demand * Q_comp

    col1, col2 = st.columns([2, 1])
    with col1:
        # Reaction functions plot
        q_range = np.linspace(0, max(A1, A2) * 1.5, 300)
        rf1 = np.maximum(A1 - B1 * q_range, 0)  # Q1 as function of Q2
        rf2 = np.maximum(A2 - B2 * q_range, 0)  # Q2 as function of Q1

        fig = make_subplots(rows=1, cols=2,
                            subplot_titles=["Reaction Functions (Best Response)",
                                            "Market Demand & Equilibrium"],
                            horizontal_spacing=0.12)

        # Left: Reaction functions
        fig.add_trace(go.Scatter(x=q_range, y=rf1, name="Firm 1 BR: Q₁(Q₂)",
                                  line=dict(color=COL["react1"], width=2.5)), row=1, col=1)
        fig.add_trace(go.Scatter(x=rf2, y=q_range, name="Firm 2 BR: Q₂(Q₁)",
                                  line=dict(color=COL["react2"], width=2.5)), row=1, col=1)
        fig.add_trace(go.Scatter(x=[Q2_star], y=[Q1_star], mode="markers+text",
            text=[f"  Nash Eq ({Q1_star:.1f}, {Q2_star:.1f})"],
            textposition="top right",
            marker=dict(size=14, color=COL["eq"], symbol="star",
                        line=dict(width=2, color="black")),
            name="Cournot-Nash Equilibrium"), row=1, col=1)

        # Iso-profit curves for firm 1
        for pi_target in [pi1 * 0.5, pi1, pi1 * 1.5]:
            q2_iso = []
            q1_iso = []
            for q1_t in np.linspace(0.5, A1 * 2, 200):
                # pi1 = (a - b(q1+q2))q1 - FC - c*q1 - d*q1^2 = target
                # (a - c - 2d*q1)*q1 - b*q1*q2 - FC = target
                # q2 = ((a-c-2d*q1)*q1 - FC - target) / (b*q1)
                if q1_t > 0:
                    num = (a_demand - c_var) * q1_t - b_demand * q1_t**2 - d_var * q1_t**2 - FC - pi_target
                    q2_v = num / (b_demand * q1_t)
                    if 0 <= q2_v <= A1 * 2:
                        q1_iso.append(q1_t)
                        q2_iso.append(q2_v)
            if q1_iso:
                fig.add_trace(go.Scatter(x=q2_iso, y=q1_iso,
                    line=dict(color=COL["react1"], width=1, dash="dot"),
                    showlegend=False, hoverinfo="skip"), row=1, col=1)

        fig.update_xaxes(title_text="Q₂", row=1, col=1)
        fig.update_yaxes(title_text="Q₁", row=1, col=1)

        # Right: Market demand with equilibrium
        Q_plot = np.linspace(0.1, a_demand / b_demand, 300)
        P_plot = a_demand - b_demand * Q_plot

        fig.add_trace(go.Scatter(x=Q_plot, y=P_plot, name="Market Demand",
                                  line=dict(color=COL["demand"], width=2.5)), row=1, col=2)
        fig.add_trace(go.Scatter(x=[Q_total], y=[P_star], mode="markers+text",
            text=[f"  Cournot: Q={Q_total:.1f}, P={P_star:.1f}"],
            textposition="top right",
            marker=dict(size=12, color=COL["eq"], line=dict(width=2, color="black")),
            name="Cournot Outcome"), row=1, col=2)
        fig.add_trace(go.Scatter(x=[Q_mono], y=[P_mono], mode="markers+text",
            text=[f"  Monopoly"], textposition="bottom left",
            marker=dict(size=10, color="purple", symbol="diamond"),
            name="Monopoly Benchmark"), row=1, col=2)
        if Q_comp <= a_demand / b_demand:
            fig.add_trace(go.Scatter(x=[Q_comp], y=[P_comp], mode="markers+text",
                text=[f"  Competitive"], textposition="bottom left",
                marker=dict(size=10, color="green", symbol="triangle-up"),
                name="Competitive Benchmark"), row=1, col=2)

        fig.update_xaxes(title_text="Total Q", row=1, col=2)
        fig.update_yaxes(title_text="Price", row=1, col=2)

        fig.update_layout(template="plotly_white", height=550,
                          title="Cournot Duopoly – Nash Equilibrium",
                          legend=dict(x=0.01, y=-0.15, orientation="h"))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Cournot Equilibrium")
        st.markdown("**Firm 1**")
        st.metric("Q₁*", f"{Q1_star:.2f}")
        st.metric("Profit π₁", f"{pi1:.2f}")
        st.markdown("**Firm 2**")
        st.metric("Q₂*", f"{Q2_star:.2f}")
        st.metric("Profit π₂", f"{pi2:.2f}")
        st.markdown("**Market**")
        st.metric("Total Output", f"{Q_total:.2f}")
        st.metric("Market Price", f"{P_star:.2f}")
        st.metric("Monopoly Price", f"{P_mono:.2f}")
        st.markdown("---")
        st.markdown(f"""
        **Cournot result** lies between
        monopoly (Q={Q_mono:.1f}) and
        competition (Q={Q_comp:.1f}).  
        Each firm's best-response:  
        Q₁ = {A1:.2f} − {B1:.3f}·Q₂
        """)

# ═══════════════════════════════════════════════════
#  COMPARATIVE STATICS  (all structures)
# ═══════════════════════════════════════════════════
st.markdown("---")
st.header("📊 Comparative Statics")
st.markdown("See how equilibrium responds to parameter changes.")

param_choice = st.selectbox("Vary which parameter?",
    ["Fixed Cost (FC)", "Variable Cost (c)", "Demand Intercept (a)", "Demand Slope (b)"])

range_map = {
    "Fixed Cost (FC)": np.linspace(0, 500, 60),
    "Variable Cost (c)": np.linspace(1, 50, 60),
    "Demand Intercept (a)": np.linspace(20, 200, 60),
    "Demand Slope (b)": np.linspace(0.1, 5, 60),
}
param_range = range_map[param_choice]

results = {"param": [], "Q_star": [], "P_star": [], "Profit": []}

for val in param_range:
    fc_i = val if "Fixed" in param_choice else FC
    c_i = val if "Variable" in param_choice else c_var
    a_i = val if "Intercept" in param_choice else (a_demand if a_demand else 100)
    b_i = val if "Slope" in param_choice else (b_demand if b_demand else 1.0)

    if market == "Perfect Competition":
        pm = P_market
        qs = max((pm - c_i) / (2 * d_var), 0)
        ps = pm
    elif market == "Monopoly":
        qs = max((a_i - c_i) / (2 * b_i + 2 * d_var), 0)
        ps = a_i - b_i * qs
    elif market == "Monopolistic Competition":
        n_f = n_firms if run_type == "Short Run" else best_n
        b_f = b_i * (1 + 0.3 * (n_f - 1))
        a_f = a_i / (n_f ** 0.4)
        qs = max((a_f - c_i) / (2 * b_f + 2 * d_var), 0)
        ps = a_f - b_f * qs
    elif market == "Duopoly (Cournot)":
        A1t = (a_i - c_i) / (2 * b_i + 2 * d_var)
        B1t = b_i / (2 * b_i + 2 * d_var)
        A2t = (a_i - c_var2) / (2 * b_i + 2 * d_var2)
        B2t = b_i / (2 * b_i + 2 * d_var2)
        den = 1 - B1t * B2t
        if abs(den) > 1e-10:
            q1t = max((A1t - B1t * A2t) / den, 0)
            q2t = max((A2t - B2t * A1t) / den, 0)
        else:
            q1t, q2t = 0, 0
        qs = q1t + q2t
        ps = max(a_i - b_i * qs, 0)

    tc_i = fc_i + c_i * qs + d_var * qs**2
    pi_i = ps * qs - tc_i

    results["param"].append(val)
    results["Q_star"].append(qs)
    results["P_star"].append(ps)
    results["Profit"].append(pi_i)

fig_cs = make_subplots(rows=1, cols=3,
    subplot_titles=["Quantity vs Parameter", "Price vs Parameter", "Profit vs Parameter"])
fig_cs.add_trace(go.Scatter(x=results["param"], y=results["Q_star"],
    line=dict(color=COL["demand"], width=2.5), name="Q*"), row=1, col=1)
fig_cs.add_trace(go.Scatter(x=results["param"], y=results["P_star"],
    line=dict(color=COL["mc"], width=2.5), name="P*"), row=1, col=2)
fig_cs.add_trace(go.Scatter(x=results["param"], y=results["Profit"],
    line=dict(color=COL["atc"], width=2.5), name="Profit"), row=1, col=3)
fig_cs.add_hline(y=0, line=dict(color="grey", dash="dash"), row=1, col=3)

short_label = param_choice.split("(")[1].rstrip(")")
for i in range(1, 4):
    fig_cs.update_xaxes(title_text=short_label, row=1, col=i)
fig_cs.update_yaxes(title_text="Q*", row=1, col=1)
fig_cs.update_yaxes(title_text="P*", row=1, col=2)
fig_cs.update_yaxes(title_text="π", row=1, col=3)

# Mark current value
current_val = {"Fixed Cost (FC)": FC, "Variable Cost (c)": c_var,
               "Demand Intercept (a)": a_demand if a_demand else 100,
               "Demand Slope (b)": b_demand if b_demand else 1.0}[param_choice]
for i in range(1, 4):
    fig_cs.add_vline(x=current_val, line=dict(color=COL["eq"], width=2, dash="dash"), row=1, col=i)

fig_cs.update_layout(template="plotly_white", height=380, showlegend=False,
                     title=f"Comparative Statics: {market}")
st.plotly_chart(fig_cs, use_container_width=True)

# ─── Footer ───
st.markdown("---")
with st.expander("📖 Model Assumptions & Equations"):
    st.markdown(r"""
    ### Cost Structure
    - **Total Cost**: $TC(Q) = FC + c \cdot Q + d \cdot Q^2$
    - **Marginal Cost**: $MC(Q) = c + 2d \cdot Q$ (upward-sloping)
    - **Average Total Cost**: $ATC(Q) = FC/Q + c + d \cdot Q$
    - **Average Variable Cost**: $AVC(Q) = c + d \cdot Q$

    ### Market Structures

    | Structure | Demand | Equilibrium Condition |
    |-----------|--------|----------------------|
    | Perfect Competition | $P$ = constant (price taker) | $P = MC$ |
    | Monopoly | $P = a - bQ$ | $MR = MC$ where $MR = a - 2bQ$ |
    | Monopolistic Competition | $P = a_f - b_f Q$ (firm-level) | $MR = MC$; LR: $P = ATC$ (tangency) |
    | Duopoly (Cournot) | $P = a - b(Q_1+Q_2)$ | Nash Eq: mutual best responses |

    ### Cournot Best Responses
    - Firm $i$: $Q_i^* = \frac{a - c_i}{2b + 2d_i} - \frac{b}{2b + 2d_i} Q_j$
    """)

st.caption("Built with Streamlit • Microeconomics Firm Equilibrium Simulator")
