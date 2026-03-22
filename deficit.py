
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Simulátor cyklické a strukturální složky salda", layout="wide")

PRESETS = {
    "Vlastní": {
        "base_actual": 8000.0,
        "base_potential": 8000.0,
        "base_gap_pct": 0.0,
        "base_tau": 0.20,
        "base_eta": 1.00,
        "anchor_mode": "Výdaje",
        "anchor_value": 1650.0,
        "description": "Ruční nastavení bez předvyplněného scénáře.",
    },
    "Recese": {
        "base_actual": 7760.0,
        "base_potential": 8000.0,
        "base_gap_pct": -3.0,
        "base_tau": 0.20,
        "base_eta": 1.05,
        "anchor_mode": "Výdaje",
        "anchor_value": 1650.0,
        "description": "Ekonomika je pod potenciálem, příjmy zaostávají a cyklická složka je záporná.",
    },
    "Neutrální ekonomika": {
        "base_actual": 8000.0,
        "base_potential": 8000.0,
        "base_gap_pct": 0.0,
        "base_tau": 0.20,
        "base_eta": 1.00,
        "anchor_mode": "Výdaje",
        "anchor_value": 1650.0,
        "description": "Skutečný výkon odpovídá potenciálu, cyklická složka je blízko nule.",
    },
    "Přehřátí": {
        "base_actual": 8240.0,
        "base_potential": 8000.0,
        "base_gap_pct": 3.0,
        "base_tau": 0.20,
        "base_eta": 1.10,
        "anchor_mode": "Výdaje",
        "anchor_value": 1650.0,
        "description": "Ekonomika běží nad potenciálem, příjmy jsou dočasně vyšší a saldo vypadá lépe.",
    },
}

