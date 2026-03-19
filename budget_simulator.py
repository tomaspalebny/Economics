import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Makroekonomický simulátor rozpočtu", layout="wide")
st.title("🏛️ Simulátor státního rozpočtu")
st.markdown("*Interaktivní nástroj pro výuku makroekonomie – 1. ročník VŠ*")

# --- PRESETS ---
# Keys: GDP (mld lokální měna), population (mil), workforce (mil), unemployed (mil),
# pensioners (mil), avg_wage (roční, lokální měna), income_tax_rate (%), employer_social (%),
# employee_social (%), vat_rate (%), corporate_tax (%), pension_avg (roční),
# unemployment_benefit (roční), debt_to_gdp (%), interest_rate (%), gov_other_spending_pct (%),
# health_spending_pct (%), defense_pct (%), education_pct (%), currency
PRESETS = {
    "🇨🇿 Česká republika": dict(
        gdp=7800, pop=10.9, workforce=5.3, unemployed=0.15, pensioners=2.9,
        avg_wage=540000, income_tax_rate=15.0, employer_social=33.8, employee_social=11.0,
        vat_rate=21.0, corporate_tax=21.0, pension_avg=228000, unemployment_benefit=180000,
        debt_to_gdp=43.0, interest_rate=3.5, health_pct=7.5, defense_pct=2.0, education_pct=4.5,
        other_spending_pct=8.0, currency="CZK mld"
    ),
    "🇸🇰 Slovensko": dict(
        gdp=130, pop=5.4, workforce=2.6, unemployed=0.17, pensioners=1.15,
        avg_wage=18000, income_tax_rate=19.0, employer_social=35.2, employee_social=13.4,
        vat_rate=23.0, corporate_tax=21.0, pension_avg=7200, unemployment_benefit=5400,
        debt_to_gdp=62.0, interest_rate=3.2, health_pct=7.0, defense_pct=2.0, education_pct=4.0,
        other_spending_pct=9.0, currency="EUR mld"
    ),
    "🇩🇪 Německo": dict(
        gdp=4260, pop=84.5, workforce=42.0, unemployed=2.7, pensioners=21.0,
        avg_wage=52000, income_tax_rate=30.0, employer_social=20.0, employee_social=20.0,
        vat_rate=19.0, corporate_tax=30.0, pension_avg=19200, unemployment_benefit=14400,
        debt_to_gdp=63.0, interest_rate=2.5, health_pct=9.5, defense_pct=2.0, education_pct=4.5,
        other_spending_pct=8.0, currency="EUR mld"
    ),
    "🇺🇸 USA": dict(
        gdp=28800, pop=335.0, workforce=160.0, unemployed=6.5, pensioners=55.0,
        avg_wage=65000, income_tax_rate=22.0, employer_social=7.65, employee_social=7.65,
        vat_rate=0.0, corporate_tax=21.0, pension_avg=22000, unemployment_benefit=16000,
        debt_to_gdp=124.0, interest_rate=4.5, health_pct=8.5, defense_pct=3.5, education_pct=5.0,
        other_spending_pct=7.0, currency="USD mld"
    ),
    "🇷🇺 Rusko": dict(
        gdp=195000, pop=146.0, workforce=73.0, unemployed=2.8, pensioners=36.0,
        avg_wage=900000, income_tax_rate=13.0, employer_social=30.0, employee_social=0.0,
        vat_rate=22.0, corporate_tax=25.0, pension_avg=252000, unemployment_benefit=144000,
        debt_to_gdp=17.0, interest_rate=8.0, health_pct=3.5, defense_pct=6.0, education_pct=3.5,
        other_spending_pct=10.0, currency="RUB mld"
    ),
    "⚙️ Vlastní": dict(
        gdp=1000, pop=10.0, workforce=5.0, unemployed=0.3, pensioners=2.0,
        avg_wage=30000, income_tax_rate=20.0, employer_social=25.0, employee_social=10.0,
        vat_rate=20.0, corporate_tax=20.0, pension_avg=10000, unemployment_benefit=6000,
        debt_to_gdp=40.0, interest_rate=3.0, health_pct=7.0, defense_pct=2.0, education_pct=4.0,
        other_spending_pct=8.0, currency="jednotek"
    ),
}

# --- SIDEBAR ---
st.sidebar.header("Vyberte preset ekonomiky")
preset_name = st.sidebar.selectbox("Ekonomika", list(PRESETS.keys()))
p = PRESETS[preset_name]
cur = p["currency"]

