import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ───────────────────────────────────────────────────
#  CONFIG
# ───────────────────────────────────────────────────
st.set_page_config(page_title="Firm Equilibrium Simulator V2", layout="wide", page_icon="📈")
st.title("📈 Firm Equilibrium Simulator V2")
st.markdown("Interactive model of firm equilibrium across four market structures with long-run toggle.")

COL = dict(
    demand="#2196F3", mr="#FF9800", mc="#E53935", atc="#4CAF50",
    avc="#8BC34A", eq="#FFD600", dwl="#FF9800", firm2="#9C27B0",
    react1="#2196F3", react2="#E53935",
    profit_fill="rgba(129,212,250,0.35)", profit_line="rgba(33,150,243,0.6)",
    loss_fill="rgba(239,154,154,0.35)", loss_line="rgba(229,57,53,0.6)",
)
Q_RANGE = np.linspace(0.1, 150, 800)


# ───────────────────────────────────────────────────
#  HELPER FUNCTIONS
# ───────────────────────────────────────────────────
def cost_curves(Q, fc, c, d):
    TC = fc + c * Q + d * Q ** 2
    MC = c + 2 * d * Q
    with np.errstate(divide="ignore", invalid="ignore"):
        ATC = np.where(Q > 0, TC / Q, np.nan)
        AVC = np.where(Q > 0, (c * Q + d * Q ** 2) / Q, np.nan)
    return TC, MC, ATC, AVC


def min_atc(fc, c, d):
    Q_eff = np.sqrt(fc / d) if fc > 0 and d > 0 else 1.0
    atc_min = fc / Q_eff + c + d * Q_eff
    return Q_eff, atc_min


def draw_profit_rect(fig, Q_star, P_star, ATC_star):
    profit = (P_star - ATC_star) * Q_star
    if Q_star <= 0:
        return profit
    xs = [0, Q_star, Q_star, 0, 0]
    if profit >= 0:
        ys = [P_star, P_star, ATC_star, ATC_star, P_star]
        fig.add_trace(go.Scatter(
            x=xs, y=ys, fill="toself",
            fillcolor=COL["profit_fill"],
            line=dict(width=1.5, color=COL["profit_line"]),
            name=f"Profit = {profit:.1f}",
        ))
    else:
        ys = [ATC_star, ATC_star, P_star, P_star, ATC_star]
        fig.add_trace(go.Scatter(
            x=xs, y=ys, fill="toself",
            fillcolor=COL["loss_fill"],
            line=dict(width=1.5, color=COL["loss_line"]),
            name=f"Loss = {profit:.1f}",
        ))
    return profit


def eq_marker(fig, x, y, label, row=None, col=None, symbol="circle"):
    kw = dict(
        x=[x], y=[y], mode="markers+text",
        text=[f"  {label}"], textposition="top right",
        marker=dict(size=12, color=COL["eq"], symbol=symbol,
                    line=dict(width=2, color="black")),
        name=label, showlegend=True,
    )
    if row is not None:
        fig.add_trace(go.Scatter(**kw), row=row, col=col)
    else:
        fig.add_trace(go.Scatter(**kw))


def guide_lines(fig, x, y):
    fig.add_hline(y=y, line=dict(color="grey", width=1, dash="dot"))
    fig.add_vline(x=x, line=dict(color="grey", width=1, dash="dot"))


# ───────────────────────────────────────────────────
#  SIDEBAR
# ───────────────────────────────────────────────────
st.sidebar.header("⚙️ Market Structure")
market = st.sidebar.selectbox(
    "Select structure",
    ["Perfect Competition", "Monopoly", "Monopolistic Competition", "Duopoly (Cournot)"],
)
lr = st.sidebar.toggle(
    "🔄 Long-Run Equilibrium", value=False,
    help="Snap to long-run equilibrium with properties matching this market structure",
)