EVENTS = {
    "Negativní poptávkový šok": {"type": "Cyklická složka", "gap_delta": -2.5, "potential_pct_delta": 0.0, "tau_delta": 0.0, "eta_delta": 0.0, "structural_spending_delta": 0.0, "cyclical_spending_delta": 0.0, "explanation": "Poptávka oslabí, výstup klesne pod potenciál a zhorší se cyklická složka salda."},
    "Přehřátí ekonomiky": {"type": "Cyklická složka", "gap_delta": 2.5, "potential_pct_delta": 0.0, "tau_delta": 0.0, "eta_delta": 0.0, "structural_spending_delta": 0.0, "cyclical_spending_delta": 0.0, "explanation": "Silná poptávka zvedne výstup nad potenciál a zlepší cyklickou složku salda."},
    "Růst nezaměstnanosti": {"type": "Cyklická složka", "gap_delta": -1.5, "potential_pct_delta": 0.0, "tau_delta": 0.0, "eta_delta": 0.0, "structural_spending_delta": 0.0, "cyclical_spending_delta": 25.0, "explanation": "Vedle nižších příjmů rostou i dočasné výdaje na dávky."},
    "Energetický cenový šok": {"type": "Smíšený dopad", "gap_delta": -1.8, "potential_pct_delta": -0.7, "tau_delta": 0.0, "eta_delta": 0.0, "structural_spending_delta": 0.0, "cyclical_spending_delta": 15.0, "explanation": "Část dopadu je cyklická přes slabší ekonomiku, část strukturální přes nižší potenciál."},
    "Dočasná kompenzace domácnostem": {"type": "Cyklická složka", "gap_delta": 0.0, "potential_pct_delta": 0.0, "tau_delta": 0.0, "eta_delta": 0.0, "structural_spending_delta": 0.0, "cyclical_spending_delta": 35.0, "explanation": "Jednorázové transfery zhorší hlavně dočasnou složku salda."},
    "Trvalé zvýšení důchodů": {"type": "Strukturální složka", "gap_delta": 0.0, "potential_pct_delta": 0.0, "tau_delta": 0.0, "eta_delta": 0.0, "structural_spending_delta": 40.0, "cyclical_spending_delta": 0.0, "explanation": "Trvale zvyšuje výdajovou základnu, tedy zhoršuje strukturální saldo."},
    "Vyšší obranné výdaje": {"type": "Strukturální složka", "gap_delta": 0.0, "potential_pct_delta": 0.0, "tau_delta": 0.0, "eta_delta": 0.0, "structural_spending_delta": 60.0, "cyclical_spending_delta": 0.0, "explanation": "Trvalé výdaje se promítají hlavně do strukturální složky."},
    "Snížení DPH": {"type": "Strukturální složka", "gap_delta": 0.0, "potential_pct_delta": 0.0, "tau_delta": -0.010, "eta_delta": 0.0, "structural_spending_delta": 0.0, "cyclical_spending_delta": 0.0, "explanation": "Nižší sazby snižují příjmovou kvótu i při stejném HDP."},
    "Lepší výběr daní": {"type": "Strukturální složka", "gap_delta": 0.0, "potential_pct_delta": 0.0, "tau_delta": 0.008, "eta_delta": 0.0, "structural_spending_delta": 0.0, "cyclical_spending_delta": 0.0, "explanation": "Vyšší efektivita výběru daní zvyšuje strukturální příjmy."},
    "Daňová progrese": {"type": "Strukturální složka", "gap_delta": 0.0, "potential_pct_delta": 0.0, "tau_delta": 0.0, "eta_delta": 0.15, "structural_spending_delta": 0.0, "cyclical_spending_delta": 0.0, "explanation": "Mění citlivost příjmů na hospodářský cyklus."},
    "Reforma trhu práce a produktivity": {"type": "Strukturální složka", "gap_delta": -0.5, "potential_pct_delta": 2.0, "tau_delta": 0.0, "eta_delta": 0.0, "structural_spending_delta": 0.0, "cyclical_spending_delta": 0.0, "explanation": "Posouvá potenciální produkt a tím i strukturální základnu ekonomiky."},
    "Konsolidační balíček": {"type": "Strukturální složka", "gap_delta": -0.4, "potential_pct_delta": 0.0, "tau_delta": 0.006, "eta_delta": 0.0, "structural_spending_delta": -30.0, "cyclical_spending_delta": 0.0, "explanation": "Vyšší příjmy a nižší trvalé výdaje zlepšují strukturální saldo."},
}


def fmt_money(x):
    return f"{x:,.1f} mld. Kč".replace(",", " ")


def fmt_pct(x):
    return f"{x:.2f} %"


def init_state():
    preset = PRESETS["Vlastní"]
    defaults = {
        "preset_name": "Vlastní",
        "macro_target": "Mezera produktu",
        "selected_events": [],
    }
    defaults.update(preset)
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def apply_preset():
    preset = PRESETS[st.session_state.preset_name]
    for k, v in preset.items():
        st.session_state[k] = v
    st.session_state.selected_events = []


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


def aggregate_events(selected):
    total = {
        "gap_delta": 0.0,
        "potential_pct_delta": 0.0,
        "tau_delta": 0.0,
        "eta_delta": 0.0,
        "structural_spending_delta": 0.0,
        "cyclical_spending_delta": 0.0,
        "notes": [],
        "types": [],
    }
    for name in selected:
        e = EVENTS[name]
        for key in ["gap_delta", "potential_pct_delta", "tau_delta", "eta_delta", "structural_spending_delta", "cyclical_spending_delta"]:
            total[key] += e[key]
        total["notes"].append((name, e["type"], e["explanation"]))
        total["types"].append(e["type"])
    return total


def apply_events(base_actual, base_potential, base_gap_pct, base_tau, base_eta, events_total):
    potential = base_potential * (1 + events_total["potential_pct_delta"] / 100)
    gap_pct = base_gap_pct + events_total["gap_delta"]
    actual = potential * (1 + gap_pct / 100)
    tau = min(max(base_tau + events_total["tau_delta"], 0.01), 0.60)
    eta = min(max(base_eta + events_total["eta_delta"], 0.10), 3.00)
    return actual, potential, gap_pct, tau, eta


