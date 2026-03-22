import datetime
current_year = datetime.datetime.now().year
# ... na konec souboru
import streamlit as st
st.markdown(f"<hr style='margin-top:2em;margin-bottom:0.5em;'>", unsafe_allow_html=True)
st.markdown(f"<div style='text-align:center; color:gray; font-size:0.95em;'>© {current_year} Tomáš Paleta, Masarykova univerzita, Ekonomicko-správní fakulta, Brno</div>", unsafe_allow_html=True)
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.set_page_config(page_title="CR4 & HHI – Soutěžní ekonomie", layout="wide", page_icon="📊")

st.title("📊 Interaktivní analýza tržní koncentrace")
st.caption("CR4, HHI, Gap test · Nástroj pro studenty soutěžní ekonomie (MUNI ECON)")

# --- Sidebar: firm management ---
st.sidebar.header("⚙️ Firmy na trhu")

if "firms" not in st.session_state:
    st.session_state.firms = {"Firma A": 40.0, "Firma B": 20.0, "Firma C": 15.0, "Firma D": 10.0, "Firma E": 8.0}

with st.sidebar.expander("➕ Přidat / ➖ Odebrat firmu"):
    new_name = st.text_input("Název nové firmy", key="new_name")
    new_share = st.number_input("Podíl (%)", 0.0, 100.0, 5.0, key="new_share")
    if st.button("Přidat firmu") and new_name and new_name != "Ostatní":
        st.session_state.firms[new_name] = new_share
        st.rerun()
    rm = st.selectbox("Odebrat firmu", [""] + list(st.session_state.firms.keys()))
    if st.button("Odebrat") and rm:
        del st.session_state.firms[rm]
        st.rerun()

with st.sidebar.expander("🤝 Fúze dvou firem"):
    names = list(st.session_state.firms.keys())
    if len(names) >= 2:
        f1 = st.selectbox("Firma 1", names, key="m1")
        f2 = st.selectbox("Firma 2", [n for n in names if n != f1], key="m2")
        merged_name = st.text_input("Název po fúzi", value=f"{f1}+{f2}", key="mn")
        if st.button("Provést fúzi"):
            new_share = st.session_state.firms.pop(f1) + st.session_state.firms.pop(f2)
            st.session_state.firms[merged_name] = new_share
            st.rerun()

with st.sidebar.expander("📦 Ukázkové scénáře"):
    presets = {
        "AquaPlus (minerální voda)": {"AquaPlus": 44, "FreshSpring": 19, "CrystalWater": 14, "NaturaDrink": 9, "PureDrop": 7},
        "TechPay (dig. peněženky)": {"TechPay": 46, "QuickWallet": 21, "PayBee": 16, "BankPay": 9, "Tap&Go": 8},
        "DuoGas (prům. plyny)": {"DuoGas": 41, "InduAir": 38, "OxyPro": 9, "NitroFlow": 6},
        "AgroChem (hnojiva)": {"AgroChem": 36, "FertiNova": 15, "GreenYield": 12, "FarmSupply": 10, "NitroMax": 8, "Dovozci": 9},
        "Dokonalá konkurence (10 firem)": {f"Firma {i+1}": 10.0 for i in range(10)},
        "Monopol": {"Monopolista": 100.0},
    }
    choice = st.selectbox("Načíst scénář", [""] + list(presets.keys()))
    if st.button("Načíst") and choice:
        st.session_state.firms = dict(presets[choice])
        st.rerun()

st.sidebar.divider()
st.sidebar.subheader("Tržní podíly (%)")
st.sidebar.caption("⚖️ **Ostatní** = zbytek do 100 % (nezahrnují se do CR4 ani HHI)")

updated = {}
for name, share in st.session_state.firms.items():
    updated[name] = st.sidebar.slider(name, 0.0, 100.0, float(share), 0.5, key=f"sl_{name}")

firms_sum = sum(updated.values())
ostatni_share = round(100.0 - firms_sum, 1)

