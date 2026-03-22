
import math
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Simulátor cyklické a strukturální složky salda", layout="wide")


def fmt_money(x):
    return f"{x:,.1f} mld. Kč".replace(",", " ")


def fmt_pct(x):
    return f"{x:.2f} %"


def solve_macro(target, actual, potential, gap_pct):
    gap = gap_pct / 100
    error = None
    if target == "Mezera produktu":
        if potential <= 0:
            error = "Potenciální HDP musí být kladné."
        else:
            gap = actual / potential - 1
            gap_pct = gap * 100
    elif target == "Skutečné HDP":
        if potential <= 0:
            error = "Potenciální HDP musí být kladné."
        elif gap <= -0.999:
            error = "Mezera produktu musí být vyšší než -99,9 %."
        else:
            actual = potential * (1 + gap)
    elif target == "Potenciální HDP":
        if actual <= 0:
            error = "Skutečné HDP musí být kladné."
        elif gap <= -0.999:
            error = "Mezera produktu musí být vyšší než -99,9 %."
        else:
            potential = actual / (1 + gap)
    return actual, potential, gap, gap_pct, error


def compute_budget(actual, potential, tau, eta, anchor_mode, anchor_value):
    ratio = actual / potential if potential > 0 else np.nan
    r_struct = tau * potential
    r_actual = r_struct * (ratio ** eta)
    cyclical = r_actual - r_struct

    if anchor_mode == "Výdaje":
        expenditure = anchor_value
        structural = r_struct - expenditure
        total = r_actual - expenditure
    elif anchor_mode == "Strukturální saldo":
        structural = anchor_value
        expenditure = r_struct - structural
        total = r_actual - expenditure
    else:
        total = anchor_value
        expenditure = r_actual - total
        structural = r_struct - expenditure

    return {
        "ratio": ratio,
        "r_struct": r_struct,
        "r_actual": r_actual,
        "cyclical": cyclical,
        "expenditure": expenditure,
        "structural": structural,
        "total": total,
    }


def classify_gap(gap):
    if gap < -0.5:
        return "Ekonomika je pod potenciálem. Příjmy jsou proti strukturální úrovni stlačené dolů a cyklická složka salda je záporná."
    if gap > 0.5:
        return "Ekonomika je nad potenciálem. Příjmy jsou dočasně nafouknuté a cyklická složka salda je kladná."
    return "Ekonomika je poblíž potenciálu. Cyklická složka je malá a celkové saldo je blízko strukturálnímu saldu."


def small_change_effect(potential, tau, eta, gap):
    return tau * eta * potential * ((1 + gap) ** max(eta - 1, 0)) * 0.01


with st.sidebar:
    st.header("Nastavení modelu")
    preset = st.selectbox("Scénář", ["Vlastní", "Recese", "Neutrální ekonomika", "Přehřátí"])

    preset_gap = {"Vlastní": 0.0, "Recese": -3.0, "Neutrální ekonomika": 0.0, "Přehřátí": 3.0}[preset]
    preset_tau = {"Vlastní": 0.20, "Recese": 0.20, "Neutrální ekonomika": 0.20, "Přehřátí": 0.20}[preset]

    st.subheader("Makro blok")
    macro_target = st.radio(
        "Dopočítávaná proměnná",
        ["Mezera produktu", "Skutečné HDP", "Potenciální HDP"],
        index=0,
    )
    actual_input = st.number_input("Skutečné HDP", min_value=100.0, value=8000.0, step=50.0)
    potential_input = st.number_input("Potenciální HDP", min_value=100.0, value=8000.0, step=50.0)
    gap_input = st.slider("Mezera produktu (%)", min_value=-10.0, max_value=10.0, value=float(preset_gap), step=0.1)

    st.subheader("Rozpočtový blok")
    tau = st.slider("Příjmová kvóta při potenciálu", min_value=0.05, max_value=0.40, value=float(preset_tau), step=0.005)
    eta = st.slider("Elasticita příjmů vůči HDP", min_value=0.50, max_value=2.00, value=1.00, step=0.05)
    anchor_mode = st.radio("Co držet fixní", ["Výdaje", "Strukturální saldo", "Celkové saldo"], index=0)

    default_anchor = {"Výdaje": 1650.0, "Strukturální saldo": -50.0, "Celkové saldo": -50.0}[anchor_mode]
    anchor_value = st.number_input(f"Hodnota: {anchor_mode}", value=default_anchor, step=10.0)

    st.caption("Předpoklad modelu: příjmy reagují na HDP, výdaje jsou v krátkém období necitlivé na cyklus.")

