
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

# ─── Asset definitions ────────────────────────────────────────────────────────
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
    "💶 EUR/CZK":                       {"ticker": "EURCZK=X",   "since": 2003, "category": "Měny",       "currency": "CZK"},
    "💵 USD/CZK":                       {"ticker": "USDCZK=X",   "since": 2003, "category": "Měny",       "currency": "CZK"},
    "📊 Dluhopisy USA (10Y)":           {"ticker": "TLT",        "since": 2002, "category": "Dluhopisy",  "currency": "USD"},
    "🏦 Dluhopisy EM":                  {"ticker": "EMB",        "since": 2007, "category": "Dluhopisy",  "currency": "USD"},
}

CURRENT_YEAR = datetime.now().year
TODAY = date.today()

# ─── Data fetching ────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def fetch_series(ticker, start_date, end_date):
    try:
        df = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=True)
        if df.empty:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        s = df["Close"].dropna()
        s.index = pd.to_datetime(s.index)
        s = s[~s.index.duplicated(keep="first")]
        return s
    except Exception:
        return None

def build_daily_series(raw_series, date_index):
    """Reindex a price series to business day index, forward-fill gaps."""
    if raw_series is None or raw_series.empty:
        return pd.Series(np.nan, index=date_index)
    s = raw_series.reindex(date_index, method="ffill")
    return s.ffill().bfill()