def compute_budget(actual, potential, tau, eta, anchor_mode, anchor_value, structural_spending_delta=0.0, cyclical_spending_delta=0.0):
    ratio = actual / potential if potential > 0 else np.nan
    r_struct = tau * potential
    r_actual = r_struct * (ratio ** eta)
    revenue_cyclical = r_actual - r_struct

    if anchor_mode == "Výdaje":
        base_expenditure = anchor_value
    elif anchor_mode == "Strukturální saldo":
        base_expenditure = r_struct - anchor_value
    else:
        base_expenditure = r_actual - anchor_value

    total_expenditure = base_expenditure + structural_spending_delta + cyclical_spending_delta
    structural = r_struct - (base_expenditure + structural_spending_delta)
    cyclical = revenue_cyclical - cyclical_spending_delta
    total = r_actual - total_expenditure

    return {
        "r_struct": r_struct,
        "r_actual": r_actual,
        "revenue_cyclical": revenue_cyclical,
        "base_expenditure": base_expenditure,
        "total_expenditure": total_expenditure,
        "structural": structural,
        "cyclical": cyclical,
        "total": total,
        "structural_spending_delta": structural_spending_delta,
        "cyclical_spending_delta": cyclical_spending_delta,
    }


def classify_gap(gap_pct):
    if gap_pct < -0.5:
        return "Ekonomika je pod potenciálem. Příjmy jsou stlačené dolů a cyklická složka je záporná."
    if gap_pct > 0.5:
        return "Ekonomika je nad potenciálem. Příjmy jsou dočasně zvýšené a cyklická složka je kladná."
    return "Ekonomika je poblíž potenciálu. Cyklická složka je malá."


def small_change_effect(potential, tau, eta, gap):
    return tau * eta * potential * ((1 + gap) ** max(eta - 1, 0)) * 0.01


init_state()

with st.sidebar:
    st.header("Nastavení modelu")
    st.selectbox("Scénář", list(PRESETS.keys()), key="preset_name", on_change=apply_preset)
    st.caption(PRESETS[st.session_state.preset_name]["description"])

    st.subheader("Makro blok")
    st.radio("Dopočítávaná proměnná", ["Mezera produktu", "Skutečné HDP", "Potenciální HDP"], key="macro_target")

    if st.session_state.macro_target == "Mezera produktu":
        st.number_input("Skutečné výchozí HDP", min_value=100.0, step=50.0, key="base_actual")
        st.number_input("Výchozí potenciální HDP", min_value=100.0, step=50.0, key="base_potential")
        st.caption("Výchozí mezera produktu se dopočítá z HDP a potenciálního HDP.")
    elif st.session_state.macro_target == "Skutečné HDP":
        st.number_input("Výchozí potenciální HDP", min_value=100.0, step=50.0, key="base_potential")
        st.slider("Výchozí mezera produktu (%)", min_value=-10.0, max_value=10.0, step=0.1, key="base_gap_pct")
        st.caption("Skutečné výchozí HDP se dopočítá z potenciálního HDP a mezery produktu.")
    else:
        st.number_input("Skutečné výchozí HDP", min_value=100.0, step=50.0, key="base_actual")
        st.slider("Výchozí mezera produktu (%)", min_value=-10.0, max_value=10.0, step=0.1, key="base_gap_pct")
        st.caption("Výchozí potenciální HDP se dopočítá ze skutečného HDP a mezery produktu.")
  
    st.subheader("Makroekonomické události")
    st.multiselect("Vyber události", list(EVENTS.keys()), key="selected_events")
    st.caption("Události upraví hodnoty použité v modelu. Vždy vidíš základ i výsledné hodnoty po událostech.")

    st.subheader("Rozpočtový blok")
    st.slider("Příjmová kvóta při potenciálu", min_value=0.05, max_value=0.40, step=0.005, key="base_tau")
    st.slider("Elasticita příjmů vůči HDP", min_value=0.50, max_value=2.00, step=0.05, key="base_eta")
    st.radio("Co držet fixní", ["Výdaje", "Strukturální saldo", "Celkové saldo"], key="anchor_mode")
    st.number_input(f"Hodnota: {st.session_state.anchor_mode}", step=10.0, key="anchor_value")