actual, potential, gap, gap_pct, macro_error = solve_macro(macro_target, actual_input, potential_input, gap_input)

st.title("Simulátor cyklické a strukturální složky salda státního rozpočtu")
st.write("Aplikace odděluje celkové saldo na strukturální a cyklickou část a současně ukazuje, jak se změna HDP promítne do příjmů a salda.")

with st.expander("Jak model funguje"):
    st.markdown(
        """
- Platí identita: **celkové saldo = strukturální saldo + cyklická složka**.
- Strukturální příjmy se počítají z potenciálního HDP.
- Skutečné příjmy se počítají ze skutečného HDP a zvolené elasticity.
- Výdaje jsou v základní verzi modelu na cyklu nezávislé.
- Když je ekonomika pod potenciálem, cyklická složka bývá záporná; nad potenciálem kladná.
        """
    )

if macro_error:
    st.error(macro_error)
    st.stop()

budget = compute_budget(actual, potential, tau, eta, anchor_mode, anchor_value)

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Skutečné HDP", fmt_money(actual))
c2.metric("Potenciální HDP", fmt_money(potential))
c3.metric("Mezera produktu", fmt_pct(gap_pct))
c4.metric("Strukturální saldo", fmt_money(budget["structural"]))
c5.metric("Cyklická složka", fmt_money(budget["cyclical"]))
c6.metric("Celkové saldo", fmt_money(budget["total"]))

left, right = st.columns([1.15, 1])

with left:
    st.subheader("Interpretace")
    st.info(classify_gap(gap_pct))

    rows = [
        ["Strukturální příjmy", fmt_money(budget["r_struct"]), fmt_pct(100 * budget["r_struct"] / potential)],
        ["Skutečné příjmy", fmt_money(budget["r_actual"]), fmt_pct(100 * budget["r_actual"] / actual)],
        ["Výdaje", fmt_money(budget["expenditure"]), fmt_pct(100 * budget["expenditure"] / actual)],
        ["Strukturální saldo", fmt_money(budget["structural"]), fmt_pct(100 * budget["structural"] / potential)],
        ["Cyklická složka", fmt_money(budget["cyclical"]), fmt_pct(100 * budget["cyclical"] / potential)],
        ["Celkové saldo", fmt_money(budget["total"]), fmt_pct(100 * budget["total"] / actual)],
    ]
    df = pd.DataFrame(rows, columns=["Ukazatel", "Hodnota", "% HDP"])
    st.dataframe(df, use_container_width=True, hide_index=True)

    approx = tau * eta * potential * gap
    diff = budget["cyclical"] - approx
    st.markdown("### Přesný vs. přibližný výpočet")
    st.write(
        f"Přesná cyklická složka: {fmt_money(budget['cyclical'])}. Lineární aproximace pro malé mezery produktu: {fmt_money(approx)}. Rozdíl: {fmt_money(diff)}."
    )

with right:
    st.subheader("Rozklad salda")
    fig_bar = go.Figure()
    fig_bar.add_bar(name="Strukturální saldo", x=["Saldo"], y=[budget["structural"]], marker_color="#1f77b4")
    fig_bar.add_bar(name="Cyklická složka", x=["Saldo"], y=[budget["cyclical"]], marker_color="#ff7f0e")
    fig_bar.add_bar(name="Celkové saldo", x=["Saldo"], y=[budget["total"]], marker_color="#2ca02c")
    fig_bar.update_layout(barmode="group", height=380, margin=dict(l=10, r=10, t=20, b=10), yaxis_title="mld. Kč")
    st.plotly_chart(fig_bar, use_container_width=True)

    one_pp = small_change_effect(potential, tau, eta, gap)
    st.markdown("### Co udělá 1 p. b. mezery produktu")
    st.write(
        f"Při aktuálním nastavení změní posun mezery produktu o 1 procentní bod cyklickou složku přibližně o {fmt_money(one_pp)}."
    )
    st.write(
        "To je dobrý most mezi intuicí a výpočtem: když jsou výdaje fixní, změna salda jde přes příjmy."
    )