# ─── Core simulation ──────────────────────────────────────────────────────────
def compute_portfolio_history(allocations, investments, end_date):
    """
    Správná logika:
    - Při nákupu: CZK → USD/CZK podle historického kurzu v den nákupu → počet jednotek
    - Hodnota portfolia každý den: jednotky × cena daného dne (v USD nebo CZK dle aktiva)
      → vše přepočteme do USD → na konci (nebo v den prodeje) přepočteme do CZK/EUR
    - invested_czk = suma skutečně zadaných CZK (konstantní po každém nákupu, nemění se s kurzem)
    """
    if not allocations or not investments:
        return None

    start_date = min(inv["date"] for inv in investments)
    fetch_start = (start_date - timedelta(days=30)).strftime("%Y-%m-%d")
    fetch_end   = (end_date + timedelta(days=5)).strftime("%Y-%m-%d")

    # Fetch asset prices
    prices = {}
    for asset in allocations:
        info = ASSETS[asset]
        s = fetch_series(info["ticker"], fetch_start, fetch_end)
        if s is not None:
            prices[asset] = s

    if not prices:
        return None

    # Fetch FX
    usdczk_raw = fetch_series("USDCZK=X", fetch_start, fetch_end)
    eurczk_raw = fetch_series("EURCZK=X", fetch_start, fetch_end)
    eurusd_raw = fetch_series("EURUSD=X", fetch_start, fetch_end)

    # Build date index
    all_dates = pd.date_range(start=start_date, end=end_date, freq="B")

    # Build aligned DataFrames
    price_df = pd.DataFrame(index=all_dates)
    for asset, s in prices.items():
        price_df[asset] = build_daily_series(s, all_dates)

    usdczk = build_daily_series(usdczk_raw, all_dates)
    eurczk = build_daily_series(eurczk_raw, all_dates)
    eurusd = build_daily_series(eurusd_raw, all_dates)

    # Holdings: počet nakoupených jednotek pro každé aktivum
    holdings = {asset: 0.0 for asset in allocations}
    # Kumulativní vloženo v CZK (skutečná zadaná hodnota, nemění se s kurzem)
    invested_czk_cumul = 0.0
    processed = set()

    records = []
    for day in all_dates:
        # Zpracuj investice v tento obchodní den
        for i, inv in enumerate(investments):
            if i in processed:
                continue
            inv_ts = pd.Timestamp(inv["date"])
            if inv_ts <= day:
                amount_czk = inv["amount_czk"]
                fx_buy = float(usdczk.loc[day]) if not pd.isna(usdczk.loc[day]) else 25.0
                # amount_usd = CZK / USDCZK (kolik USD dostaneme za CZK)
                amount_usd = amount_czk / fx_buy

                for asset, weight in allocations.items():
                    if weight <= 0:
                        continue
                    if asset not in price_df.columns or pd.isna(price_df.loc[day, asset]):
                        continue
                    price = float(price_df.loc[day, asset])
                    if price <= 0:
                        continue
                    asset_info = ASSETS[asset]
                    if asset_info["currency"] == "CZK":
                        # Aktivum denominováno v CZK – nakupujeme za CZK přímo
                        amount_for_asset = amount_czk * weight
                        units = amount_for_asset / price
                    else:
                        # Aktivum denominováno v USD
                        amount_for_asset = amount_usd * weight
                        units = amount_for_asset / price
                    holdings[asset] += units

                invested_czk_cumul += amount_czk
                processed.add(i)

        # Hodnota portfolia v USD (všechna USD aktiva)
        total_usd = 0.0
        total_czk_assets = 0.0  # hodnota CZK aktiv

        for asset, units in holdings.items():
            if units == 0:
                continue
            if asset not in price_df.columns or pd.isna(price_df.loc[day, asset]):
                continue
            price = float(price_df.loc[day, asset])
            asset_info = ASSETS[asset]
            if asset_info["currency"] == "CZK":
                total_czk_assets += units * price
            else:
                total_usd += units * price

        # Přepočet: vše do CZK pomocí DNEŠNÍHO kurzu (kurzu v daný den simulace)
        fx_day = float(usdczk.loc[day]) if not pd.isna(usdczk.loc[day]) else 25.0
        fx_eurusd_day = float(eurusd.loc[day]) if not pd.isna(eurusd.loc[day]) else 0.93

        total_czk = total_usd * fx_day + total_czk_assets
        total_eur = (total_usd * fx_eurusd_day) + (total_czk_assets / (fx_day / fx_eurusd_day)) if fx_day > 0 else 0
        # total_usd celkem (včetně CZK aktiv přepočtených)
        total_usd_all = total_usd + (total_czk_assets / fx_day if fx_day > 0 else 0)

        records.append({
            "date": day,
            "total_czk": total_czk,
            "total_usd": total_usd_all,
            "total_eur": total_eur,
            "invested_czk": invested_czk_cumul,   # skutečně vloženo v CZK – konstantní
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
    regular_amount = 0
    regular_freq = "Měsíčně"
    if regular_enabled:
        regular_amount = st.number_input(
            "Pravidelná částka (CZK)", min_value=100, max_value=1_000_000,
            value=5000, step=500, format="%d"
        )
        regular_freq = st.selectbox("Frekvence", ["Měsíčně", "Čtvrtletně", "Ročně"])

    st.subheader("📤 Datum prodeje portfolia")
    sell_mode = st.checkbox("Nastavit datum prodeje (jinak = dnes)", value=False)
    sell_date = TODAY
    if sell_mode:
        start_year_val = CURRENT_YEAR - investment_years_ago
        min_sell = date(start_year_val, 2, 1)
        sell_date = st.date_input(
            "Datum prodeje",
            value=TODAY,
            min_value=min_sell,
            max_value=TODAY
        )

    st.subheader("🗂️ Složení portfolia")
    st.caption("Součet vah musí být 100 %")

    start_year = CURRENT_YEAR - investment_years_ago
    available_assets = {k: v for k, v in ASSETS.items() if v["since"] <= start_year + 2}
    cat_list = sorted(set(v["category"] for v in available_assets.values()))

    weights_input = {asset_name: 0 for asset_name in available_assets}

    with st.form("portfolio_form"):
        st.markdown("**Nastavte váhy aktiv (%):**")
        for cat in cat_list:
            st.markdown(f"*{cat}*")
            for asset_name, info in available_assets.items():
                if info["category"] == cat:
                    weights_input[asset_name] = st.slider(
                        asset_name, 0, 100, 0, 1, key=f"w_{asset_name}"
                    )

        total_weight = sum(weights_input.values())
        if total_weight > 0:
            st.metric(
                "Součet vah", f"{total_weight} %",
                delta=f"{total_weight - 100} %" if total_weight != 100 else "✅ OK"
            )

        submitted = st.form_submit_button("🚀 Spočítat výkonnost", type="primary")


# ─── LANDING PAGE ─────────────────────────────────────────────────────────────
if not submitted:
    st.info("👈 Nastavte portfolio v postranním panelu a klikněte na **Spočítat výkonnost**.")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
### Jak aplikace funguje
1. Zvolte, před kolika lety jste začali investovat
2. Zadejte počáteční a případně pravidelné investice v CZK
3. Volitelně nastavte datum prodeje portfolia
4. Nastavte váhy aktiv (musí dávat 100 %)
5. Klikněte na **Spočítat výkonnost**
""")
    with col2:
        st.markdown("""
### Dostupná aktiva
- 🇺🇸 Akcie USA (S&P 500), MSCI World
- 🇪🇺 Evropské akcie (Euro Stoxx, DAX)
- 🇨🇿 Česká burza (PX index)
- 🪙 Zlato, 🥈 Stříbro, 🛢️ Ropa
- ₿ Bitcoin (od 2014), 🔷 Ethereum (od 2016)
- 💶 EUR/CZK, 💵 USD/CZK
- 📊 Dluhopisy USA & Emerging Markets
""")
    with col3:
        st.markdown("""
### Výstupy
- 📈 Graf vývoje hodnoty portfolia
- 💹 Výnos v CZK, USD a EUR
- 📊 Roční výnosy (bar chart)
- 🥧 Složení portfolia
- 📋 Měsíční tabulka ke stažení jako CSV
""")
    st.stop()

# ─── VALIDATION ───────────────────────────────────────────────────────────────
total_weight = sum(weights_input.values())
if total_weight == 0:
    st.error("❌ Nastavte váhy aktiv (součet musí být > 0).")
    st.stop()
if total_weight != 100:
    st.warning(f"⚠️ Součet vah je {total_weight} %. Váhy budou automaticky normalizovány.")

allocations = {asset: w / total_weight for asset, w in weights_input.items() if w > 0}

# ─── BUILD INVESTMENT SCHEDULE ────────────────────────────────────────────────
start_date = date(CURRENT_YEAR - investment_years_ago, 1, 2)
investments = [{"date": start_date, "amount_czk": float(initial_amount)}]

if regular_enabled and regular_amount > 0:
    freq_map = {"Měsíčně": 1, "Čtvrtletně": 3, "Ročně": 12}
    months_step = freq_map[regular_freq]
    current = start_date
    while True:
        month = current.month + months_step
        year = current.year + (month - 1) // 12
        month = ((month - 1) % 12) + 1
        try:
            current = date(year, month, current.day)
        except ValueError:
            current = date(year, month, 1)
        if current >= sell_date:
            break
        investments.append({"date": current, "amount_czk": float(regular_amount)})

total_invested_czk = sum(i["amount_czk"] for i in investments)

# ─── RUN SIMULATION ───────────────────────────────────────────────────────────
with st.spinner("⏳ Stahuji historická data a počítám výkonnost portfolia..."):
    result_df = compute_portfolio_history(allocations, investments, end_date=sell_date)

if result_df is None or result_df.empty:
    st.error("❌ Nepodařilo se načíst data. Zkontrolujte výběr aktiv a zkuste to znovu.")
    st.stop()

# ─── METRICS ──────────────────────────────────────────────────────────────────
final = result_df.iloc[-1]
final_czk = final["total_czk"]
final_usd = final["total_usd"]
final_eur = final["total_eur"]

gain_czk = final_czk - total_invested_czk
gain_pct = (gain_czk / total_invested_czk * 100) if total_invested_czk > 0 else 0
years_elapsed = (result_df.index[-1] - result_df.index[0]).days / 365.25
cagr = ((final_czk / total_invested_czk) ** (1 / years_elapsed) - 1) * 100 if years_elapsed > 0 and total_invested_czk > 0 else 0

sell_label = f"ke dni {sell_date.strftime('%d.%m.%Y')}" if sell_mode else "dnes"
st.markdown(f"## 📊 Výsledky — portfolio {sell_label}")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("💰 Celkem vloženo", f"{total_invested_czk:,.0f} Kč")
col2.metric("📈 Hodnota (CZK)", f"{final_czk:,.0f} Kč", delta=f"{gain_czk:+,.0f} Kč")
col3.metric("💵 Hodnota (USD)", f"${final_usd:,.0f}")
col4.metric("💶 Hodnota (EUR)", f"€{final_eur:,.0f}")
col5.metric("📊 CAGR", f"{cagr:.1f} % p.a.", delta=f"Celkem {gain_pct:.1f} %")

st.markdown("---")

# ─── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📈 Vývoj portfolia", "📅 Roční výnosy", "🥧 Složení portfolia", "📋 Data"])

with tab1:
    currency = st.radio("Zobrazit v měně:", ["CZK", "USD", "EUR"], horizontal=True)
    col_map = {"CZK": ("total_czk", "Kč"), "USD": ("total_usd", "$"), "EUR": ("total_eur", "€")}
    col_name, sym = col_map[currency]

    # Přepočet invested na zvolenou měnu pro graf
    if col_name == "total_czk":
        inv_series = result_df["invested_czk"]
    elif col_name == "total_usd":
        inv_series = result_df["invested_czk"] / (result_df["total_czk"] / result_df["total_usd"].replace(0, np.nan))
    else:
        inv_series = result_df["invested_czk"] / (result_df["total_czk"] / result_df["total_eur"].replace(0, np.nan))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=result_df.index, y=result_df[col_name],
        name="Hodnota portfolia",
        line=dict(width=2.5),
        fill="tozeroy", fillcolor="rgba(99,110,250,0.1)",
        hovertemplate=f"Datum: %{{x|%d.%m.%Y}}<br>Hodnota: %{{y:,.0f}} {sym}<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=result_df.index, y=inv_series,
        name="Celkem vloženo",
        line=dict(width=1.5, dash="dash", color="orange"),
        hovertemplate=f"Vloženo: %{{y:,.0f}} {sym}<extra></extra>"
    ))
    fig.update_layout(
        title=f"Vývoj hodnoty portfolia ({currency})",
        xaxis_title="Datum", yaxis_title=f"Hodnota ({sym})",
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5),
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    annual = result_df["total_czk"].resample("YE").last()
    annual_returns = annual.pct_change().dropna() * 100
    colors = ["green" if v >= 0 else "crimson" for v in annual_returns.values]

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=annual_returns.index.year, y=annual_returns.values,
        marker_color=colors,
        hovertemplate="Rok %{x}: %{y:.1f} %<extra></extra>"
    ))
    fig2.add_hline(y=0, line_color="gray", line_width=1)
    fig2.update_layout(
        title="Roční výnosy portfolia (%)",
        xaxis_title="Rok", yaxis_title="Výnos (%)"
    )
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    labels = list(allocations.keys())
    values = [allocations[a] * 100 for a in labels]
    fig3 = px.pie(names=labels, values=values, title="Složení portfolia (váhy aktiv)")
    fig3.update_traces(textposition="inside", textinfo="percent+label")
    fig3.update_layout(
        uniformtext_minsize=12, uniformtext_mode="hide",
        legend=dict(orientation="v", x=1.05)
    )
    st.plotly_chart(fig3, use_container_width=True)

with tab4:
    st.subheader("Detailní data (měsíčně)")
    monthly = result_df.resample("ME").last().copy()
    monthly.index = monthly.index.strftime("%Y-%m")

    monthly["Hodnota CZK"]  = monthly["total_czk"].map("{:,.0f} Kč".format)
    monthly["Hodnota USD"]  = monthly["total_usd"].map("${:,.0f}".format)
    monthly["Hodnota EUR"]  = monthly["total_eur"].map("€{:,.0f}".format)
    # ← OPRAVA: vloženo = skutečná kumulativní CZK hodnota, ne přepočet kurzem
    monthly["Vloženo CZK"]  = monthly["invested_czk"].map("{:,.0f} Kč".format)
    monthly["Výnos CZK"]    = (monthly["total_czk"] - monthly["invested_czk"]).map("{:+,.0f} Kč".format)
    monthly["Výnos %"]      = ((monthly["total_czk"] / monthly["invested_czk"] - 1) * 100).map("{:+.1f} %".format)

    st.dataframe(
        monthly[["Hodnota CZK", "Hodnota USD", "Hodnota EUR", "Vloženo CZK", "Výnos CZK", "Výnos %"]],
        use_container_width=True
    )

    csv = result_df.copy()
    csv.index = csv.index.strftime("%Y-%m-%d")
    st.download_button(
        "⬇️ Stáhnout data (CSV)", data=csv.to_csv(),
        file_name="portfolio_history.csv", mime="text/csv"
    )

st.markdown("---")
st.caption(
    "⚠️ Data pochází ze služby Yahoo Finance (yfinance). "
    "Historická výkonnost nezaručuje budoucí výnosy. "
    "Aplikace slouží pouze pro vzdělávací účely."
)
