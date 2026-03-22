
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Simulátor cyklické a strukturální složky salda", layout="wide")

PRESETS = {
    "Vlastní": {
        "actual": 8000.0,
        "potential": 8000.0,
        "gap_pct": 0.0,
        "tau": 0.20,
        "eta": 1.00,
        "anchor_mode": "Výdaje",
        "anchor_value": 1650.0,
        "description": "Ruční nastavení bez předvyplněného makro scénáře.",
    },
    "Recese": {
        "actual": 7760.0,
        "potential": 8000.0,
        "gap_pct": -3.0,
        "tau": 0.20,
        "eta": 1.05,
        "anchor_mode": "Výdaje",
        "anchor_value": 1650.0,
        "description": "Ekonomika je pod potenciálem, příjmy zaostávají a cyklická složka je záporná.",
    },
    "Neutrální ekonomika": {
        "actual": 8000.0,
        "potential": 8000.0,
        "gap_pct": 0.0,
        "tau": 0.20,
        "eta": 1.00,
        "anchor_mode": "Výdaje",
        "anchor_value": 1650.0,
        "description": "Skutečný výkon odpovídá potenciálu, cyklická složka je blízko nule.",
    },
    "Přehřátí": {
        "actual": 8240.0,
        "potential": 8000.0,
        "gap_pct": 3.0,
        "tau": 0.20,
        "eta": 1.10,
        "anchor_mode": "Výdaje",
        "anchor_value": 1650.0,
        "description": "Ekonomika běží nad potenciálem, příjmy jsou dočasně vyšší a saldo vypadá lépe.",
    },
}