st.sidebar.markdown("---")
st.sidebar.header("📊 Základní parametry")
gdp = st.sidebar.slider(f"HDP ({cur})", 10.0, 50000.0, float(p["gdp"]), step=10.0)
pop = st.sidebar.slider("Populace (mil)", 1.0, 400.0, p["pop"], step=0.5)
workforce = st.sidebar.slider("Zaměstnaní (mil)", 0.5, 200.0, p["workforce"], step=0.1)
unemployed = st.sidebar.slider("Nezaměstnaní (mil)", 0.0, 30.0, p["unemployed"], step=0.05)
pensioners = st.sidebar.slider("Důchodci (mil)", 0.1, 80.0, p["pensioners"], step=0.1)
avg_wage = st.sidebar.slider("Průměrná roční mzda", 1000.0, 200000.0 if "CZK" not in cur and "RUB" not in cur else 2000000.0, float(p["avg_wage"]), step=1000.0)

st.sidebar.markdown("---")
st.sidebar.header("💰 Daňové sazby")
income_tax = st.sidebar.slider("Daň z příjmů FO (%)", 0.0, 50.0, p["income_tax_rate"], step=0.5)
employer_social = st.sidebar.slider("Odvody zaměstnavatele (%)", 0.0, 50.0, p["employer_social"], step=0.5)
employee_social = st.sidebar.slider("Odvody zaměstnance (%)", 0.0, 30.0, p["employee_social"], step=0.5)
vat_rate = st.sidebar.slider("DPH (%)", 0.0, 30.0, p["vat_rate"], step=0.5)
corporate_tax = st.sidebar.slider("Daň z příjmů PO (%)", 0.0, 40.0, p["corporate_tax"], step=0.5)

st.sidebar.markdown("---")
st.sidebar.header("📤 Výdajové parametry")
pension_avg = st.sidebar.slider("Průměrný roční důchod", 1000.0, 100000.0 if "CZK" not in cur and "RUB" not in cur else 500000.0, float(p["pension_avg"]), step=1000.0)
unemp_benefit = st.sidebar.slider("Roční podpora v nezam.", 1000.0, 50000.0 if "CZK" not in cur and "RUB" not in cur else 400000.0, float(p["unemployment_benefit"]), step=500.0)
health_pct = st.sidebar.slider("Zdravotnictví (% HDP)", 0.0, 15.0, p["health_pct"], step=0.5)
defense_pct = st.sidebar.slider("Obrana (% HDP)", 0.0, 10.0, p["defense_pct"], step=0.5)
education_pct = st.sidebar.slider("Vzdělávání (% HDP)", 0.0, 10.0, p["education_pct"], step=0.5)
other_pct = st.sidebar.slider("Ostatní výdaje (% HDP)", 0.0, 20.0, p["other_spending_pct"], step=0.5)

st.sidebar.markdown("---")
st.sidebar.header("🏦 Státní dluh")
debt_to_gdp = st.sidebar.slider("Dluh/HDP (%)", 0.0, 200.0, p["debt_to_gdp"], step=1.0)
interest_rate = st.sidebar.slider("Úroková sazba dluhu (%)", 0.0, 15.0, p["interest_rate"], step=0.1)

# --- CALCULATIONS ---
# All in billions of local currency
total_wage_bill = workforce * 1e6 * avg_wage / 1e9  # mld

# PŘÍJMY
income_tax_rev = total_wage_bill * (income_tax / 100)
employer_social_rev = total_wage_bill * (employer_social / 100)
employee_social_rev = total_wage_bill * (employee_social / 100)
vat_rev = gdp * (vat_rate / 100) * 0.45  # ~45% of GDP is consumption subject to VAT
corporate_tax_rev = gdp * 0.25 * (corporate_tax / 100)  # ~25% GDP is corporate profit base
other_rev = gdp * 0.02  # excise, property, fees etc ~2% GDP

total_revenue = income_tax_rev + employer_social_rev + employee_social_rev + vat_rev + corporate_tax_rev + other_rev

# VÝDAJE
pension_spending = pensioners * 1e6 * pension_avg / 1e9
unemployment_spending = unemployed * 1e6 * unemp_benefit / 1e9
health_spending = gdp * health_pct / 100
defense_spending = gdp * defense_pct / 100
education_spending = gdp * education_pct / 100
other_spending = gdp * other_pct / 100
debt_total = gdp * debt_to_gdp / 100
interest_spending = debt_total * interest_rate / 100

total_expenditure = pension_spending + unemployment_spending + health_spending + defense_spending + education_spending + other_spending + interest_spending

