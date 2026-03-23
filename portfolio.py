
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import yfinance as yf
from datetime import datetime, date, timedelta
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="Historická výkonnost portfolia", page_icon="📈", layout="wide")
st.title("📈 Historická výkonnost investičního portfolia")
st.markdown("Zjistěte, jak by si vaše investice vedla v minulosti na základě **reálných historických dat**.")

ASSETS = {
    "🇺🇸 S&P 500 (USA)":              {"ticker": "SPY",        "since": 1993, "category": "Akcie",      "currency": "USD"},
    "🌍 MSCI World":                   {"ticker": "URTH",       "since": 2012, "category": "Akcie",      "currency": "USD"},
    "🇪🇺 Euro Stoxx 50 (záp. Evropa)": {"ticker": "FEZ",        "since": 2002, "category": "Akcie",      "currency": "USD"},
    "🇩🇪 DAX (Německo)":               {"ticker": "EWG",        "since": 1996, "category": "Akcie",      "currency": "USD"},
    "🇨🇿 PX Praha (ČR)":               {"ticker": "BPrague.PR", "since": 2002, "category": "Akcie",      "currency": "CZK"},
    "🇨🇳 MSCI Emerging Markets":       {"ticker": "EEM",        "since": 2003, "category": "Akcie",      "currency": "USD"},
    "🏠 Nemovitosti (REITs USA)":       {"ticker": "VNQ",        "since": 2004, "category": "Akcie",      "currency": "USD"},
    "🪙 Zlato":                         {"ticker": "GLD",        "since": 2004, "category": "Drahé kovy", "currency": "USD"},
    "🥈 Stříbro":                       {"ticker": "SLV",        "since": 2006, "category": "Drahé kovy", "currency": "USD"},
    "🛢️ Ropa (WTI)":                   {"ticker": "USO",        "since": 2006, "category": "Komodity",   "currency": "USD"},
    "₿ Bitcoin":                        {"ticker": "BTC-USD",    "since": 2014, "category": "Krypto",     "currency": "USD"},
    "🔷 Ethereum":                      {"ticker": "ETH-USD",    "since": 2016, "category": "Krypto",     "currency": "USD"},
    "📊 Dluhopisy USA (10Y)":           {"ticker": "TLT",        "since": 2002, "category": "Dluhopisy",  "currency": "USD"},
    "🏦 Dluhopisy EM":                  {"ticker": "EMB",        "since": 2007, "category": "Dluhopisy",  "currency": "USD"},
}

CURRENT_YEAR = datetime.now().year
TODAY = date.today()

@st.cache_data(ttl=3600)
def fetch_series(ticker, start_str, end_str):
    try:
        df = yf.download(ticker, start=start_str, end=end_str, progress=False, auto_adjust=True)
        if df.empty:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        s = df["Close"].dropna()
        s.index = pd.to_datetime(s.index).tz_localize(None)
        s = s[~s.index.duplicated(keep="first")]
        return s
    except Exception:
        return None

def align(series, idx):
    if series is None or series.empty:
        return pd.Series(np.nan, index=idx)
    return series.reindex(idx, method="ffill").ffill().bfill()