EVENTS = {
    "Negativní poptávkový šok": {
        "type": "Cyklická složka",
        "gap_delta": -2.5,
        "potential_pct_delta": 0.0,
        "tau_delta": 0.0,
        "eta_delta": 0.0,
        "structural_spending_delta": 0.0,
        "cyclical_spending_delta": 0.0,
        "explanation": "Domácnosti a firmy omezí poptávku. Produkce klesne pod potenciál a cyklická složka salda se zhorší hlavně přes nižší příjmy.",
    },
    "Přehřátí ekonomiky": {
        "type": "Cyklická složka",
        "gap_delta": 2.5,
        "potential_pct_delta": 0.0,
        "tau_delta": 0.0,
        "eta_delta": 0.0,
        "structural_spending_delta": 0.0,
        "cyclical_spending_delta": 0.0,
        "explanation": "Dočasně silná poptávka zvyšuje výstup nad potenciál. Příjmy rostou a cyklická složka salda je kladná.",
    },
    "Růst nezaměstnanosti": {
        "type": "Cyklická složka",
        "gap_delta": -1.5,
        "potential_pct_delta": 0.0,
        "tau_delta": 0.0,
        "eta_delta": 0.0,
        "structural_spending_delta": 0.0,
        "cyclical_spending_delta": 25.0,
        "explanation": "Vedle poklesu příjmů rostou i dočasné výdaje na dávky. Cyklická složka se proto zhoršuje na příjmové i výdajové straně.",
    },
    "Energetický cenový šok": {
        "type": "Smíšený dopad",
        "gap_delta": -1.8,
        "potential_pct_delta": -0.7,
        "tau_delta": 0.0,
        "eta_delta": 0.0,
        "structural_spending_delta": 0.0,
        "cyclical_spending_delta": 15.0,
        "explanation": "Část dopadu je cyklická přes oslabení ekonomiky, část může být strukturální přes nižší produktivitu a vyšší nákladovost.",
    },
    "Dočasná kompenzace domácnostem": {
        "type": "Cyklická složka",
        "gap_delta": 0.0,
        "potential_pct_delta": 0.0,
        "tau_delta": 0.0,
        "eta_delta": 0.0,
        "structural_spending_delta": 0.0,
        "cyclical_spending_delta": 35.0,
        "explanation": "Vláda zavede jednorázové či dočasné transfery. Celkové saldo se zhorší hlavně přes dočasnou, tedy cyklicky chápanou výdajovou složku.",
    },
    "Trvalé zvýšení důchodů": {
        "type": "Strukturální složka",
        "gap_delta": 0.0,
        "potential_pct_delta": 0.0,
        "tau_delta": 0.0,
        "eta_delta": 0.0,
        "structural_spending_delta": 40.0,
        "cyclical_spending_delta": 0.0,
        "explanation": "Jde o trvalé navýšení výdajové základny. Zhoršuje strukturální saldo i při ekonomice na potenciálu.",
    },
    "Vyšší obranné výdaje": {
        "type": "Strukturální složka",
        "gap_delta": 0.0,
        "potential_pct_delta": 0.0,
        "tau_delta": 0.0,
        "eta_delta": 0.0,
        "structural_spending_delta": 60.0,
        "cyclical_spending_delta": 0.0,
        "explanation": "Pokud jsou nové výdaje trvalé, promítají se hlavně do strukturální složky rozpočtu.",
    },
    "Snížení DPH": {
        "type": "Strukturální složka",
        "gap_delta": 0.0,
        "potential_pct_delta": 0.0,
        "tau_delta": -0.010,
        "eta_delta": 0.0,
        "structural_spending_delta": 0.0,
        "cyclical_spending_delta": 0.0,
        "explanation": "Nižší sazby snižují příjmovou kvótu i při stejném HDP. To je typická změna strukturálního salda.",
    },
    "Lepší výběr daní": {
        "type": "Strukturální složka",
        "gap_delta": 0.0,
        "potential_pct_delta": 0.0,
        "tau_delta": 0.008,
        "eta_delta": 0.0,
        "structural_spending_delta": 0.0,
        "cyclical_spending_delta": 0.0,
        "explanation": "Vyšší efektivita výběru daní zlepšuje strukturální příjmy a tím i strukturální saldo.",
    },
    "Daňová progrese": {
        "type": "Strukturální složka",
        "gap_delta": 0.0,
        "potential_pct_delta": 0.0,
        "tau_delta": 0.0,
        "eta_delta": 0.15,
        "structural_spending_delta": 0.0,
        "cyclical_spending_delta": 0.0,
        "explanation": "Vyšší progrese zvyšuje citlivost příjmů na cyklus. Struktura daňového systému tak mění sílu cyklické složky.",
    },
    "Reforma trhu práce a produktivity": {
        "type": "Strukturální složka",
        "gap_delta": -0.5,
        "potential_pct_delta": 2.0,
        "tau_delta": 0.0,
        "eta_delta": 0.0,
        "structural_spending_delta": 0.0,
        "cyclical_spending_delta": 0.0,
        "explanation": "Vyšší potenciální produkt posouvá strukturální základnu ekonomiky. Krátkodobě může vzniknout zápornější mezera produktu, protože potenciál roste rychleji než skutečný výstup.",
    },
    "Konsolidační balíček": {
        "type": "Strukturální složka",
        "gap_delta": -0.4,
        "potential_pct_delta": 0.0,
        "tau_delta": 0.006,
        "eta_delta": 0.0,
        "structural_spending_delta": -30.0,
        "cyclical_spending_delta": 0.0,
        "explanation": "Kombinace vyšších příjmů a nižších trvalých výdajů zlepšuje strukturální saldo, i když krátkodobě může lehce tlumit poptávku.",
    },
}


def fmt_money(x):
    return f"{x:,.1f} mld. Kč".replace(",", " ")


def fmt_pct(x):
    return f"{x:.2f} %"