st.subheader("Citlivost na mezeru produktu")
gaps = np.linspace(-8, 8, 161)
records = []
for g in gaps:
    y = potential * (1 + g / 100)
    vals = compute_budget(y, potential, tau, eta, anchor_mode, anchor_value)
    records.append(
        {
            "gap": g,
            "total": vals["total"],
            "structural": vals["structural"],
            "cyclical": vals["cyclical"],
        }
    )
line_df = pd.DataFrame(records)
fig_line = go.Figure()
fig_line.add_trace(go.Scatter(x=line_df["gap"], y=line_df["total"], mode="lines", name="Celkové saldo", line=dict(color="#2ca02c", width=3)))
fig_line.add_trace(go.Scatter(x=line_df["gap"], y=line_df["structural"], mode="lines", name="Strukturální saldo", line=dict(color="#1f77b4", width=3, dash="dash")))
fig_line.add_trace(go.Scatter(x=line_df["gap"], y=line_df["cyclical"], mode="lines", name="Cyklická složka", line=dict(color="#ff7f0e", width=3)))
fig_line.add_vline(x=gap_pct, line_width=1.5, line_dash="dot")
fig_line.update_layout(height=420, margin=dict(l=10, r=10, t=20, b=10), xaxis_title="Mezera produktu (%)", yaxis_title="mld. Kč")
st.plotly_chart(fig_line, use_container_width=True)

st.subheader("Procvičovací kalkulačka identity")
st.write("Tato část je schválně algebraická: studenti si mohou procvičit samotnou identitu bez ostatních předpokladů modelu.")
sandbox_target = st.radio("Dopočítat", ["Celkové saldo", "Strukturální saldo", "Cyklická složka"], horizontal=True)
sc1, sc2, sc3 = st.columns(3)
with sc1:
    sandbox_total = st.number_input("Celkové saldo (B)", value=float(budget["total"]), step=10.0, disabled=sandbox_target == "Celkové saldo", key="sb_total")
with sc2:
    sandbox_struct = st.number_input("Strukturální saldo (SB)", value=float(budget["structural"]), step=10.0, disabled=sandbox_target == "Strukturální saldo", key="sb_struct")
with sc3:
    sandbox_cyc = st.number_input("Cyklická složka (C)", value=float(budget["cyclical"]), step=10.0, disabled=sandbox_target == "Cyklická složka", key="sb_cyc")

if sandbox_target == "Celkové saldo":
    sandbox_total = sandbox_struct + sandbox_cyc
elif sandbox_target == "Strukturální saldo":
    sandbox_struct = sandbox_total - sandbox_cyc
else:
    sandbox_cyc = sandbox_total - sandbox_struct

r1, r2, r3 = st.columns(3)
r1.metric("B", fmt_money(sandbox_total))
r2.metric("SB", fmt_money(sandbox_struct))
r3.metric("C", fmt_money(sandbox_cyc))

st.subheader("Náměty do výuky")
st.markdown(
    """
1. Nechte studenty držet výdaje fixní a měnit jen mezeru produktu. Uvidí, že celkové saldo se mění přes příjmy.
2. Potom přepněte ukotvení na strukturální saldo. Studenti uvidí, jaká úroveň výdajů je s ním konzistentní.
3. Nakonec zvyšte elasticitu příjmů nad 1. Tím ukážete, že stejné makro kolísání může vytvářet silnější cyklickou složku.
4. Porovnávejte přesný výpočet s lineární aproximací. To dobře vysvětluje, proč se v učebnicích často pracuje se zjednodušením.
    """
)

# Dynamický copyright v patičce
import datetime
current_year = datetime.datetime.now().year
st.markdown(f"<hr style='margin-top:2em;margin-bottom:0.5em;'>", unsafe_allow_html=True)
st.markdown(f"<div style='text-align:center; color:gray; font-size:0.95em;'>© {current_year} Tomáš Paleta, Masarykova univerzita, Ekonomicko-správní fakulta, Brno</div>", unsafe_allow_html=True)