valid = True
if ostatni_share < 0:
    st.sidebar.error(f"⚠️ Součet firem = {firms_sum:.1f} % > 100 %. Snižte podíly!")
    valid = False
    ostatni_share = 0.0

st.sidebar.metric("Ostatní (dopočet)", f"{ostatni_share:.1f} %")

st.session_state.firms = updated

# --- Calculations: ONLY named firms, NOT "Ostatní" ---
firm_shares_pct = np.array(sorted(updated.values(), reverse=True))
n = len(firm_shares_pct)
cr4 = float(firm_shares_pct[:4].sum()) if n >= 4 else float(firm_shares_pct.sum())
hhi = float((firm_shares_pct**2).sum())
s1 = firm_shares_pct[0] if n > 0 else 0
s2 = firm_shares_pct[1] if n > 1 else 0
gap = s1 - s2
ratio = s1 / s2 if s2 > 0 else float('inf')

# For display: include Ostatní
all_shares = dict(updated)
if ostatni_share > 0:
    all_shares["Ostatní"] = ostatni_share
total = sum(all_shares.values())

if not valid or abs(total - 100.0) > 0.5:
    st.error(f"⚠️ Součet podílů = {total:.1f} % ≠ 100 %. Upravte podíly v postranním panelu!")
    st.stop()

signal = "Testovat dominanci" if s1 >= 40 and ratio >= 2 else ("Nejasné – nutná analýza" if s1 >= 40 or ratio >= 1.5 else "Nepravděpodobná dominance")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Součet podílů", f"{total:.1f} %", delta="OK ✓")
col2.metric("CR4", f"{cr4:.1f} %")
col3.metric("HHI", f"{hhi:.0f}")
col4.metric("Gap test signál", signal)

st.info(f"ℹ️ CR4 a HHI se počítají pouze z **{n} pojmenovaných firem** (bez kategorie Ostatní = {ostatni_share:.1f} %).")

c1, c2 = st.columns([1, 1])

with c1:
    st.subheader("Mapa koncentrace (CR4 × HHI)")
    fig = go.Figure()
    fig.add_hrect(y0=0, y1=1500, fillcolor="green", opacity=0.07, line_width=0)
    fig.add_hrect(y0=1500, y1=2500, fillcolor="orange", opacity=0.07, line_width=0)
    fig.add_hrect(y0=2500, y1=10000, fillcolor="red", opacity=0.07, line_width=0)
    fig.add_vline(x=60, line_dash="dash", line_color="steelblue", opacity=0.5)
    fig.add_hline(y=1500, line_dash="dash", line_color="steelblue", opacity=0.5)
    fig.add_hline(y=2500, line_dash="dash", line_color="steelblue", opacity=0.5)
    for label, x, y in [("Competitive", 30, 700), ("Moderate", 50, 1800), ("Oligopoly", 75, 2600), ("Very high\nconcentration", 85, 3500)]:
        fig.add_annotation(x=x, y=y, text=label, showarrow=False, font=dict(size=11, color="gray"))
    fig.add_trace(go.Scatter(x=[cr4], y=[hhi], mode="markers+text",
                             text=[f"CR4={cr4:.0f}%, HHI={hhi:.0f}"],
                             textposition="top center", marker=dict(size=14, color="blue"),
                             name="Aktuální stav"))
    fig.update_layout(
        xaxis=dict(title="CR4 (%)", range=[0, 105], fixedrange=True, dtick=20),
        yaxis=dict(title="HHI", range=[0, 10200], fixedrange=True, dtick=1000),
        height=500, margin=dict(l=40, r=20, t=30, b=40), showlegend=False, dragmode=False)
    st.plotly_chart(fig, use_container_width=True, config={"staticPlot": True})