def init_state():
    default = PRESETS["Vlastní"]
    defaults = {
        "preset": "Vlastní",
        "actual": default["actual"],
        "potential": default["potential"],
        "gap_pct": default["gap_pct"],
        "tau": default["tau"],
        "eta": default["eta"],
        "anchor_mode": default["anchor_mode"],
        "anchor_value": default["anchor_value"],
        "macro_target": "Mezera produktu",
        "selected_events": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def apply_preset():
    config = PRESETS[st.session_state.preset]
    st.session_state.actual = config["actual"]
    st.session_state.potential = config["potential"]
    st.session_state.gap_pct = config["gap_pct"]
    st.session_state.tau = config["tau"]
    st.session_state.eta = config["eta"]
    st.session_state.anchor_mode = config["anchor_mode"]
    st.session_state.anchor_value = config["anchor_value"]
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


def aggregate_events(selected_events):
    totals = {
        "gap_delta": 0.0,
        "potential_pct_delta": 0.0,
        "tau_delta": 0.0,
        "eta_delta": 0.0,
        "structural_spending_delta": 0.0,
        "cyclical_spending_delta": 0.0,
        "explanations": [],
        "types": [],
    }
    for event_name in selected_events:
        event = EVENTS[event_name]
        for key in [
            "gap_delta",
            "potential_pct_delta",
            "tau_delta",
            "eta_delta",
            "structural_spending_delta",
            "cyclical_spending_delta",
        ]:
            totals[key] += event[key]
        totals["explanations"].append((event_name, event["type"], event["explanation"]))
        totals["types"].append(event["type"])
    return totals


def apply_events(actual, potential, gap_pct, tau, eta, events_total):
    potential_eff = potential * (1 + events_total["potential_pct_delta"] / 100)
    gap_eff = gap_pct + events_total["gap_delta"]
    actual_eff = potential_eff * (1 + gap_eff / 100)
    tau_eff = min(max(tau + events_total["tau_delta"], 0.01), 0.60)
    eta_eff = min(max(eta + events_total["eta_delta"], 0.10), 3.00)
    return actual_eff, potential_eff, gap_eff, tau_eff, eta_eff


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
        "ratio": ratio,
        "r_struct": r_struct,
        "r_actual": r_actual,
        "revenue_cyclical": revenue_cyclical,
        "cyclical": cyclical,
        "base_expenditure": base_expenditure,
        "total_expenditure": total_expenditure,
        "structural": structural,
        "total": total,
        "structural_spending_delta": structural_spending_delta,
        "cyclical_spending_delta": cyclical_spending_delta,
    }


def classify_gap(gap):
    if gap < -0.5:
        return "Ekonomika je pod potenciálem. Příjmy jsou proti strukturální úrovni stlačené dolů a cyklická složka salda je záporná."
    if gap > 0.5:
        return "Ekonomika je nad potenciálem. Příjmy jsou dočasně nafouknuté a cyklická složka salda je kladná."
    return "Ekonomika je poblíž potenciálu. Cyklická složka je malá a celkové saldo je blízko strukturálnímu saldu."


def event_summary(types):
    unique_types = sorted(set(types))
    if not unique_types:
        return "Bez dodatečných událostí."
    return " + ".join(unique_types)


def small_change_effect(potential, tau, eta, gap):
    return tau * eta * potential * ((1 + gap) ** max(eta - 1, 0)) * 0.01


init_state()

with st.sidebar:
    st.header("Nastavení modelu")
    st.selectbox("Scénář", list(PRESETS.keys()), key="preset", on_change=apply_preset)
    st.caption(PRESETS[st.session_state.preset]["description"])

    st.subheader("Makro blok")
    st.radio(
        "Dopočítávaná proměnná",
        ["Mezera produktu", "Skutečné HDP", "Potenciální HDP"],
        key="macro_target",
    )
    st.number_input("Skutečné HDP", min_value=100.0, step=50.0, key="actual")
    st.number_input("Potenciální HDP", min_value=100.0, step=50.0, key="potential")
    st.slider("Mezera produktu (%)", min_value=-10.0, max_value=10.0, step=0.1, key="gap_pct")

    st.subheader("Rozpočtový blok")
    st.slider("Příjmová kvóta při potenciálu", min_value=0.05, max_value=0.40, step=0.005, key="tau")
    st.slider("Elasticita příjmů vůči HDP", min_value=0.50, max_value=2.00, step=0.05, key="eta")
    st.radio("Co držet fixní", ["Výdaje", "Strukturální saldo", "Celkové saldo"], key="anchor_mode")
    st.number_input(f"Hodnota: {st.session_state.anchor_mode}", step=10.0, key="anchor_value")

    st.subheader("Makroekonomické události")
    st.multiselect("Vyber události", list(EVENTS.keys()), key="selected_events")
    st.caption("Události upravují efektivní hodnoty modelu a ukazují, zda působí hlavně strukturálně, cyklicky, nebo smíšeně.")