base_actual, base_potential, base_gap, base_gap_pct, macro_error = solve_macro(
    st.session_state.macro_target,
    st.session_state.base_actual,
    st.session_state.base_potential,
    st.session_state.base_gap_pct,
)
if macro_error:
    st.error(macro_error)
    st.stop()

events_total = aggregate_events(st.session_state.selected_events)
actual, potential, gap_pct, tau, eta = apply_events(
    base_actual,
    base_potential,
    base_gap_pct,
    st.session_state.base_tau,
    st.session_state.base_eta,
    events_total,
)
gap = gap_pct / 100

budget = compute_budget(
    actual,
    potential,
    tau,
    eta,
    st.session_state.anchor_mode,
    st.session_state.anchor_value,
    events_total["structural_spending_delta"],
    events_total["cyclical_spending_delta"],
)

st.title("Simulátor cyklické a strukturální složky salda státního rozpočtu")
st.write("Základní vstupy zadáváš v levém panelu. Hlavní panel pracuje se stejnými hodnotami; pokud vybereš události, v levém panelu se zároveň ukáže jejich efektivní dopad na model.")

with st.expander("Jak model funguje"):
    st.markdown(
        """
- Platí identita: **celkové saldo = strukturální saldo + cyklická složka**.
- Strukturální příjmy se počítají z potenciálního HDP.
- Skutečné příjmy se počítají ze skutečného HDP a elasticity.
- Události mohou změnit mezeru produktu, potenciální HDP, příjmovou kvótu, elasticitu i výdaje.
        """
    )

m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Skutečné HDP", fmt_money(actual), delta=fmt_money(actual - base_actual))
m2.metric("Potenciální HDP", fmt_money(potential), delta=fmt_money(potential - base_potential))
m3.metric("Mezera produktu", fmt_pct(gap_pct), delta=fmt_pct(gap_pct - base_gap_pct))
m4.metric("Strukturální saldo", fmt_money(budget["structural"]))
m5.metric("Cyklická složka", fmt_money(budget["cyclical"]))
m6.metric("Celkové saldo", fmt_money(budget["total"]))

if st.session_state.macro_target == "Mezera produktu":
    st.info(f"Zadané jsou dvě veličiny: skutečné HDP a potenciální HDP. Dopočtená mezera produktu je {fmt_pct(base_gap_pct)}.")
elif st.session_state.macro_target == "Skutečné HDP":
    st.info(f"Zadané jsou dvě veličiny: potenciální HDP a mezera produktu. Dopočtené skutečné HDP je {fmt_money(base_actual)}.")
else:
    st.info(f"Zadané jsou dvě veličiny: skutečné HDP a mezera produktu. Dopočtené potenciální HDP je {fmt_money(base_potential)}.")

if events_total["notes"]:
    st.subheader("Dopad vybraných událostí")
    for name, typ, explanation in events_total["notes"]:
        st.info(f"**{name}** — {typ}. {explanation}")