with c2:
    st.subheader("Podíly firem")
    df = pd.DataFrame({"Firma": list(all_shares.keys()), "Podíl (%)": list(all_shares.values())})
    df = df.sort_values("Podíl (%)", ascending=False).reset_index(drop=True)
    colors = ["steelblue" if f != "Ostatní" else "lightgray" for f in df["Firma"]]
    fig2 = go.Figure(go.Bar(x=df["Firma"], y=df["Podíl (%)"], marker_color=colors,
                            text=df["Podíl (%)"].apply(lambda v: f"{v:.1f}%"), textposition="outside"))
    fig2.update_layout(yaxis=dict(title="Tržní podíl (%)", range=[0, 105], fixedrange=True),
                       xaxis=dict(fixedrange=True),
                       height=500, margin=dict(l=40, r=20, t=30, b=40), dragmode=False)
    st.plotly_chart(fig2, use_container_width=True, config={"staticPlot": True})

with st.expander("📋 Detailní výpočty"):
    detail = pd.DataFrame({
        "Firma": list(all_shares.keys()),
        "Podíl (%)": list(all_shares.values()),
        "Zahrnuto v CR4/HHI": ["✅ Ano" if f != "Ostatní" else "❌ Ne" for f in all_shares.keys()],
        "Podíl²": [v**2 if f != "Ostatní" else 0 for f, v in all_shares.items()],
    }).sort_values("Podíl (%)", ascending=False)
    st.dataframe(detail, use_container_width=True, hide_index=True)
    st.markdown(f"""
| Ukazatel | Hodnota | Interpretace |
|---|---|---|
| **CR4** | {cr4:.1f} % | {"< 60 % → nízká" if cr4 < 60 else ("60–80 % → střední" if cr4 < 80 else "> 80 % → vysoká")} koncentrace |
| **HHI** | {hhi:.0f} | {"< 1 500 → nízká" if hhi < 1500 else ("1 500–2 500 → střední" if hhi < 2500 else "> 2 500 → vysoká")} koncentrace |
| **Share #1** | {s1:.1f} % | Největší firma |
| **Share #2** | {s2:.1f} % | Druhá největší |
| **GAP** | {gap:.1f} p. b. | Rozdíl #1 − #2 |
| **Ratio** | {ratio:.2f} | #1 / #2 {"≥ 2 → signál dominance" if ratio >= 2 else "< 2"} |
| **Signál** | {signal} | Gap test heuristika |
""")

with st.expander("📚 Teorie – CR4, HHI, Gap test"):
    st.markdown(r"""
### CR4 (Concentration Ratio top 4)
Součet tržních podílů 4 největších firem.
- < 60 % → nízká koncentrace (konkurenční trh)
- 60–80 % → střední koncentrace
- \> 80 % → vysoká koncentrace

**Pozn.:** Do CR4 se zahrnují pouze pojmenované firmy, ne kategorie „Ostatní".

### HHI (Herfindahl-Hirschmanův index)
Součet čtverců tržních podílů všech **identifikovaných** firem (v %).
$$HHI = \sum_{i=1}^{n} s_i^2$$
- < 1 500 → nízká koncentrace
- 1 500–2 500 → střední koncentrace
- \> 2 500 → vysoká koncentrace (oligopol/monopol)
- Maximální hodnota = 10 000 (monopol)

**Pozn.:** Kategorie „Ostatní" (agregát drobných hráčů) se do HHI nezahrnuje, protože neznáme podíly jednotlivých firem v ní obsažených. Jejich individuální podíly² by byly zanedbatelné.

### Gap test (heuristika dominance)
Rychlý screening pro posouzení dominantního postavení:
- **Share #1** = podíl největší firmy
- **Share #2** = podíl druhé největší
- **GAP** = Share #1 − Share #2
- **Ratio** = Share #1 / Share #2
- Pokud Share #1 ≥ 40 % **a** Ratio ≥ 2 → **testovat dominanci**

⚠️ Gap test je pouze heuristika – nenahrazuje plnou soutěžní analýzu!
""")

st.divider()
st.caption("MPE_SOEK Soutěžní ekonomie · MUNI ECON / ITREGEP · Vytvořeno pro výuku")