base_actual = st.session_state.actual
base_potential = st.session_state.potential
base_gap_pct = st.session_state.gap_pct
base_tau = st.session_state.tau
base_eta = st.session_state.eta
base_anchor_mode = st.session_state.anchor_mode
base_anchor_value = st.session_state.anchor_value

base_actual, base_potential, base_gap, base_gap_pct, macro_error = solve_macro(
    st.session_state.macro_target,
    base_actual,
    base_potential,
    base_gap_pct,
)

if macro_error:
    st.error(macro_error)
    st.stop()

events_total = aggregate_events(st.session_state.selected_events)
actual, potential, gap_pct, tau, eta = apply_events(
    base_actual,
    base_potential,
    base_gap_pct,
    base_tau,
    base_eta,
    events_total,
)
gap = gap_pct / 100

budget = compute_budget(
    actual,
    potential,
    tau,
    eta,
    base_anchor_mode,
    base_anchor_value,
    structural_spending_delta=events_total["structural_spending_delta"],
    cyclical_spending_delta=events_total["cyclical_spending_delta"],
)

st.title("Simulátor cyklické a strukturální složky salda státního rozpočtu")
st.write("Aplikace odděluje celkové saldo na strukturální a cyklickou část a ukazuje, jak se změny HDP, daňového nastavení a výdajových šoků promítnou do salda.")

with st.expander("Jak model funguje"):
    st.markdown(
        """
- Platí identita: **celkové saldo = strukturální saldo + cyklická složka**.
- Strukturální příjmy se počítají z potenciálního HDP.
- Skutečné příjmy se počítají ze skutečného HDP a zvolené elasticity.
- Základní výdaje držíš fixní přes zvolenou kotvu, ale události mohou přidat strukturální nebo cyklický výdajový šok.
- Když je ekonomika pod potenciálem, cyklická složka bývá záporná; nad potenciálem kladná.
        """
    )

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Skutečné HDP", fmt_money(actual), delta=fmt_money(actual - base_actual))
c2.metric("Potenciální HDP", fmt_money(potential), delta=fmt_money(potential - base_potential))
c3.metric("Mezera produktu", fmt_pct(gap_pct), delta=fmt_pct(gap_pct - base_gap_pct))
c4.metric("Strukturální saldo", fmt_money(budget["structural"]))
c5.metric("Cyklická složka", fmt_money(budget["cyclical"]))
c6.metric("Celkové saldo", fmt_money(budget["total"]))

st.caption(f"Typ vybraných událostí: {event_summary(events_total['types'])}")

if events_total["explanations"]:
    st.subheader("Dopad vybraných událostí")
    for name, typ, explanation in events_total["explanations"]:
        st.info(f"**{name}** — {typ}. {explanation}")

left, right = st.columns([1.2, 1])

with left:
    st.subheader("Interpretace")
    st.info(classify_gap(gap_pct))

    rows = [
        ["Strukturální příjmy", fmt_money(budget["r_struct"]), fmt_pct(100 * budget["r_struct"] / potential)],
        ["Skutečné příjmy", fmt_money(budget["r_actual"]), fmt_pct(100 * budget["r_actual"] / actual)],
        ["Základní výdaje", fmt_money(budget["base_expenditure"]), fmt_pct(100 * budget["base_expenditure"] / actual)],
        ["Strukturální výdajový šok", fmt_money(budget["structural_spending_delta"]), fmt_pct(100 * budget["structural_spending_delta"] / potential)],
        ["Cyklický výdajový šok", fmt_money(budget["cyclical_spending_delta"]), fmt_pct(100 * budget["cyclical_spending_delta"] / potential)],
        ["Celkové výdaje", fmt_money(budget["total_expenditure"]), fmt_pct(100 * budget["total_expenditure"] / actual)],
        ["Strukturální saldo", fmt_money(budget["structural"]), fmt_pct(100 * budget["structural"] / potential)],
        ["Cyklická složka", fmt_money(budget["cyclical"]), fmt_pct(100 * budget["cyclical"] / potential)],
        ["Celkové saldo", fmt_money(budget["total"]), fmt_pct(100 * budget["total"] / actual)],
    ]
    df = pd.DataFrame(rows, columns=["Ukazatel", "Hodnota", "% HDP"])
    st.dataframe(df, use_container_width=True, hide_index=True)

    approx = tau * eta * potential * gap - events_total["cyclical_spending_delta"]
    diff = budget["cyclical"] - approx
    st.markdown("### Přesný vs. přibližný výpočet")
    st.write(
        f"Přesná cyklická složka: {fmt_money(budget['cyclical'])}. Lineární aproximace pro malé mezery produktu a danou elasticitu: {fmt_money(approx)}. Rozdíl: {fmt_money(diff)}."
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
        f"Při aktuálním nastavení změní posun mezery produktu o 1 procentní bod cyklickou složku přibližně o {fmt_money(one_pp)} na příjmové straně."
    )
    if events_total["cyclical_spending_delta"] != 0:
        st.write(
            f"Navíc je právě aktivní cyklický výdajový šok ve výši {fmt_money(events_total['cyclical_spending_delta'])}, takže čistý dopad na cyklickou složku je horší o tuto částku."
        )