st.sidebar.header("💰 Cost Parameters")
FC = st.sidebar.slider("Fixed Cost (FC)", 0, 500, 100, 10)
c1 = st.sidebar.slider("Variable cost coeff c", 1.0, 50.0, 10.0, 0.5, help="VC = c·Q + d·Q²")
d1 = st.sidebar.slider("Variable cost coeff d", 0.01, 2.0, 0.50, 0.01, help="VC = c·Q + d·Q²")

st.sidebar.header("🏪 Demand / Market")
if market == "Perfect Competition":
    P_input = st.sidebar.slider("Market Price (P)", 5.0, 100.0, 40.0, 0.5)
    a_dem = b_dem = None
else:
    a_dem = st.sidebar.slider("Demand intercept (a)", 20.0, 200.0, 100.0, 1.0, help="P = a − b·Q")
    b_dem = st.sidebar.slider("Demand slope (b)", 0.1, 5.0, 1.0, 0.05, help="P = a − b·Q")
    if market == "Monopolistic Competition":
        n_input = st.sidebar.slider("Number of firms (n)", 2, 20, 5)
    if market == "Duopoly (Cournot)":
        c2 = st.sidebar.slider("Firm 2 cost coeff c₂", 1.0, 50.0, 10.0, 0.5)
        d2 = st.sidebar.slider("Firm 2 cost coeff d₂", 0.01, 2.0, 0.50, 0.01)

# Precompute cost arrays for firm 1
TC_arr, MC_arr, ATC_arr, AVC_arr = cost_curves(Q_RANGE, FC, c1, d1)
Q_eff, ATC_min_val = min_atc(FC, c1, d1)