def compute_portfolio(allocations, investments, end_date):
    """
    Simulace portfolia:
    - Nákup: CZK částka se převede na měnu aktiva v den nákupu
    - Hodnota každý den = počet jednotek × cena daného dne v měně aktiva
    - Vše se převede do CZK pomocí kurzu daného dne
    - invested_czk = fixní součet skutečně zadaných CZK (nemění se)
    - Konverze: USD aktiva přes USDCZK, CZK aktiva přímo
    """
    start_date = min(inv["date"] for inv in investments)
    s0 = (start_date - timedelta(days=30)).strftime("%Y-%m-%d")
    s1 = (end_date + timedelta(days=5)).strftime("%Y-%m-%d")

    # Stáhnout ceny aktiv
    prices_raw = {}
    for asset in allocations:
        s = fetch_series(ASSETS[asset]["ticker"], s0, s1)
        if s is not None:
            prices_raw[asset] = s

    if not prices_raw:
        return None

    # Stáhnout FX
    usdczk_raw = fetch_series("USDCZK=X", s0, s1)
    eurczk_raw = fetch_series("EURCZK=X", s0, s1)

    # Obchodní dny
    idx = pd.date_range(start=start_date, end=end_date, freq="B")

    # Zarovnat série
    price_df = pd.DataFrame({a: align(s, idx) for a, s in prices_raw.items()})
    usdczk   = align(usdczk_raw, idx)
    eurczk   = align(eurczk_raw, idx)

    # Simulace
    holdings = {a: 0.0 for a in allocations}  # počet jednotek
    invested_czk = 0.0   # skutečně zadaných CZK – konstantní po nákupu
    processed = set()
    records = []

    for day in idx:
        # Zpracuj nákupy
        for i, inv in enumerate(investments):
            if i in processed:
                continue
            if pd.Timestamp(inv["date"]) <= day:
                amt_czk = float(inv["amount_czk"])
                fx = float(usdczk.loc[day]) if not np.isnan(usdczk.loc[day]) else 25.0
                for asset, weight in allocations.items():
                    if asset not in price_df.columns:
                        continue
                    price = float(price_df.loc[day, asset])
                    if np.isnan(price) or price <= 0:
                        continue
                    allocated_czk = amt_czk * weight
                    if ASSETS[asset]["currency"] == "USD":
                        allocated_native = allocated_czk / fx   # CZK → USD
                    else:
                        allocated_native = allocated_czk        # zůstává CZK
                    holdings[asset] += allocated_native / price
                invested_czk += amt_czk
                processed.add(i)

        # Hodnota portfolia v CZK
        fx_today = float(usdczk.loc[day]) if not np.isnan(usdczk.loc[day]) else 25.0
        eur_today = float(eurczk.loc[day]) if not np.isnan(eurczk.loc[day]) else 25.0

        val_czk = 0.0
        for asset, units in holdings.items():
            if units == 0 or asset not in price_df.columns:
                continue
            price = float(price_df.loc[day, asset])
            if np.isnan(price):
                continue
            if ASSETS[asset]["currency"] == "USD":
                val_czk += units * price * fx_today   # USD → CZK dnešním kurzem
            else:
                val_czk += units * price              # CZK aktiva přímo

        val_usd = val_czk / fx_today if fx_today > 0 else 0.0
        val_eur = val_czk / eur_today if eur_today > 0 else 0.0

        records.append({
            "date":         day,
            "total_czk":    val_czk,
            "total_usd":    val_usd,
            "total_eur":    val_eur,
            "invested_czk": invested_czk,  # ← fixní CZK, nemění se s kurzem
        })

    return pd.DataFrame(records).set_index("date")


# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Nastavení portfolia")

    st.subheader("💰 Počáteční investice")
    investment_years_ago = st.selectbox(
        "Kdy jste začali investovat?",
        options=[5, 10, 15, 20, 30],
        format_func=lambda x: f"Před {x} lety ({CURRENT_YEAR - x})"
    )
    initial_amount = st.number_input(
        "Počáteční částka (CZK)", min_value=1000, max_value=10_000_000,
        value=100_000, step=1000, format="%d"
    )

    st.subheader("📅 Pravidelné investice")
    regular_enabled = st.checkbox("Přidat pravidelné investice", value=False)
    regular_amount, regular_freq = 0, "Měsíčně"
    if regular_enabled:
        regular_amount = st.number_input(
            "Pravidelná částka (CZK)", min_value=100, max_value=1_000_000,
            value=5000, step=500, format="%d"
        )
        regular_freq = st.selectbox("Frekvence", ["Měsíčně", "Čtvrtletně", "Ročně"])

    st.subheader("📤 Datum prodeje")
    sell_mode = st.checkbox("Nastavit datum prodeje (jinak = dnes)", value=False)
    sell_date = TODAY
    if sell_mode:
        min_sell = date(CURRENT_YEAR - investment_years_ago, 2, 1)
        sell_date = st.date_input("Datum prodeje", value=TODAY, min_value=min_sell, max_value=TODAY)

    st.subheader("🗂️ Složení portfolia")
    st.caption("Součet vah musí být 100 %")

    start_year = CURRENT_YEAR - investment_years_ago
    available_assets = {k: v for k, v in ASSETS.items() if v["since"] <= start_year + 2}
    cat_list = sorted(set(v["category"] for v in available_assets.values()))
    weights_input = {a: 0 for a in available_assets}

    with st.form("portfolio_form"):
        st.markdown("**Nastavte váhy aktiv (%):**")
        for cat in cat_list:
            st.markdown(f"*{cat}*")
            for aname, info in available_assets.items():
                if info["category"] == cat:
                    weights_input[aname] = st.slider(aname, 0, 100, 0, 1, key=f"w_{aname}")

        tw = sum(weights_input.values())
        if tw > 0:
            st.metric("Součet vah", f"{tw} %", delta=f"{tw-100} %" if tw != 100 else "✅ OK")

        submitted = st.form_submit_button("🚀 Spočítat výkonnost", type="primary")