st.subheader("Citlivost na mezeru produktu")
gaps = np.linspace(-8, 8, 161)
records = []
for g in gaps:
    y = potential * (1 + g / 100)
    vals = compute_budget(
        y,
        potential,
        tau,
        eta,
        base_anchor_mode,
        base_anchor_value,
        structural_spending_delta=events_total["structural_spending_delta"],
        cyclical_spending_delta=events_total["cyclical_spending_delta"],
    )
    records.append({
        "gap": g,
        "total": vals["total"],
        "structural": vals["structural"],
        "cyclical": vals["cyclical"],
    })
line_df = pd.DataFrame(records)
fig_line = go.Figure()
fig_line.add_trace(go.Scatter(x=line_df["gap"], y=line_df["total"], mode="lines", name="Celkové saldo", line=dict(color="#2ca02c", width=3)))
fig_line.add_trace(go.Scatter(x=line_df["gap"], y=line_df["structural"], mode="lines", name="Strukturální saldo", line=dict(color="#1f77b4", width=3, dash="dash")))
fig_line.add_trace(go.Scatter(x=line_df["gap"], y=line_df["cyclical"], mode="lines", name="Cyklická složka", line=dict(color="#ff7f0e", width=3)))
fig_line.add_vline(x=gap_pct, line_width=1.5, line_dash="dot")
fig_line.update_layout(height=420, margin=dict(l=10, r=10, t=20, b=10), xaxis_title="Mezera produktu (%)", yaxis_title="mld. Kč")
st.plotly_chart(fig_line, use_container_width=True)

st.subheader("Co se změnilo po událostech")
changes = pd.DataFrame([
    ["Skutečné HDP", fmt_money(base_actual), fmt_money(actual), fmt_money(actual - base_actual)],
    ["Potenciální HDP", fmt_money(base_potential), fmt_money(potential), fmt_money(potential - base_potential)],
    ["Mezera produktu", fmt_pct(base_gap_pct), fmt_pct(gap_pct), fmt_pct(gap_pct - base_gap_pct)],
    ["Příjmová kvóta", fmt_pct(base_tau * 100), fmt_pct(tau * 100), fmt_pct((tau - base_tau) * 100)],
    ["Elasticita příjmů", f"{base_eta:.2f}", f"{eta:.2f}", f"{eta - base_eta:+.2f}"],
], columns=["Proměnná", "Základ", "Po událostech", "Změna"])
st.dataframe(changes, use_container_width=True, hide_index=True)

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
1. Začni s presetem **Recese** a bez dalších událostí; studenti uvidí čistě příjmový cyklický kanál.
2. Potom přidej **Růst nezaměstnanosti**; stejné oslabení ekonomiky už teď zhoršuje saldo i přes výdaje.
3. Přepni na **Snížení DPH** nebo **Trvalé zvýšení důchodů**; studenti rozliší strukturální zhoršení od pouhého cyklického výkyvu.
4. Nakonec zkombinuj **Reformu trhu práce a produktivity** s recesí; studenti uvidí, že změna potenciálu a změna skutečného výkonu nejsou totéž.
    """
)
