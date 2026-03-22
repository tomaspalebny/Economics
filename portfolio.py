
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
    "🇺🇸 S&P 500 (USA)": {"ticker": "SPY", "since": 1993, "category": "Akcie"},
    "🌍 MSCI World": {"ticker": "URTH", "since": 2012, "category": "Akcie"},
    "🇪🇺 Euro Stoxx 50 (záp. Evropa)": {"ticker": "FEZ", "since": 2002, "category": "Akcie"},
    "🇩🇪 DAX (Německo)": {"ticker": "EWG", "since": 1996, "category": "Akcie"},
    "🇨🇿 PX Praha (ČR)": {"ticker": "BPrague.PR", "since": 2002, "category": "Akcie"},
    "🇨🇳 MSCI Emerging Markets": {"ticker": "EEM", "since": 2003, "category": "Akcie"},
    "🏠 Nemovitosti (REITs USA)": {"ticker": "VNQ", "since": 2004, "category": "Akcie"},
    "🪙 Zlato": {"ticker": "GLD", "since": 2004, "category": "Drahé kovy"},
    "🥈 Stříbro": {"ticker": "SLV", "since": 2006, "category": "Drahé kovy"},
    "🛢️ Ropa (WTI)": {"ticker": "USO", "since": 2006, "category": "Komodity"},
    "₿ Bitcoin": {"ticker": "BTC-USD", "since": 2014, "category": "Krypto"},
    "🔷 Ethereum": {"ticker": "ETH-USD", "since": 2016, "category": "Krypto"},
    "💶 EUR/CZK": {"ticker": "EURCZK=X", "since": 2003, "category": "Měny"},
    "💵 USD/CZK": {"ticker": "USDCZK=X", "since": 2003, "category": "Měny"},
    "📊 Dluhopisy USA (10Y)": {"ticker": "TLT", "since": 2002, "category": "Dluhopisy"},
    "🏦 Dluhopisy EM": {"ticker": "EMB", "since": 2007, "category": "Dluhopisy"},
}

FX_TICKERS = {
    "USD/CZK": "USDCZK=X",
    "EUR/CZK": "EURCZK=X",
    "EUR/USD": "EURUSD=X",
}

YEARS_OPTIONS = {5: 2021, 10: 2016, 15: 2011, 20: 2006, 30: 1996}
CURRENT_YEAR = datetime.now().year

@st.cache_data(ttl=3600)
def fetch_price(ticker, start_date, end_date):
    try:
        df = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=True)
        if df.empty:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df[["Close"]].dropna()
    except Exception:
        return None

@st.cache_data(ttl=3600)
def fetch_fx(ticker, start_date, end_date):
    try:
        df = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=True)
        if df.empty:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df[["Close"]].dropna()
    except Exception:
        return None

