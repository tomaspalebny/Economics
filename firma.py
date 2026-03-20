import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Simulace firmy – Mikroekonomie", layout="wide")

st.title("🏭 Plnohodnotná simulace firmy v krátkém období")
st.markdown(
    """
Tato interaktivní aplikace simuluje chování firmy v dokonale konkurenčním trhu.
Obsahuje produkční funkci, mezní a průměrný produkt, nákladové křivky,
tržní cenu, mezní příjem, optimalizaci výroby a výpočet zisku.
"""
)

st.sidebar.header("⚙️ Parametry modelu")

FC = st.sidebar.slider("Fixní náklady (FC)", 0.0, 1000.0, 200.0, 10.0)
w = st.sidebar.slider("Cena práce (w)", 1.0, 100.0, 20.0, 1.0)

st.sidebar.markdown("### Parametry produkční funkce Q(L) = aL - bL²")
a = st.sidebar.slider("a – produktivita práce", 1.0, 50.0, 20.0, 1.0)
b = st.sidebar.slider("b – síla klesajících výnosů", 0.001, 0.2, 0.04, 0.001)
max_L = st.sidebar.slider("Max. množství práce (L)", 1.0, 1000.0, 300.0, 1.0)
P = st.sidebar.slider("Tržní cena P", 1.0, 200.0, 40.0, 1.0)

points = 1200
L_full = np.linspace(0.0, max_L, points)
Q_full = a * L_full - b * L_full**2
MP_full = a - 2 * b * L_full

feasible = MP_full > 1e-9
L = L_full[feasible]
Q = Q_full[feasible]
MP = MP_full[feasible]

positive_q = Q > 1e-9
L = L[positive_q]
Q = Q[positive_q]
MP = MP[positive_q]

if len(Q) == 0:
    st.error("Pro zadané parametry nevzniká kladná produkce. Zvyšte a nebo snižte b.")
    st.stop()

AP = Q / L
VC = w * L
TC = FC + VC
AFC = FC / Q
AVC = VC / Q
AC = TC / Q
MC = w / MP

TR = P * Q
MR = np.full(Q.shape, P, dtype=float)
profit = TR - TC
profit_shutdown = -FC

shutdown = P < np.min(AVC)

if shutdown:
    L_opt = 0.0
    Q_opt = 0.0
    TR_opt = 0.0
    TC_opt = FC
    profit_opt = profit_shutdown
    idx_opt = None
else:
    idx_opt = int(np.argmax(profit))
    L_opt = float(L[idx_opt])
    Q_opt = float(Q[idx_opt])
    TR_opt = float(TR[idx_opt])
    TC_opt = float(TC[idx_opt])
    profit_opt = float(profit[idx_opt])

idx_min_avc = int(np.argmin(AVC))
idx_min_ac = int(np.argmin(AC))
Q_min_avc = float(Q[idx_min_avc])
Q_min_ac = float(Q[idx_min_ac])
min_avc = float(AVC[idx_min_avc])
min_ac = float(AC[idx_min_ac])
mc_at_min_avc = float(MC[idx_min_avc])
mc_at_min_ac = float(MC[idx_min_ac])

st.subheader("📈 Interpretace – optimální rozhodnutí firmy")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Optimální práce L*", f"{L_opt:.2f}")
col2.metric("Optimální produkce Q*", f"{Q_opt:.2f}")
col3.metric("Optimální tržby TR*", f"{TR_opt:.2f}")
col4.metric("Optimální zisk π*", f"{profit_opt:.2f}")

if shutdown:
    st.error(
        f"Firma by měla v krátkém období uzavřít výrobu, protože P = {P:.2f} < min(AVC) = {min_avc:.2f}. "
        f"Při uzavření je ztráta rovna fixním nákladům: π = -FC = {-FC:.2f}."
    )
else:
    st.success(
        f"Firma vyrábí, protože P = {P:.2f} ≥ min(AVC) = {min_avc:.2f}. "
        f"Optimum vychází přibližně v bodě, kde MR = MC: MR = {P:.2f}, MC(Q*) = {MC[idx_opt]:.2f}."
    )

st.markdown(
    f"- Produkční funkce: Q(L) = aL - bL², tedy zde Q(L) = {a:.2f}L - {b:.3f}L².\n"
    f"- Mezní produkt práce: MP(L) = a - 2bL, tedy MP(L) = {a:.2f} - {2*b:.3f}L.\n"
    f"- Průměrný produkt práce: AP(L) = Q/L.\n"
    f"- Mezní náklady: MC = dTC/dQ = w/MP, proto při klesajícím MP rostou MC."
)

