import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Simulace firmy – Mikroekonomie", layout="wide")

st.title("🏭 Plnohodnotná simulace firmy v krátkém období")
st.markdown("""
Tato interaktivní aplikace simuluje chování firmy v dokonale konkurenčním trhu.  
Obsahuje produkční funkci, mezní produkt, všechny nákladové křivky, tržní cenu,
mezní příjem, optimalizaci výroby MR = MC a výpočet zisku.
""")

# ----------------------------------------------------------
# SIDEBAR – PARAMETRY
# ----------------------------------------------------------

st.sidebar.header("⚙️ Parametry modelu")

# Náklady
FC = st.sidebar.slider("Fixní náklady (FC)", 0, 1000, 200)
w = st.sidebar.slider("Cena práce (w)", 1, 100, 20)

# Produkční funkce
st.sidebar.markdown("### Parametry produkční funkce Q(L) = aL - bL²")
a = st.sidebar.slider("a – produktivita práce", 1, 50, 20)
b = st.sidebar.slider("b – síla klesajících výnosů", 0.001, 0.2, 0.04)
max_L = st.sidebar.slider("Max. množství práce (L)", 50, 1000, 300)

# TRH
P = st.sidebar.slider("Tržní cena P", 1, 200, 40)

# ----------------------------------------------------------
# VÝPOČTY PRODUKCE
# ----------------------------------------------------------

L = np.arange(1, max_L)

# Produkce
Q = a * L - b * L**2
Q[Q < 0] = 0

# Pokud je produkce nulová, přeskoč zobrazování
valid = Q > 0
L = L[valid]
Q = Q[valid]

# Mezní produkt
MP = np.gradient(Q)

# ----------------------------------------------------------
# NÁKLADY
# ----------------------------------------------------------

VC = w * L
TC = FC + VC

AC = TC / Q
AVC = VC / Q
AFC = FC / Q

MC = np.gradient(TC) / np.gradient(Q)

# ----------------------------------------------------------
# TRŽNÍ VÝSLEDKY
# ----------------------------------------------------------

TR = P * Q                # total revenue
MR = np.full_like(Q, P)   # v DK je MR = P

profit = TR - TC          # profit π(Q)

# Optimum MR = MC
idx_opt = np.argmin(np.abs(MC - MR))
Q_opt = Q[idx_opt]
profit_opt = profit[idx_opt]

# Uzavírací podmínka
shutdown = P < np.min(AVC)

# ----------------------------------------------------------
# INTERPRETACE
# ----------------------------------------------------------

st.subheader("📈 Interpretace – optimální rozhodnutí firmy")

if shutdown:
    st.error(f"Firma by měla **uzavřít výrobu**, protože P = {P} < min(AVC) = {np.min(AVC):.2f}")
else:
    st.success(f"""
### ✔ Optimální produkce je:
**Q\* = {Q_opt:.2f} jednotek**  
Zisk firmy při optimu: **π = {profit_opt:.2f}**
""")

# Mezní produkt
if np.mean(MP[len(MP)//2:]) < np.mean(MP[:len(MP)//2]):
    st.info("Mezní produkt je **klesající** – platí zákon klesajících výnosů.")
else:
    st.info("Mezní produkt je **rostoucí**.")

# ----------------------------------------------------------
# GRAFY V ZÁLOŽKÁCH
# ----------------------------------------------------------

tabs = st.tabs([
    "📘 Produkce a MP",
    "💰 Náklady (TC, VC, FC)",
    "📉 AC, AVC, AFC",
    "📈 MC a MR (optimum firmy)",
    "📊 Zisk firmy"
])

# PRODUKCE
with tabs[0]:
    fig, ax = plt.subplots(figsize=(8,5))
    ax.plot(L, Q, label="Q (produkce)")
    ax.plot(L, MP, label="MP (mezní produkt)")
    ax.set_title("Produkční funkce a mezní produkt")
    ax.legend()
    ax.set_xlabel("L")
    ax.set_ylabel("Q / MP")
    st.pyplot(fig)

# NÁKLADY
with tabs[1]:
    fig, ax = plt.subplots(figsize=(8,5))
    ax.plot(Q, TC, label="TC")
    ax.plot(Q, VC, label="VC")
    ax.plot(Q, FC*np.ones_like(Q), label="FC")
    ax.set_title("Nákladové křivky")
    ax.legend()
    ax.set_xlabel("Q")
    st.pyplot(fig)

# PRŮMĚRNÉ NÁKLADY
with tabs[2]:
    fig, ax = plt.subplots(figsize=(8,5))
    ax.plot(Q, AC, label="AC")
    ax.plot(Q, AVC, label="AVC")
    ax.plot(Q, AFC, label="AFC")
    ax.set_title("Průměrné náklady")
    ax.legend()
    ax.set_xlabel("Q")
    st.pyplot(fig)

# MC A MR – OPTIMUM FIRMY
with tabs[3]:
    fig, ax = plt.subplots(figsize=(8,5))
    ax.plot(Q, MC, label="MC", color="red")
    ax.plot(Q, MR, label="MR = P", color="blue")
    ax.axvline(Q_opt, linestyle="--", color="green", label=f"Q* = {Q_opt:.1f}")
    ax.set_title("Mezní náklady a mezní příjem – optimum firmy")
    ax.legend()
    ax.set_xlabel("Q")
    st.pyplot(fig)

# PROFIT
with tabs[4]:
    fig, ax = plt.subplots(figsize=(8,5))
    ax.plot(Q, profit, label="Profit π(Q)", color="purple")
    ax.axhline(0, color="black", linewidth=1)
    ax.axvline(Q_opt, linestyle="--", color="green", label=f"Q* = {Q_opt:.1f}")
    ax.set_title("Zisk firmy")
    ax.legend()
    ax.set_xlabel("Q")
    st.pyplot(fig)

st.markdown("---")
st.markdown("Aplikaci vytvořil **Tomáš Paleta** – kompletní mikroekonomická simulace firmy.")