def get_fx_rate(ticker, target_date):
    """Get FX rate closest to a given date."""
    start = target_date - timedelta(days=10)
    end = target_date + timedelta(days=10)
    df = fetch_fx(ticker, start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
    if df is None or df.empty:
        return None
    closest = df.iloc[(df.index - pd.Timestamp(target_date)).abs().argsort()[0]]
    return float(closest["Close"])

def compute_portfolio_history(allocations, investments, end_date_str="today"):
    """
    allocations: dict {asset_name: weight (0-1)}
    investments: list of {"date": date, "amount_czk": float}
    Returns: DataFrame with date index, columns = [total_czk, total_usd, total_eur, invested_czk]
    """
    if not allocations or not investments:
        return None

    end_date = datetime.today() if end_date_str == "today" else datetime.strptime(end_date_str, "%Y-%m-%d")
    start_date = min(inv["date"] for inv in investments)

    # Fetch all asset prices
    prices = {}
    for asset, weight in allocations.items():
        if weight > 0:
            info = ASSETS[asset]
            df = fetch_price(info["ticker"],
                             (start_date - timedelta(days=30)).strftime("%Y-%m-%d"),
                             end_date.strftime("%Y-%m-%d"))
            if df is not None and not df.empty:
                prices[asset] = df["Close"]

    if not prices:
        return None

    # Build common date range (business days)
    all_dates = pd.date_range(start=start_date, end=end_date, freq="B")
    price_df = pd.DataFrame(index=all_dates)
    for asset, series in prices.items():
        series.index = pd.to_datetime(series.index)
        series = series[~series.index.duplicated(keep='first')]
        price_df[asset] = series.reindex(all_dates, method="ffill")
    price_df = price_df.ffill().bfill()

    # Fetch FX series
    fx_usdczk = fetch_fx("USDCZK=X",
                          (start_date - timedelta(days=30)).strftime("%Y-%m-%d"),
                          end_date.strftime("%Y-%m-%d"))
    fx_eurczk = fetch_fx("EURCZK=X",
                          (start_date - timedelta(days=30)).strftime("%Y-%m-%d"),
                          end_date.strftime("%Y-%m-%d"))
    fx_eurusd = fetch_fx("EURUSD=X",
                          (start_date - timedelta(days=30)).strftime("%Y-%m-%d"),
                          end_date.strftime("%Y-%m-%d"))

    def reindex_fx(fx_df):
        if fx_df is None or fx_df.empty:
            return pd.Series(np.nan, index=all_dates)
        s = fx_df["Close"].copy()
        s.index = pd.to_datetime(s.index)
        s = s[~s.index.duplicated(keep='first')]
        return s.reindex(all_dates, method="ffill").ffill().bfill()

    usdczk_series = reindex_fx(fx_usdczk)
    eurczk_series = reindex_fx(fx_eurczk)
    eurusd_series = reindex_fx(fx_eurusd)

    # Simulate portfolio: for each investment, buy units of each asset
    # Store: {asset: number_of_units}
    holdings = {asset: 0.0 for asset in allocations if allocations[asset] > 0}
    invested_cumulative = []
    total_invested = 0.0

    records = []
    for day in all_dates:
        # Process investments on this day
        for inv in investments:
            inv_date = pd.Timestamp(inv["date"])
            if inv_date == day or (inv_date < day and inv_date >= day - timedelta(days=4) and
                                    not any(r["date"] == day for r in records)):
                # Find the nearest available date
                pass
        for inv in investments:
            inv_date = pd.Timestamp(inv["date"])
            # Match investment to trading day
            if (inv_date <= day) and (inv_date > day - pd.tseries.offsets.BDay(5)):
                already_processed = any(
                    inv.get("_processed_on") == day for inv2 in investments for k, v in inv2.items()
                    if k == "_processed_on" and v == day
                )
        total_invested = 0.0  # will calc below

        # Process each investment on the closest business day after investment date
        for inv in investments:
            inv_ts = pd.Timestamp(inv["date"])
            if inv_ts <= day and not inv.get("_processed"):
                # Check if this is the first business day >= inv_ts
                if day >= inv_ts:
                    amount = inv["amount_czk"]
                    # Convert CZK to USD using FX on that day
                    fx = float(usdczk_series.loc[day]) if not pd.isna(usdczk_series.loc[day]) else 25.0
                    amount_usd = amount / fx
                    for asset in holdings:
                        if asset in price_df.columns and not pd.isna(price_df.loc[day, asset]):
                            price = float(price_df.loc[day, asset])
                            if price > 0:
                                units = (amount_usd * allocations[asset]) / price
                                holdings[asset] += units
                    inv["_processed"] = True
                    inv["_processed_day"] = day

        # Calculate portfolio value in USD
        total_usd = 0.0
        for asset, units in holdings.items():
            if asset in price_df.columns and not pd.isna(price_df.loc[day, asset]):
                total_usd += units * float(price_df.loc[day, asset])

        # Convert to CZK and EUR
        fx_uc = float(usdczk_series.loc[day]) if not pd.isna(usdczk_series.loc[day]) else 25.0
        fx_eu = float(eurusd_series.loc[day]) if not pd.isna(eurusd_series.loc[day]) else 0.93
        total_czk = total_usd * fx_uc
        total_eur = total_usd * fx_eu

        # Calculate total invested in CZK
        total_inv = sum(inv["amount_czk"] for inv in investments if inv.get("_processed"))

        records.append({
            "date": day,
            "total_usd": total_usd,
            "total_czk": total_czk,
            "total_eur": total_eur,
            "invested_czk": total_inv,
        })

    result_df = pd.DataFrame(records).set_index("date")
    # Reset processed flags
    for inv in investments:
        inv.pop("_processed", None)
        inv.pop("_processed_day", None)
    return result_df


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

    st.subheader("🗂️ Složení portfolia")
    st.caption("Součet vah musí být 100 %")

    categories = list(set(v["category"] for v in ASSETS.values()))
    selected_assets = {}

    start_year = CURRENT_YEAR - investment_years_ago
    available_assets = {k: v for k, v in ASSETS.items() if v["since"] <= start_year + 2}

    tabs_cat = st.tabs(list(set(v["category"] for v in available_assets.values())))
    cat_list = list(set(v["category"] for v in available_assets.values()))

    weights_input = {}
    for cat in cat_list:
        cat_assets = {k: v for k, v in available_assets.items() if v["category"] == cat}
        for asset_name in cat_assets:
            weights_input[asset_name] = 0

    with st.form("portfolio_form"):
        st.markdown("**Nastavte váhy aktiv (%):**")
        for cat in sorted(cat_list):
            st.markdown(f"*{cat}*")
            cat_assets = {k: v for k, v in available_assets.items() if v["category"] == cat}
            for asset_name in cat_assets:
                weights_input[asset_name] = st.slider(
                    asset_name, 0, 100, 0, 1, key=f"w_{asset_name}"
                )

        total_weight = sum(weights_input.values())
        if total_weight > 0:
            st.metric("Součet vah", f"{total_weight} %",
                      delta=f"{total_weight - 100} %" if total_weight != 100 else "✅ OK")

        submitted = st.form_submit_button("🚀 Spočítat výkonnost", type="primary")

# ─── MAIN CONTENT ─────────────────────────────────────────────────────────────
if not submitted:
    st.info("👈 Nastavte portfolio v postranním panelu a klikněte na **Spočítat výkonnost**.")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        ### Jak aplikace funguje
        1. Zvolte, před kolika lety jste začali investovat
        2. Zadejte počáteční a případně pravidelné investice v CZK
        3. Nastavte váhy jednotlivých aktiv (musí dávat 100 %)
        4. Klikněte na **Spočítat výkonnost**
        """)
    with col2:
        st.markdown("""
        ### Dostupná aktiva
        - 🇺🇸 Akcie USA (S&P 500)
        - 🇪🇺 Evropské akcie (Euro Stoxx, DAX)
        - 🇨🇿 Česká burza (PX)
        - 🪙 Drahé kovy (zlato, stříbro)
        - ₿ Krypto (Bitcoin, Ethereum)
        - 💶 Měny (EUR/CZK, USD/CZK)
        - 📊 Dluhopisy
        """)
    with col3:
        st.markdown("""
        ### Výstupy
        - 📈 Graf vývoje hodnoty portfolia
        - 💹 Výnos v CZK, USD a EUR
        - 📊 Roční výnosy (bar chart)
        - 🥧 Složení portfolia (koláčový graf)
        - 📋 Detailní tabulka výsledků
        """)
    st.stop()

# Validate weights
total_weight = sum(weights_input.values())
allocations = {}
if total_weight == 0:
    st.error("❌ Nastavte váhy aktiv (součet musí být > 0).")
    st.stop()
elif total_weight != 100:
    st.warning(f"⚠️ Součet vah je {total_weight} %. Váhy budou automaticky normalizovány.")

for asset, w in weights_input.items():
    if w > 0:
        allocations[asset] = w / total_weight

# Build investment schedule
start_date = date(CURRENT_YEAR - investment_years_ago, 1, 2)
investments = [{"date": start_date, "amount_czk": float(initial_amount)}]

if regular_enabled and regular_amount > 0:
    freq_map = {"Měsíčně": 1, "Čtvrtletně": 3, "Ročně": 12}
    months_step = freq_map[regular_freq]
    current = start_date
    today = date.today()
    while True:
        month = current.month + months_step
        year = current.year + (month - 1) // 12
        month = ((month - 1) % 12) + 1
        try:
            current = date(year, month, current.day)
        except ValueError:
            current = date(year, month, 1)
        if current >= today:
            break
        investments.append({"date": current, "amount_czk": float(regular_amount)})

total_invested = sum(i["amount_czk"] for i in investments)

with st.spinner("⏳ Stahuji historická data a počítám výkonnost portfolia..."):
    result_df = compute_portfolio_history(allocations, investments)

if result_df is None or result_df.empty:
    st.error("❌ Nepodařilo se načíst data. Zkontrolujte výběr aktiv a zkuste to znovu.")
    st.stop()

# ─── RESULTS ──────────────────────────────────────────────────────────────────
final_row = result_df.iloc[-1]
final_czk = final_row["total_czk"]
final_usd = final_row["total_usd"]
final_eur = final_row["total_eur"]

gain_czk = final_czk - total_invested
gain_pct = (gain_czk / total_invested * 100) if total_invested > 0 else 0

# CAGR
years_elapsed = (result_df.index[-1] - result_df.index[0]).days / 365.25
cagr = ((final_czk / total_invested) ** (1 / years_elapsed) - 1) * 100 if years_elapsed > 0 and total_invested > 0 else 0

st.markdown("## 📊 Výsledky")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("💰 Vloženo (CZK)", f"{total_invested:,.0f} Kč")
col2.metric("📈 Hodnota (CZK)", f"{final_czk:,.0f} Kč", delta=f"{gain_czk:+,.0f} Kč")
col3.metric("💵 Hodnota (USD)", f"${final_usd:,.0f}")
col4.metric("💶 Hodnota (EUR)", f"€{final_eur:,.0f}")
col5.metric("📊 CAGR (roční výnos)", f"{cagr:.1f} % p.a.", delta=f"Celkem {gain_pct:.1f} %")

st.markdown("---")

# ─── CHARTS ───────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📈 Vývoj portfolia", "📅 Roční výnosy", "🥧 Složení portfolia", "📋 Data"])

with tab1:
    currency = st.radio("Zobrazit v měně:", ["CZK", "USD", "EUR"], horizontal=True)
    col_map = {"CZK": ("total_czk", "Kč"), "USD": ("total_usd", "$"), "EUR": ("total_eur", "€")}
    col_name, sym = col_map[currency]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=result_df.index,
        y=result_df[col_name],
        name="Hodnota portfolia",
        line=dict(width=2.5),
        fill="tozeroy",
        fillcolor="rgba(99,110,250,0.1)",
        hovertemplate=f"Datum: %{{x|%d.%m.%Y}}<br>Hodnota: %{{y:,.0f}} {sym}<extra></extra>"
    ))
    # Add invested line
    fig.add_trace(go.Scatter(
        x=result_df.index,
        y=result_df["invested_czk"] * (result_df[col_name] / result_df["total_czk"]) if col_name != "total_czk" else result_df["invested_czk"],
        name="Vloženo",
        line=dict(width=1.5, dash="dash"),
        hovertemplate=f"Vloženo: %{{y:,.0f}} {sym}<extra></extra>"
    ))
    fig.update_layout(
        title=f"Vývoj hodnoty portfolia ({currency})",
        xaxis_title="Datum",
        yaxis_title=f"Hodnota ({sym})",
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5),
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    # Annual returns
    annual = result_df["total_czk"].resample("YE").last()
    annual_returns = annual.pct_change() * 100
    annual_returns = annual_returns.dropna()
    annual_invested = result_df["invested_czk"].resample("YE").last()

    fig2 = go.Figure()
    colors = ["green" if v >= 0 else "red" for v in annual_returns.values]
    fig2.add_trace(go.Bar(
        x=annual_returns.index.year,
        y=annual_returns.values,
        marker_color=colors,
        hovertemplate="Rok %{x}: %{y:.1f} %<extra></extra>"
    ))
    fig2.update_layout(
        title="Roční výnosy portfolia (%)",
        xaxis_title="Rok",
        yaxis_title="Výnos (%)",
    )
    fig2.add_hline(y=0, line_dash="solid", line_color="gray", line_width=1)
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    labels = list(allocations.keys())
    values = [allocations[a] * 100 for a in labels]
    fig3 = px.pie(
        names=labels, values=values,
        title="Složení portfolia (váhy aktiv)"
    )
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
    monthly["Hodnota CZK"] = monthly["total_czk"].map("{:,.0f} Kč".format)
    monthly["Hodnota USD"] = monthly["total_usd"].map("${:,.0f}".format)
    monthly["Hodnota EUR"] = monthly["total_eur"].map("€{:,.0f}".format)
    monthly["Vloženo CZK"] = monthly["invested_czk"].map("{:,.0f} Kč".format)
    monthly["Výnos CZK"] = (monthly["total_czk"] - monthly["invested_czk"]).map("{:+,.0f} Kč".format)
    st.dataframe(
        monthly[["Hodnota CZK", "Hodnota USD", "Hodnota EUR", "Vloženo CZK", "Výnos CZK"]],
        use_container_width=True
    )
    # Download button
    csv = result_df.to_csv()
    st.download_button(
        "⬇️ Stáhnout data (CSV)",
        data=csv,
        file_name="portfolio_history.csv",
        mime="text/csv"
    )

st.markdown("---")
st.caption("⚠️ Data pochází ze služby Yahoo Finance (yfinance). Historická výkonnost nezaručuje budoucí výnosy. "
           "Aplikace slouží pouze pro vzdělávací účely.")