left, right = st.columns([1.2, 1])
with left:
    st.subheader("Interpretace")
    st.info(classify_gap(gap_pct))
    df = pd.DataFrame([
        ["Strukturální příjmy", fmt_money(budget["r_struct"]), fmt_pct(100 * budget["r_struct"] / potential)],
        ["Skutečné příjmy", fmt_money(budget["r_actual"]), fmt_pct(100 * budget["r_actual"] / actual)],
        ["Základní výdaje", fmt_money(budget["base_expenditure"]), fmt_pct(100 * budget["base_expenditure"] / actual)],
        ["Strukturální výdajový šok", fmt_money(budget["structural_spending_delta"]), fmt_pct(100 * budget["structural_spending_delta"] / potential)],
        ["Cyklický výdajový šok", fmt_money(budget["cyclical_spending_delta"]), fmt_pct(100 * budget["cyclical_spending_delta"] / potential)],
        ["Celkové výdaje", fmt_money(budget["total_expenditure"]), fmt_pct(100 * budget["total_expenditure"] / actual)],
        ["Strukturální saldo", fmt_money(budget["structural"]), fmt_pct(100 * budget["structural"] / potential)],
        ["Cyklická složka", fmt_money(budget["cyclical"]), fmt_pct(100 * budget["cyclical"] / potential)],
        ["Celkové saldo", fmt_money(budget["total"]), fmt_pct(100 * budget["total"] / actual)],
    ], columns=["Ukazatel", "Hodnota", "% HDP"])
    st.dataframe(df, use_container_width=True, hide_index=True)
    approx = tau * eta * potential * gap - events_total["cyclical_spending_delta"]
    diff = budget["cyclical"] - approx
    st.write(f"Přesná cyklická složka je {fmt_money(budget['cyclical'])}. Lineární aproximace dává {fmt_money(approx)} a rozdíl je {fmt_money(diff)}.")

with right:
    st.subheader("Rozklad salda")
    fig_bar = go.Figure()
    fig_bar.add_bar(name="Strukturální saldo", x=["Saldo"], y=[budget["structural"]], marker_color="#1f77b4")
    fig_bar.add_bar(name="Cyklická složka", x=["Saldo"], y=[budget["cyclical"]], marker_color="#ff7f0e")
    fig_bar.add_bar(name="Celkové saldo", x=["Saldo"], y=[budget["total"]], marker_color="#2ca02c")
    fig_bar.update_layout(barmode="group", height=360, margin=dict(l=10, r=10, t=20, b=10), yaxis_title="mld. Kč")
    st.plotly_chart(fig_bar, use_container_width=True)
    one_pp = small_change_effect(potential, tau, eta, gap)
    st.write(f"Posun mezery produktu o 1 p. b. mění cyklickou složku přibližně o {fmt_money(one_pp)} na příjmové straně.")

st.subheader("Citlivost na mezeru produktu")
gaps = np.linspace(-8, 8, 161)
records = []
for g in gaps:
    y = potential * (1 + g / 100)
    vals = compute_budget(y, potential, tau, eta, st.session_state.anchor_mode, st.session_state.anchor_value, events_total["structural_spending_delta"], events_total["cyclical_spending_delta"])
    records.append({"gap": g, "total": vals["total"], "structural": vals["structural"], "cyclical": vals["cyclical"]})
line_df = pd.DataFrame(records)
fig_line = go.Figure()
fig_line.add_trace(go.Scatter(x=line_df["gap"], y=line_df["total"], mode="lines", name="Celkové saldo", line=dict(color="#2ca02c", width=3)))
fig_line.add_trace(go.Scatter(x=line_df["gap"], y=line_df["structural"], mode="lines", name="Strukturální saldo", line=dict(color="#1f77b4", width=3, dash="dash")))
fig_line.add_trace(go.Scatter(x=line_df["gap"], y=line_df["cyclical"], mode="lines", name="Cyklická složka", line=dict(color="#ff7f0e", width=3)))
fig_line.add_vline(x=gap_pct, line_width=1.5, line_dash="dot")
fig_line.update_layout(height=420, margin=dict(l=10, r=10, t=20, b=10), xaxis_title="Mezera produktu (%)", yaxis_title="mld. Kč")
st.plotly_chart(fig_line, use_container_width=True)