st.markdown("### Kontroly základních vztahů")
check1 = np.all(np.diff(MP) <= 1e-8)
check2 = np.all(np.diff(MC) >= -1e-8)
check3 = abs(mc_at_min_avc - min_avc) < 0.15
check4 = abs(mc_at_min_ac - min_ac) < 0.15

st.write(f"- Klesající mezní produkt: {'Ano' if check1 else 'Ne'}")
st.write(f"- Rostoucí mezní náklady v ekonomicky relevantní oblasti (MP > 0): {'Ano' if check2 else 'Ne'}")
st.write(f"- MC protíná AVC v minimu AVC: {'Ano' if check3 else 'Přibližně ne'}")
st.write(f"- MC protíná AC v minimu AC: {'Ano' if check4 else 'Přibližně ne'}")

tabs = st.tabs([
    "📘 Produkce, MP a AP",
    "💰 Náklady (TC, VC, FC)",
    "📉 AC, AVC, AFC",
    "📈 MC a MR",
    "📊 Zisk firmy"
])

with tabs[0]:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(L, Q, label="Q(L) – produkce")
    ax.plot(L, MP, label="MP(L) – mezní produkt")
    ax.plot(L, AP, label="AP(L) – průměrný produkt")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_title("Produkční funkce, mezní produkt a průměrný produkt")
    ax.set_xlabel("Práce L")
    ax.set_ylabel("Produkt")
    ax.legend()
    ax.grid(alpha=0.25)
    st.pyplot(fig)

with tabs[1]:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(Q, TC, label="TC")
    ax.plot(Q, VC, label="VC")
    ax.plot(Q, np.full_like(Q, FC), label="FC")
    if idx_opt is not None:
        ax.scatter(Q_opt, TC_opt, color="green", zorder=5, label=f"Optimum Q* = {Q_opt:.2f}")
    ax.set_title("Celkové náklady")
    ax.set_xlabel("Produkce Q")
    ax.set_ylabel("Náklady")
    ax.legend()
    ax.grid(alpha=0.25)
    st.pyplot(fig)

with tabs[2]:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(Q, AC, label="AC")
    ax.plot(Q, AVC, label="AVC")
    ax.plot(Q, AFC, label="AFC")
    ax.scatter(Q_min_avc, min_avc, color="orange", zorder=5, label="min AVC")
    ax.scatter(Q_min_ac, min_ac, color="red", zorder=5, label="min AC")
    ax.set_title("Průměrné náklady")
    ax.set_xlabel("Produkce Q")
    ax.set_ylabel("Náklady na jednotku")
    ax.legend()
    ax.grid(alpha=0.25)
    st.pyplot(fig)

with tabs[3]:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(Q, MC, label="MC", color="red")
    ax.plot(Q, MR, label="MR = P", color="blue")
    ax.scatter(Q_min_avc, mc_at_min_avc, color="orange", zorder=5, label="MC = AVC v minimu AVC")
    ax.scatter(Q_min_ac, mc_at_min_ac, color="purple", zorder=5, label="MC = AC v minimu AC")
    if idx_opt is not None:
        ax.axvline(Q_opt, linestyle="--", color="green", label=f"Q* = {Q_opt:.2f}")
    ax.set_title("Mezní náklady a mezní příjem")
    ax.set_xlabel("Produkce Q")
    ax.set_ylabel("Náklady / příjem na jednotku")
    ax.legend()
    ax.grid(alpha=0.25)
    st.pyplot(fig)

with tabs[4]:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(Q, profit, label="π(Q)", color="purple")
    ax.axhline(0, color="black", linewidth=1)
    if idx_opt is not None:
        ax.axvline(Q_opt, linestyle="--", color="green", label=f"Q* = {Q_opt:.2f}")
    ax.set_title("Zisk firmy")
    ax.set_xlabel("Produkce Q")
    ax.set_ylabel("Zisk")
    ax.legend()
    ax.grid(alpha=0.25)
    st.pyplot(fig)

st.markdown("---")
st.caption("Opravená verze: výpočty jsou omezeny na ekonomicky relevantní oblast s MP > 0, optimum respektuje podmínku uzavření a základní mikroekonomické vztahy.")