# ─── LANDING ──────────────────────────────────────────────────────────────────
if not submitted:
    st.info("👈 Nastavte portfolio v postranním panelu a klikněte na **Spočítat výkonnost**.")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
### Jak aplikace funguje
1. Zvolte, před kolika lety jste začali investovat
2. Zadejte počáteční a případně pravidelné investice v CZK
3. Volitelně nastavte datum prodeje portfolia
4. Nastavte váhy aktiv (musí dávat 100 %)
5. Klikněte na **Spočítat výkonnost**
""")
    with c2:
        st.markdown("""
### Dostupná aktiva
- 🇺🇸 Akcie USA (S&P 500), MSCI World
- 🇪🇺 Evropské akcie (Euro Stoxx, DAX)
- 🇨🇿 Česká burza (PX index)
- 🪙 Zlato, 🥈 Stříbro, 🛢️ Ropa
- ₿ Bitcoin (od 2014), 🔷 Ethereum (od 2016)
- 📊 Dluhopisy USA & Emerging Markets
""")
    with c3:
        st.markdown("""
### Výstupy
- 📈 Graf vývoje hodnoty portfolia v CZK
- 💹 Výnos v CZK, USD a EUR
- 📊 Roční výnosy (bar chart)
- 🥧 Složení portfolia
- 📋 Měsíční tabulka ke stažení jako CSV
""")
    st.stop()

# ─── VALIDATE ─────────────────────────────────────────────────────────────────
tw = sum(weights_input.values())
if tw == 0:
    st.error("❌ Nastavte váhy aktiv.")
    st.stop()
if tw != 100:
    st.warning(f"⚠️ Součet vah je {tw} %. Váhy budou normalizovány.")

allocations = {a: w / tw for a, w in weights_input.items() if w > 0}

# ─── INVESTMENT SCHEDULE ──────────────────────────────────────────────────────
start_date = date(CURRENT_YEAR - investment_years_ago, 1, 2)
investments = [{"date": start_date, "amount_czk": float(initial_amount)}]

if regular_enabled and regular_amount > 0:
    freq_map = {"Měsíčně": 1, "Čtvrtletně": 3, "Ročně": 12}
    step = freq_map[regular_freq]
    cur = start_date
    while True:
        m = cur.month + step
        y = cur.year + (m - 1) // 12
        m = ((m - 1) % 12) + 1
        try:
            cur = date(y, m, cur.day)
        except ValueError:
            cur = date(y, m, 1)
        if cur >= sell_date:
            break
        investments.append({"date": cur, "amount_czk": float(regular_amount)})

total_invested_czk = sum(i["amount_czk"] for i in investments)

# ─── SIMULATE ─────────────────────────────────────────────────────────────────
with st.spinner("⏳ Stahuji historická data a počítám výkonnost..."):
    result_df = compute_portfolio(allocations, investments, sell_date)

if result_df is None or result_df.empty:
    st.error("❌ Nepodařilo se načíst data.")
    st.stop()

# ─── METRICS ──────────────────────────────────────────────────────────────────
final = result_df.iloc[-1]
gain_czk = final["total_czk"] - total_invested_czk
gain_pct = gain_czk / total_invested_czk * 100 if total_invested_czk > 0 else 0
yrs = (result_df.index[-1] - result_df.index[0]).days / 365.25
cagr = ((final["total_czk"] / total_invested_czk) ** (1 / yrs) - 1) * 100 if yrs > 0 else 0

sell_label = f"ke dni {sell_date.strftime('%d.%m.%Y')}" if sell_mode else "dnes"
st.markdown(f"## 📊 Výsledky — portfolio {sell_label}")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("💰 Celkem vloženo", f"{total_invested_czk:,.0f} Kč")
c2.metric("📈 Hodnota (CZK)", f"{final['total_czk']:,.0f} Kč", delta=f"{gain_czk:+,.0f} Kč")
c3.metric("💵 Hodnota (USD)", f"${final['total_usd']:,.0f}")
c4.metric("💶 Hodnota (EUR)", f"€{final['total_eur']:,.0f}")
c5.metric("📊 CAGR", f"{cagr:.1f} % p.a.", delta=f"Celkem {gain_pct:.1f} %")

st.markdown("---")

# ─── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📈 Vývoj portfolia", "📅 Roční výnosy", "🥧 Složení portfolia", "📋 Data"])

with tab1:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=result_df.index, y=result_df["total_czk"],
        name="Hodnota portfolia",
        line=dict(width=2.5),
        fill="tozeroy", fillcolor="rgba(99,110,250,0.1)",
        hovertemplate="Datum: %{x|%d.%m.%Y}<br>Hodnota: %{y:,.0f} Kč<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=result_df.index, y=result_df["invested_czk"],
        name="Celkem vloženo",
        line=dict(width=1.5, dash="dash", color="orange"),
        hovertemplate="Vloženo: %{y:,.0f} Kč<extra></extra>"
    ))
    fig.update_layout(
        title="Vývoj hodnoty portfolia (CZK)",
        xaxis_title="Datum", yaxis_title="Hodnota (Kč)",
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5),
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.info(
        f"📌 Hodnota portfolia je v CZK. USD a EUR hodnoty ke konci: "
        f"**${final['total_usd']:,.0f}** / **€{final['total_eur']:,.0f}**"
    )

with tab2:
    annual = result_df["total_czk"].resample("YE").last().pct_change().dropna() * 100
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=annual.index.year, y=annual.values,
        marker_color=["green" if v >= 0 else "crimson" for v in annual.values],
        hovertemplate="Rok %{x}: %{y:.1f} %<extra></extra>"
    ))
    fig2.add_hline(y=0, line_color="gray", line_width=1)
    fig2.update_layout(title="Roční výnosy portfolia (%)", xaxis_title="Rok", yaxis_title="Výnos (%)")
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    labels = list(allocations.keys())
    values = [allocations[a] * 100 for a in labels]
    fig3 = px.pie(names=labels, values=values, title="Složení portfolia")
    fig3.update_traces(textposition="inside", textinfo="percent+label")
    fig3.update_layout(uniformtext_minsize=12, uniformtext_mode="hide", legend=dict(orientation="v", x=1.05))
    st.plotly_chart(fig3, use_container_width=True)

with tab4:
    st.subheader("Detailní data (měsíčně)")
    monthly = result_df.resample("ME").last().copy()
    monthly.index = monthly.index.strftime("%Y-%m")
    monthly["Hodnota CZK"] = monthly["total_czk"].map("{:,.0f} Kč".format)
    monthly["Hodnota USD"] = monthly["total_usd"].map("${:,.0f}".format)
    monthly["Hodnota EUR"] = monthly["total_eur"].map("€{:,.0f}".format)
    monthly["Vloženo CZK"] = monthly["invested_czk"].map("{:,.0f} Kč".format)
    monthly["Výnos CZK"]   = (monthly["total_czk"] - monthly["invested_czk"]).map("{:+,.0f} Kč".format)
    monthly["Výnos %"]     = ((monthly["total_czk"] / monthly["invested_czk"] - 1) * 100).map("{:+.1f} %".format)
    st.dataframe(monthly[["Hodnota CZK","Hodnota USD","Hodnota EUR","Vloženo CZK","Výnos CZK","Výnos %"]], use_container_width=True)

    out = result_df.copy()
    out.index = out.index.strftime("%Y-%m-%d")
    st.download_button("⬇️ Stáhnout data (CSV)", data=out.to_csv(), file_name="portfolio_history.csv", mime="text/csv")

st.markdown("---")
st.caption("⚠️ Data pochází ze služby Yahoo Finance. Historická výkonnost nezaručuje budoucí výnosy. Pouze pro vzdělávací účely.")
# Dynamický copyright v patičce
import datetime
current_year = datetime.datetime.now().year
st.markdown(f"<hr style='margin-top:2em;margin-bottom:0.5em;'>", unsafe_allow_html=True)
st.markdown(f"<div style='text-align:center; color:gray; font-size:0.95em;'>© {current_year} Tomáš Paleta, Masarykova univerzita, Ekonomicko-správní fakulta, Brno</div>", unsafe_allow_html=True)