# ═══════════════════════════════════════════════════
#  PERFECT COMPETITION
# ═══════════════════════════════════════════════════
if market == "Perfect Competition":
    P_m = ATC_min_val if lr else P_input
    if lr:
        st.sidebar.info(f"🔄 LR: Price → min ATC = {ATC_min_val:.2f}")

    Q_star = max((P_m - c1) / (2 * d1), 0)
    shutdown = P_m < c1
    TC_star = FC + c1 * Q_star + d1 * Q_star ** 2
    ATC_star = TC_star / Q_star if Q_star > 0 else 0

    c1_col, c2_col = st.columns([2, 1])
    with c1_col:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=Q_RANGE, y=MC_arr, name="MC", line=dict(color=COL["mc"], width=2.5)))
        fig.add_trace(go.Scatter(x=Q_RANGE, y=ATC_arr, name="ATC", line=dict(color=COL["atc"], width=2, dash="dash")))
        fig.add_trace(go.Scatter(x=Q_RANGE, y=AVC_arr, name="AVC", line=dict(color=COL["avc"], width=2, dash="dot")))
        fig.add_hline(y=P_m, line=dict(color=COL["demand"], width=2),
                      annotation_text=f"P = MR = AR = {P_m:.1f}")

        if Q_star > 0 and not shutdown:
            profit = draw_profit_rect(fig, Q_star, P_m, ATC_star)
            eq_marker(fig, Q_star, P_m, f"Q*={Q_star:.1f}")
            if lr:
                eq_marker(fig, Q_eff, ATC_min_val, f"min ATC={ATC_min_val:.1f}", symbol="diamond")

        fig.update_layout(
            title="Perfect Competition" + (" — Long Run" if lr else ""),
            xaxis_title="Quantity (Q)", yaxis_title="Price / Cost",
            yaxis=dict(range=[0, max(P_m * 2.2, 80)]),
            xaxis=dict(range=[0, min(Q_star * 3 + 10, 150)]),
            template="plotly_white", height=520, legend=dict(x=0.60, y=0.98),
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2_col:
        st.subheader("Equilibrium")
        if shutdown:
            st.error("🛑 **Shutdown**: P < min AVC — firm does not produce.")
        else:
            profit = (P_m - ATC_star) * Q_star
            st.metric("Q*", f"{Q_star:.2f}")
            st.metric("Price", f"{P_m:.2f}")
            st.metric("ATC at Q*", f"{ATC_star:.2f}")
            st.metric("TR", f"{P_m * Q_star:.2f}")
            st.metric("TC", f"{TC_star:.2f}")
            st.metric("Profit (P−ATC)·Q", f"{profit:.2f}",
                      delta="Positive" if profit > 0.5 else ("≈ 0 ✓" if abs(profit) < 0.5 else "Loss"),
                      delta_color="normal" if profit >= -0.5 else "inverse")
        st.markdown("---")
        if lr:
            st.success("**LR properties**\n"
                       "- P = min ATC → π = 0\n"
                       "- P = MC → allocative efficiency\n"
                       "- Production at efficient scale\n"
                       "- Free entry / exit drives to this point")
        else:
            st.info("**Rules:** P = MC; Shutdown if P < min AVC\n\nToggle 🔄 for long-run zero-profit eq.")


# ═══════════════════════════════════════════════════
#  MONOPOLY
# ═══════════════════════════════════════════════════
elif market == "Monopoly":
    Q_star = max((a_dem - c1) / (2 * b_dem + 2 * d1), 0)
    P_star = a_dem - b_dem * Q_star
    TC_star = FC + c1 * Q_star + d1 * Q_star ** 2
    ATC_star = TC_star / Q_star if Q_star > 0 else 0
    MR_star = a_dem - 2 * b_dem * Q_star
    MC_star = c1 + 2 * d1 * Q_star
    profit = (P_star - ATC_star) * Q_star

    Q_comp = max((a_dem - c1) / (b_dem + 2 * d1), 0)
    P_comp = a_dem - b_dem * Q_comp
    Q_int = a_dem / b_dem

    P_dem = a_dem - b_dem * Q_RANGE
    MR_c = a_dem - 2 * b_dem * Q_RANGE

    if lr:
        st.sidebar.info("🔄 LR (Monopoly): MR = MC with barriers → supernormal profit persists")

    c1_col, c2_col = st.columns([2, 1])
    with c1_col:
        fig = go.Figure()
        m = P_dem >= 0
        fig.add_trace(go.Scatter(x=Q_RANGE[m], y=P_dem[m], name="Demand (AR)", line=dict(color=COL["demand"], width=2.5)))
        m2 = MR_c >= -20
        fig.add_trace(go.Scatter(x=Q_RANGE[m2], y=MR_c[m2], name="MR", line=dict(color=COL["mr"], width=2.5)))
        fig.add_trace(go.Scatter(x=Q_RANGE, y=MC_arr, name="MC", line=dict(color=COL["mc"], width=2.5)))
        fig.add_trace(go.Scatter(x=Q_RANGE, y=ATC_arr, name="ATC", line=dict(color=COL["atc"], width=2, dash="dash")))
        fig.add_trace(go.Scatter(x=Q_RANGE, y=AVC_arr, name="AVC", line=dict(color=COL["avc"], width=2, dash="dot")))

        if Q_star > 0:
            draw_profit_rect(fig, Q_star, P_star, ATC_star)

            # DWL triangle
            fig.add_trace(go.Scatter(
                x=[Q_star, Q_star, Q_comp, Q_star],
                y=[P_star, MR_star, P_comp, P_star],
                fill="toself", fillcolor="rgba(255,152,0,0.18)",
                line=dict(width=1, color=COL["dwl"], dash="dot"),
                name="Deadweight Loss",
            ))
            eq_marker(fig, Q_star, P_star, f"Q*={Q_star:.1f}, P*={P_star:.1f}")
            guide_lines(fig, Q_star, P_star)

        fig.update_layout(
            title="Monopoly — MR = MC" + (" (Long Run)" if lr else ""),
            xaxis_title="Quantity (Q)", yaxis_title="Price / Cost",
            yaxis=dict(range=[0, max(a_dem * 1.1, 80)]),
            xaxis=dict(range=[0, min(Q_int * 1.1, 150)]),
            template="plotly_white", height=520, legend=dict(x=0.60, y=0.98),
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2_col:
        st.subheader("Equilibrium")
        st.metric("Q*", f"{Q_star:.2f}")
        st.metric("P*", f"{P_star:.2f}")
        st.metric("MR = MC", f"{MC_star:.2f}")
        st.metric("ATC at Q*", f"{ATC_star:.2f}")
        st.metric("TR", f"{P_star * Q_star:.2f}")
        st.metric("TC", f"{TC_star:.2f}")
        st.metric("Profit (P−ATC)·Q", f"{profit:.2f}",
                  delta="Supernormal" if profit > 0.5 else ("Zero" if abs(profit) < 0.5 else "Loss"),
                  delta_color="normal" if profit >= -0.5 else "inverse")
        lerner = (P_star - MC_star) / P_star if P_star > 0 else 0
        st.metric("Lerner Index", f"{lerner:.3f}")
        st.markdown("---")
        if lr:
            st.success("**LR properties (Monopoly)**\n"
                       f"- MR = MC → profit max\n"
                       f"- Barriers → π = {profit:.1f} persists\n"
                       f"- P > MC → DWL (allocative inefficiency)\n"
                       f"- Lerner = {lerner:.3f}")
        else:
            st.info("**Rules:** MR = MC; Price from demand curve\n\nToggle 🔄 for LR view.")


# ═══════════════════════════════════════════════════
#  MONOPOLISTIC COMPETITION
# ═══════════════════════════════════════════════════
elif market == "Monopolistic Competition":
    if lr:
        # find n that zeroes profit
        best_n, best_err = 1.0, 1e15
        for nt in np.arange(1.0, 200, 0.05):
            bf = b_dem * (1 + 0.3 * (nt - 1))
            af = a_dem / (nt ** 0.4)
            qs = (af - c1) / (2 * bf + 2 * d1)
            if qs <= 0:
                break
            ps = af - bf * qs
            tc = FC + c1 * qs + d1 * qs ** 2
            err = abs(ps * qs - tc)
            if err < best_err:
                best_err = err
                best_n = nt
        n_f = best_n
        st.sidebar.info(f"🔄 LR: n ≈ {best_n:.1f} firms (zero profit)")
    else:
        n_f = n_input

    b_f = b_dem * (1 + 0.3 * (n_f - 1))
    a_f = a_dem / (n_f ** 0.4)

    Q_star = max((a_f - c1) / (2 * b_f + 2 * d1), 0)
    P_star = a_f - b_f * Q_star
    TC_star = FC + c1 * Q_star + d1 * Q_star ** 2
    ATC_star = TC_star / Q_star if Q_star > 0 else 0
    profit = (P_star - ATC_star) * Q_star

    P_dem_f = a_f - b_f * Q_RANGE
    MR_f = a_f - 2 * b_f * Q_RANGE

    c1_col, c2_col = st.columns([2, 1])
    with c1_col:
        fig = go.Figure()
        m = P_dem_f >= 0
        fig.add_trace(go.Scatter(x=Q_RANGE[m], y=P_dem_f[m], name="Firm Demand (d)", line=dict(color=COL["demand"], width=2.5)))
        m2 = MR_f >= -10
        fig.add_trace(go.Scatter(x=Q_RANGE[m2], y=MR_f[m2], name="MR", line=dict(color=COL["mr"], width=2.5)))
        fig.add_trace(go.Scatter(x=Q_RANGE, y=MC_arr, name="MC", line=dict(color=COL["mc"], width=2.5)))
        fig.add_trace(go.Scatter(x=Q_RANGE, y=ATC_arr, name="ATC", line=dict(color=COL["atc"], width=2, dash="dash")))

        if Q_star > 0:
            draw_profit_rect(fig, Q_star, P_star, ATC_star)
            sym = "star" if lr else "circle"
            eq_marker(fig, Q_star, P_star, f"Q*={Q_star:.1f}, P*={P_star:.1f}", symbol=sym)
            guide_lines(fig, Q_star, P_star)

            if lr:
                eq_marker(fig, Q_eff, ATC_min_val, f"min ATC={ATC_min_val:.1f}", symbol="diamond")
                if Q_star < Q_eff:
                    fig.add_annotation(
                        x=(Q_star + Q_eff) / 2, y=ATC_min_val * 0.88,
                        text="← excess capacity →", showarrow=False,
                        font=dict(size=11, color=COL["atc"]),
                    )

        y_hi = max(a_f * 1.1, 80)
        x_hi = min(a_f / b_f * 1.2 if b_f > 0 else 100, 150)
        fig.update_layout(
            title=f"Monopolistic Competition — {'LR Tangency' if lr else f'SR (n={n_f:.0f})'}",
            xaxis_title="Quantity (Q)", yaxis_title="Price / Cost",
            yaxis=dict(range=[0, y_hi]), xaxis=dict(range=[0, x_hi]),
            template="plotly_white", height=520, legend=dict(x=0.58, y=0.98),
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2_col:
        st.subheader("Equilibrium")
        st.metric("Firms (n)", f"{n_f:.1f}")
        st.metric("Q* per firm", f"{Q_star:.2f}")
        st.metric("P*", f"{P_star:.2f}")
        st.metric("ATC at Q*", f"{ATC_star:.2f}")
        st.metric("Profit (P−ATC)·Q", f"{profit:.2f}",
                  delta="Positive" if profit > 0.5 else ("≈ 0 ✓" if abs(profit) < 0.5 else "Loss"),
                  delta_color="normal" if profit >= -0.5 else "inverse")
        if Q_star < Q_eff:
            st.metric("Excess Capacity", f"{Q_eff - Q_star:.2f} units")
        st.markdown("---")
        if lr:
            st.success("**LR properties**\n"
                       "- MR = MC → profit max\n"
                       "- P = ATC (tangency) → π = 0\n"
                       "- P > MC → some DWL\n"
                       f"- Excess capacity = {max(Q_eff - Q_star, 0):.1f}\n"
                       f"- Entry adjusted n to {n_f:.1f}")
        else:
            st.info(f"**{n_f:.0f} firms**, each with downward-sloping demand.\n\nToggle 🔄 for zero-profit tangency.")


# ═══════════════════════════════════════════════════
#  DUOPOLY (COURNOT)
# ═══════════════════════════════════════════════════
elif market == "Duopoly (Cournot)":
    A1 = (a_dem - c1) / (2 * b_dem + 2 * d1)
    B1 = b_dem / (2 * b_dem + 2 * d1)
    A2 = (a_dem - c2) / (2 * b_dem + 2 * d2)
    B2 = b_dem / (2 * b_dem + 2 * d2)

    det = 1 - B1 * B2
    if abs(det) > 1e-10:
        Q1s = max((A1 - B1 * A2) / det, 0)
        Q2s = max((A2 - B2 * A1) / det, 0)
    else:
        Q1s = Q2s = 0

    Qt = Q1s + Q2s
    Ps = max(a_dem - b_dem * Qt, 0)
    TC1 = FC + c1 * Q1s + d1 * Q1s ** 2
    TC2 = FC + c2 * Q2s + d2 * Q2s ** 2
    ATC1 = TC1 / Q1s if Q1s > 0 else 0
    ATC2 = TC2 / Q2s if Q2s > 0 else 0
    pi1 = (Ps - ATC1) * Q1s
    pi2 = (Ps - ATC2) * Q2s

    Q_mono = max((a_dem - c1) / (2 * b_dem + 2 * d1), 0)
    P_mono = a_dem - b_dem * Q_mono
    Q_comp = max((a_dem - c1) / (b_dem + 2 * d1), 0)
    P_comp = max(a_dem - b_dem * Q_comp, 0)

    if lr:
        st.sidebar.info("🔄 LR (Cournot): Nash eq. with barriers → profit may persist")

    c1_col, c2_col = st.columns([2, 1])
    with c1_col:
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=["Reaction Functions", "Market & Profit"],
            horizontal_spacing=0.12,
        )
        qr = np.linspace(0, max(A1, A2) * 1.5, 300)
        rf1 = np.maximum(A1 - B1 * qr, 0)
        rf2 = np.maximum(A2 - B2 * qr, 0)

        fig.add_trace(go.Scatter(x=qr, y=rf1, name="Firm 1 BR: Q₁(Q₂)",
                                  line=dict(color=COL["react1"], width=2.5)), row=1, col=1)
        fig.add_trace(go.Scatter(x=rf2, y=qr, name="Firm 2 BR: Q₂(Q₁)",
                                  line=dict(color=COL["react2"], width=2.5)), row=1, col=1)
        eq_marker(fig, Q2s, Q1s, f"Nash ({Q1s:.1f},{Q2s:.1f})", row=1, col=1, symbol="star")

        # Iso-profit contours for firm 1
        for mult in [0.5, 1.0, 1.5]:
            pi_t = pi1 * mult if pi1 != 0 else mult * 10
            q2_iso, q1_iso = [], []
            for q1t in np.linspace(0.5, A1 * 2, 200):
                num = (a_dem - c1) * q1t - b_dem * q1t ** 2 - d1 * q1t ** 2 - FC - pi_t
                denom_v = b_dem * q1t
                if denom_v != 0:
                    q2v = num / denom_v
                    if 0 <= q2v <= max(A1, A2) * 1.5:
                        q1_iso.append(q1t)
                        q2_iso.append(q2v)
            if q1_iso:
                fig.add_trace(go.Scatter(
                    x=q2_iso, y=q1_iso,
                    line=dict(color=COL["react1"], width=1, dash="dot"),
                    showlegend=False, hoverinfo="skip",
                ), row=1, col=1)

        fig.update_xaxes(title_text="Q₂", row=1, col=1)
        fig.update_yaxes(title_text="Q₁", row=1, col=1)

        # Right panel — demand + profit rectangles
        Qp = np.linspace(0.1, a_dem / b_dem, 300)
        Pp = a_dem - b_dem * Qp
        fig.add_trace(go.Scatter(x=Qp, y=Pp, name="Market Demand",
                                  line=dict(color=COL["demand"], width=2.5)), row=1, col=2)

        # Firm 1 profit rectangle
        if Q1s > 0:
            top1, bot1 = (Ps, ATC1) if pi1 >= 0 else (ATC1, Ps)
            fig.add_trace(go.Scatter(
                x=[0, Q1s, Q1s, 0, 0], y=[top1, top1, bot1, bot1, top1],
                fill="toself", fillcolor="rgba(33,150,243,0.18)",
                line=dict(width=1, color="rgba(33,150,243,0.5)"),
                name=f"Firm 1 π={pi1:.1f}",
            ), row=1, col=2)

        # Firm 2 profit rectangle (offset)
        if Q2s > 0:
            top2, bot2 = (Ps, ATC2) if pi2 >= 0 else (ATC2, Ps)
            fig.add_trace(go.Scatter(
                x=[Q1s, Qt, Qt, Q1s, Q1s], y=[top2, top2, bot2, bot2, top2],
                fill="toself", fillcolor="rgba(156,39,176,0.18)",
                line=dict(width=1, color="rgba(156,39,176,0.5)"),
                name=f"Firm 2 π={pi2:.1f}",
            ), row=1, col=2)

        eq_marker(fig, Qt, Ps, f"Cournot Q={Qt:.1f}", row=1, col=2)
        fig.add_trace(go.Scatter(x=[Q_mono], y=[P_mono], mode="markers+text",
            text=["  Monopoly"], textposition="bottom left",
            marker=dict(size=9, color="purple", symbol="diamond"),
            name="Monopoly"), row=1, col=2)
        if Q_comp <= a_dem / b_dem:
            fig.add_trace(go.Scatter(x=[Q_comp], y=[P_comp], mode="markers+text",
                text=["  Competitive"], textposition="bottom left",
                marker=dict(size=9, color="green", symbol="triangle-up"),
                name="Competitive"), row=1, col=2)

        fig.update_xaxes(title_text="Total Q", row=1, col=2)
        fig.update_yaxes(title_text="Price", row=1, col=2)
        fig.update_layout(
            template="plotly_white", height=560,
            title="Cournot Duopoly — Nash Equilibrium" + (" (Long Run)" if lr else ""),
            legend=dict(x=0.01, y=-0.18, orientation="h"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2_col:
        st.subheader("Cournot Equilibrium")
        st.markdown("**Firm 1**")
        st.metric("Q₁*", f"{Q1s:.2f}")
        st.metric("ATC₁", f"{ATC1:.2f}")
        st.metric("π₁ = (P−ATC₁)·Q₁", f"{pi1:.2f}")
        st.markdown("**Firm 2**")
        st.metric("Q₂*", f"{Q2s:.2f}")
        st.metric("ATC₂", f"{ATC2:.2f}")
        st.metric("π₂ = (P−ATC₂)·Q₂", f"{pi2:.2f}")
        st.markdown("**Market**")
        st.metric("Total Q", f"{Qt:.2f}")
        st.metric("Price", f"{Ps:.2f}")
        st.markdown("---")
        if lr:
            st.success("**LR properties (Cournot)**\n"
                       "- Nash eq.: no unilateral deviation\n"
                       f"- Q_mono={Q_mono:.1f} < Q_cournot={Qt:.1f} < Q_comp={Q_comp:.1f}\n"
                       "- Barriers → profits can persist\n"
                       f"- BR₁: Q₁ = {A1:.2f} − {B1:.3f}·Q₂")
        else:
            st.info(f"Cournot output between monopoly ({Q_mono:.1f}) and competition ({Q_comp:.1f}).\n\nToggle 🔄 for LR details.")


# ═══════════════════════════════════════════════════
#  COMPARATIVE STATICS
# ═══════════════════════════════════════════════════
st.markdown("---")
st.header("📊 Comparative Statics")

param = st.selectbox("Vary parameter:", ["Fixed Cost (FC)", "Variable Cost (c)", "Demand Intercept (a)", "Demand Slope (b)"])
rng = {
    "Fixed Cost (FC)": np.linspace(0, 500, 60),
    "Variable Cost (c)": np.linspace(1, 50, 60),
    "Demand Intercept (a)": np.linspace(20, 200, 60),
    "Demand Slope (b)": np.linspace(0.1, 5, 60),
}[param]

Qs, Ps_arr, Pis = [], [], []
for v in rng:
    fc_v = v if "Fixed" in param else FC
    c_v = v if "Variable" in param else c1
    a_v = v if "Intercept" in param else (a_dem if a_dem else 100)
    b_v = v if "Slope" in param else (b_dem if b_dem else 1.0)

    if market == "Perfect Competition":
        pm = ATC_min_val if lr else P_input
        qs = max((pm - c_v) / (2 * d1), 0)
        ps = pm
    elif market == "Monopoly":
        qs = max((a_v - c_v) / (2 * b_v + 2 * d1), 0)
        ps = a_v - b_v * qs
    elif market == "Monopolistic Competition":
        bf = b_v * (1 + 0.3 * (n_f - 1))
        af = a_v / (n_f ** 0.4)
        qs = max((af - c_v) / (2 * bf + 2 * d1), 0)
        ps = af - bf * qs
    else:
        _A1 = (a_v - c_v) / (2 * b_v + 2 * d1)
        _B1 = b_v / (2 * b_v + 2 * d1)
        _A2 = (a_v - c2) / (2 * b_v + 2 * d2)
        _B2 = b_v / (2 * b_v + 2 * d2)
        _det = 1 - _B1 * _B2
        if abs(_det) > 1e-10:
            _q1 = max((_A1 - _B1 * _A2) / _det, 0)
            _q2 = max((_A2 - _B2 * _A1) / _det, 0)
        else:
            _q1 = _q2 = 0
        qs = _q1 + _q2
        ps = max(a_v - b_v * qs, 0)

    tc_v = fc_v + c_v * qs + d1 * qs ** 2
    atc_v = tc_v / qs if qs > 0 else 0
    Qs.append(qs)
    Ps_arr.append(ps)
    Pis.append((ps - atc_v) * qs)

fig_cs = make_subplots(rows=1, cols=3, subplot_titles=["Quantity", "Price", "Profit"])
fig_cs.add_trace(go.Scatter(x=rng, y=Qs, line=dict(color=COL["demand"], width=2.5), name="Q*"), row=1, col=1)
fig_cs.add_trace(go.Scatter(x=rng, y=Ps_arr, line=dict(color=COL["mc"], width=2.5), name="P*"), row=1, col=2)
fig_cs.add_trace(go.Scatter(x=rng, y=Pis, line=dict(color=COL["atc"], width=2.5), name="π"), row=1, col=3)
fig_cs.add_hline(y=0, line=dict(color="grey", dash="dash"), row=1, col=3)

xlabel = param.split("(")[1].rstrip(")")
cur = {"Fixed Cost (FC)": FC, "Variable Cost (c)": c1,
       "Demand Intercept (a)": a_dem if a_dem else 100,
       "Demand Slope (b)": b_dem if b_dem else 1.0}[param]
for i in range(1, 4):
    fig_cs.update_xaxes(title_text=xlabel, row=1, col=i)
    fig_cs.add_vline(x=cur, line=dict(color=COL["eq"], width=2, dash="dash"), row=1, col=i)
fig_cs.update_yaxes(title_text="Q*", row=1, col=1)
fig_cs.update_yaxes(title_text="P*", row=1, col=2)
fig_cs.update_yaxes(title_text="π", row=1, col=3)
fig_cs.update_layout(template="plotly_white", height=370, showlegend=False,
                     title=f"Comparative Statics — {market}")
st.plotly_chart(fig_cs, use_container_width=True)

# ───────────────────────────────────────────────────
#  REFERENCE
# ───────────────────────────────────────────────────
st.markdown("---")
with st.expander("📖 Model Equations"):
    st.markdown(r"""
| Symbol | Formula |
|--------|---------|
| Total Cost | $TC = FC + c \cdot Q + d \cdot Q^2$ |
| Marginal Cost | $MC = c + 2d \cdot Q$ |
| ATC | $ATC = FC/Q + c + d \cdot Q$ |
| AVC | $AVC = c + d \cdot Q$ |
| Min ATC at | $Q_{eff} = \sqrt{FC / d}$ |
| Profit | $\pi = (P - ATC) \times Q$ |

| Structure | Equilibrium | Long Run |
|-----------|-------------|----------|
| Perfect Competition | $P = MC$ | $P = \min ATC \Rightarrow \pi = 0$ |
| Monopoly | $MR = MC$ | Barriers $\Rightarrow \pi > 0$ |
| Monopolistic Comp. | $MR = MC$ | Tangency $P = ATC \Rightarrow \pi = 0$ |
| Cournot Duopoly | Nash: $Q_i^* = \frac{a-c_i}{2b+2d_i} - \frac{b}{2b+2d_i}Q_j$ | Barriers $\Rightarrow \pi \geq 0$ |
    """)

st.caption("Firm Equilibrium Simulator V2 • Built with Streamlit & Plotly")