balance = total_revenue - total_expenditure
balance_gdp_pct = (balance / gdp) * 100 if gdp > 0 else 0

# New debt ratio after one year
new_debt = debt_total - balance  # if deficit, debt grows
new_debt_to_gdp = (new_debt / gdp) * 100 if gdp > 0 else 0

# --- DISPLAY ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Příjmy", f"{total_revenue:,.1f} {cur}")
col2.metric("Výdaje", f"{total_expenditure:,.1f} {cur}")
col3.metric("Saldo", f"{balance:,.1f} {cur}", delta=f"{balance_gdp_pct:+.1f}% HDP")
col4.metric("Dluh po roce", f"{new_debt_to_gdp:.1f}% HDP", delta=f"{new_debt_to_gdp - debt_to_gdp:+.1f} p.b.")

st.markdown("---")

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Struktura příjmů")
    rev_labels = ["Daň z příjmů FO", "Odvody zaměstnavatel", "Odvody zaměstnanec", "DPH", "Daň z příjmů PO", "Ostatní příjmy"]
    rev_values = [income_tax_rev, employer_social_rev, employee_social_rev, vat_rev, corporate_tax_rev, other_rev]
    fig_rev = px.pie(names=rev_labels, values=rev_values, hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Set2)
    fig_rev.update_layout(height=400)
    st.plotly_chart(fig_rev, use_container_width=True)

with col_right:
    st.subheader("Struktura výdajů")
    exp_labels = ["Důchody", "Podpora v nezam.", "Zdravotnictví", "Obrana", "Vzdělávání", "Ostatní", "Úroky z dluhu"]
    exp_values = [pension_spending, unemployment_spending, health_spending, defense_spending, education_spending, other_spending, interest_spending]
    fig_exp = px.pie(names=exp_labels, values=exp_values, hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_exp.update_layout(height=400)
    st.plotly_chart(fig_exp, use_container_width=True)

# Bar chart comparison
st.subheader("Příjmy vs. Výdaje – porovnání položek")
fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(name="Příjmy", x=rev_labels, y=rev_values, marker_color="#2ecc71"))
fig_bar.add_trace(go.Bar(name="Výdaje", x=exp_labels, y=exp_values, marker_color="#e74c3c"))
fig_bar.update_layout(barmode="group", height=400, yaxis_title=cur)
st.plotly_chart(fig_bar, use_container_width=True)

# 10-year projection
st.subheader("📈 10letá projekce dluhu (při zachování parametrů)")
years = list(range(0, 11))
debt_proj = [debt_to_gdp]
d = debt_total
for y in range(1, 11):
    annual_interest = d * interest_rate / 100
    exp_y = total_expenditure - interest_spending + annual_interest
    bal_y = total_revenue - exp_y
    d = d - bal_y
    debt_proj.append((d / gdp) * 100 if gdp > 0 else 0)

fig_debt = go.Figure()
fig_debt.add_trace(go.Scatter(x=years, y=debt_proj, mode="lines+markers", name="Dluh/HDP %",
                              line=dict(color="#e74c3c", width=3)))
fig_debt.add_hline(y=60, line_dash="dash", annotation_text="Maastrichtské kritérium 60%",
                   line_color="orange")
fig_debt.update_layout(height=350, xaxis_title="Rok", yaxis_title="Dluh/HDP (%)")
st.plotly_chart(fig_debt, use_container_width=True)

# Detail table
st.subheader("📋 Detailní přehled")
import pandas as pd
data = {
    "Položka": rev_labels + ["**PŘÍJMY CELKEM**"] + exp_labels + ["**VÝDAJE CELKEM**", "**SALDO**"],
    f"Hodnota ({cur})": [f"{v:,.1f}" for v in rev_values] + [f"**{total_revenue:,.1f}**"] +
                         [f"{v:,.1f}" for v in exp_values] + [f"**{total_expenditure:,.1f}**", f"**{balance:,.1f}**"],
    "% HDP": [f"{v/gdp*100:.1f}%" for v in rev_values] + [f"**{total_revenue/gdp*100:.1f}%**"] +
              [f"{v/gdp*100:.1f}%" for v in exp_values] + [f"**{total_expenditure/gdp*100:.1f}%**", f"**{balance_gdp_pct:.1f}%**"]
}
st.markdown(pd.DataFrame(data).to_markdown(index=False), unsafe_allow_html=True)

st.markdown("---")
st.caption("⚠️ Zjednodušený model pro výukové účely. Skutečné rozpočty jsou komplexnější. Přednastavené hodnoty jsou aproximací stavu k roku 2025/2026.")
