import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Makroekonomický simulátor rozpočtu", layout="wide")
st.title("🏛️ Simulátor státního rozpočtu")
st.markdown("*Interaktivní nástroj pro výuku makroekonomie – 1. ročník VŠ*")

PRESETS = {
    "🇨🇿 Česká republika": dict(
        gdp=7800, pop=10.9, workforce=5.3, unemployment_rate=2.8, pensioners=2.9, outside_lf=2.0,
        avg_wage_month=45000, income_tax_rate=15.0, employer_social=33.8, employee_social=11.0,
        vat_high=21.0, vat_low=12.0, vat_high_share=65.0,
        corporate_tax=21.0, pension_month=19000, unemployment_benefit_month=15000,
        debt_to_gdp=43.0, interest_rate=3.5, health_pct=7.5, defense_pct=2.0, education_pct=4.5,
        other_spending_pct=8.0, currency="CZK mld"
    ),
    "🇸🇰 Slovensko": dict(
        gdp=130, pop=5.4, workforce=2.6, unemployment_rate=6.2, pensioners=1.15, outside_lf=1.1,
        avg_wage_month=1500, income_tax_rate=19.0, employer_social=35.2, employee_social=13.4,
        vat_high=23.0, vat_low=10.0, vat_high_share=70.0,
        corporate_tax=21.0, pension_month=600, unemployment_benefit_month=450,
        debt_to_gdp=62.0, interest_rate=3.2, health_pct=7.0, defense_pct=2.0, education_pct=4.0,
        other_spending_pct=9.0, currency="EUR mld"
    ),
    "🇩🇪 Německo": dict(
        gdp=4260, pop=84.5, workforce=42.0, unemployment_rate=6.0, pensioners=21.0, outside_lf=14.0,
        avg_wage_month=4333, income_tax_rate=30.0, employer_social=20.0, employee_social=20.0,
        vat_high=19.0, vat_low=7.0, vat_high_share=75.0,
        corporate_tax=30.0, pension_month=1600, unemployment_benefit_month=1200,
        debt_to_gdp=63.0, interest_rate=2.5, health_pct=9.5, defense_pct=2.0, education_pct=4.5,
        other_spending_pct=8.0, currency="EUR mld"
    ),
    "🇺🇸 USA": dict(
        gdp=28800, pop=335.0, workforce=160.0, unemployment_rate=3.9, pensioners=55.0, outside_lf=95.0,
        avg_wage_month=5417, income_tax_rate=22.0, employer_social=7.65, employee_social=7.65,
        vat_high=0.0, vat_low=0.0, vat_high_share=100.0,
        corporate_tax=21.0, pension_month=1833, unemployment_benefit_month=1333,
        debt_to_gdp=124.0, interest_rate=4.5, health_pct=8.5, defense_pct=3.5, education_pct=5.0,
        other_spending_pct=7.0, currency="USD mld"
    ),
    "🇷🇺 Rusko": dict(
        gdp=195000, pop=146.0, workforce=73.0, unemployment_rate=3.7, pensioners=36.0, outside_lf=31.0,
        avg_wage_month=75000, income_tax_rate=13.0, employer_social=30.0, employee_social=0.0,
        vat_high=22.0, vat_low=10.0, vat_high_share=70.0,
        corporate_tax=25.0, pension_month=21000, unemployment_benefit_month=12000,
        debt_to_gdp=17.0, interest_rate=8.0, health_pct=3.5, defense_pct=6.0, education_pct=3.5,
        other_spending_pct=10.0, currency="RUB mld"
    ),
    "⚙️ Vlastní": dict(
        gdp=1000, pop=10.0, workforce=5.0, unemployment_rate=5.0, pensioners=2.0, outside_lf=1.5,
        avg_wage_month=2500, income_tax_rate=20.0, employer_social=25.0, employee_social=10.0,
        vat_high=20.0, vat_low=10.0, vat_high_share=65.0,
        corporate_tax=20.0, pension_month=800, unemployment_benefit_month=500,
        debt_to_gdp=40.0, interest_rate=3.0, health_pct=7.0, defense_pct=2.0, education_pct=4.0,
        other_spending_pct=8.0, currency="jednotek"
    ),
}

# --- SIDEBAR ---
st.sidebar.header("Vyberte preset ekonomiky")
preset_name = st.sidebar.selectbox("Ekonomika", list(PRESETS.keys()))
p = PRESETS[preset_name]
cur = p["currency"]

big_wage = "CZK" in cur or "RUB" in cur

st.sidebar.markdown("---")
st.sidebar.header("📊 Základní parametry")
gdp = st.sidebar.slider(f"HDP ({cur})", 10.0, 250000.0, float(p["gdp"]), step=10.0)
pop = st.sidebar.slider("Populace (mil)", 1.0, 400.0, p["pop"], step=0.5)
workforce = st.sidebar.slider("Pracovní síla – zaměstnaní (mil)", 0.5, 200.0, p["workforce"], step=0.1)
unemployment_rate = st.sidebar.slider("Míra nezaměstnanosti (%)", 0.0, 30.0, p["unemployment_rate"], step=0.1)
pensioners = st.sidebar.slider("Důchodci (mil)", 0.1, 80.0, p["pensioners"], step=0.1)
outside_lf = st.sidebar.slider("Mimo pracovní sílu – ostatní (mil)", 0.0, 120.0, p["outside_lf"], step=0.1)

# Derived
labor_force = workforce / (1 - unemployment_rate / 100) if unemployment_rate < 100 else workforce
unemployed = labor_force - workforce
total_check = workforce + unemployed + pensioners + outside_lf

pop_diff = pop - total_check
if abs(pop_diff) > 0.05:
    st.sidebar.warning(f"⚠️ Součet skupin ({total_check:.2f} mil) se liší od populace ({pop:.1f} mil) o **{pop_diff:+.2f} mil**. Upravte parametry.")
else:
    st.sidebar.success(f"✅ Populace sedí: {workforce:.2f} zaměst. + {unemployed:.2f} nezam. + {pensioners:.2f} důch. + {outside_lf:.2f} ostatní = {total_check:.2f} mil")

st.sidebar.markdown("---")
st.sidebar.header("💵 Mzdy a důchody (měsíční)")
wmax = 200000.0 if big_wage else 15000.0
avg_wage_month = st.sidebar.slider("Průměrná měsíční mzda", 500.0, wmax, float(p["avg_wage_month"]), step=500.0 if big_wage else 50.0)
pmax = 100000.0 if big_wage else 5000.0
pension_month = st.sidebar.slider("Průměrný měsíční důchod", 100.0, pmax, float(p["pension_month"]), step=500.0 if big_wage else 50.0)
ubmax = 80000.0 if big_wage else 4000.0
unemp_benefit_month = st.sidebar.slider("Měsíční podpora v nezam.", 100.0, ubmax, float(p["unemployment_benefit_month"]), step=500.0 if big_wage else 50.0)

st.sidebar.markdown("---")
st.sidebar.header("💰 Daňové sazby")
income_tax = st.sidebar.slider("Daň z příjmů FO (%)", 0.0, 50.0, p["income_tax_rate"], step=0.5)
employer_social = st.sidebar.slider("Odvody zaměstnavatele (%)", 0.0, 50.0, p["employer_social"], step=0.5)
employee_social = st.sidebar.slider("Odvody zaměstnance (%)", 0.0, 30.0, p["employee_social"], step=0.5)
corporate_tax = st.sidebar.slider("Daň z příjmů PO (%)", 0.0, 40.0, p["corporate_tax"], step=0.5)

st.sidebar.markdown("---")
st.sidebar.header("🛒 DPH (dvě sazby)")
vat_high = st.sidebar.slider("Základní sazba DPH (%)", 0.0, 30.0, p["vat_high"], step=0.5)
vat_low = st.sidebar.slider("Snížená sazba DPH (%)", 0.0, 20.0, p["vat_low"], step=0.5)
vat_high_share = st.sidebar.slider("Podíl zboží v základní sazbě (%)", 0.0, 100.0, p["vat_high_share"], step=1.0)

st.sidebar.markdown("---")
st.sidebar.header("📤 Výdaje (% HDP)")
health_pct = st.sidebar.slider("Zdravotnictví", 0.0, 15.0, p["health_pct"], step=0.5)
defense_pct = st.sidebar.slider("Obrana", 0.0, 10.0, p["defense_pct"], step=0.5)
education_pct = st.sidebar.slider("Vzdělávání", 0.0, 10.0, p["education_pct"], step=0.5)
other_pct = st.sidebar.slider("Ostatní výdaje", 0.0, 20.0, p["other_spending_pct"], step=0.5)

st.sidebar.markdown("---")
st.sidebar.header("🏦 Státní dluh")
debt_to_gdp = st.sidebar.slider("Dluh/HDP (%)", 0.0, 200.0, p["debt_to_gdp"], step=1.0)
interest_rate = st.sidebar.slider("Úroková sazba dluhu (%)", 0.0, 15.0, p["interest_rate"], step=0.1)

# --- CALCULATIONS ---
avg_wage = avg_wage_month * 12
pension_avg = pension_month * 12
unemp_benefit = unemp_benefit_month * 12

total_wage_bill = workforce * 1e6 * avg_wage / 1e9

# PŘÍJMY
income_tax_rev = total_wage_bill * (income_tax / 100)
employer_social_rev = total_wage_bill * (employer_social / 100)
employee_social_rev = total_wage_bill * (employee_social / 100)
consumption_base = gdp * 0.45
vat_rev = consumption_base * ((vat_high_share / 100) * (vat_high / 100) + ((100 - vat_high_share) / 100) * (vat_low / 100))
corporate_tax_rev = gdp * 0.25 * (corporate_tax / 100)
other_rev = gdp * 0.02

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

new_debt = debt_total - balance
new_debt_to_gdp = (new_debt / gdp) * 100 if gdp > 0 else 0

# --- DISPLAY ---
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Příjmy", f"{total_revenue:,.1f} {cur}")
col2.metric("Výdaje", f"{total_expenditure:,.1f} {cur}")
col3.metric("Saldo", f"{balance:,.1f} {cur}", delta=f"{balance_gdp_pct:+.1f}% HDP")
col4.metric("Dluh (abs.)", f"{debt_total:,.1f} {cur}")
col5.metric("Dluh po roce", f"{new_debt:,.1f} {cur}", delta=f"{new_debt_to_gdp:.1f}% HDP ({new_debt_to_gdp - debt_to_gdp:+.1f} p.b.)")

st.markdown("---")

# Population breakdown
st.subheader("👥 Struktura populace")
pop_cols = st.columns(5)
pop_cols[0].metric("Zaměstnaní", f"{workforce:.2f} mil")
pop_cols[1].metric("Nezaměstnaní", f"{unemployed:.2f} mil", delta=f"{unemployment_rate:.1f}%")
pop_cols[2].metric("Důchodci", f"{pensioners:.2f} mil")
pop_cols[3].metric("Mimo prac. sílu", f"{outside_lf:.2f} mil")
pop_cols[4].metric("Celkem / Populace", f"{total_check:.2f} / {pop:.1f} mil")

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

st.subheader("Příjmy vs. Výdaje – porovnání položek")
fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(name="Příjmy", x=rev_labels, y=rev_values, marker_color="#2ecc71"))
fig_bar.add_trace(go.Bar(name="Výdaje", x=exp_labels, y=exp_values, marker_color="#e74c3c"))
fig_bar.update_layout(barmode="group", height=400, yaxis_title=cur)
st.plotly_chart(fig_bar, use_container_width=True)

# DPH detail
st.subheader("🛒 Detail DPH")
vat_h_rev = consumption_base * (vat_high_share / 100) * (vat_high / 100)
vat_l_rev = consumption_base * ((100 - vat_high_share) / 100) * (vat_low / 100)
dcol1, dcol2, dcol3 = st.columns(3)
dcol1.metric(f"Základní sazba ({vat_high:.0f}%)", f"{vat_h_rev:,.1f} {cur}")
dcol2.metric(f"Snížená sazba ({vat_low:.0f}%)", f"{vat_l_rev:,.1f} {cur}")
dcol3.metric("DPH celkem", f"{vat_rev:,.1f} {cur}")

# 10-year projection
st.subheader("📈 10letá projekce dluhu")
years = list(range(0, 11))
debt_proj_pct = [debt_to_gdp]
debt_proj_abs = [debt_total]
d = debt_total
for y in range(1, 11):
    annual_interest = d * interest_rate / 100
    exp_y = total_expenditure - interest_spending + annual_interest
    bal_y = total_revenue - exp_y
    d = d - bal_y
    debt_proj_pct.append((d / gdp) * 100 if gdp > 0 else 0)
    debt_proj_abs.append(d)

fig_debt = go.Figure()
fig_debt.add_trace(go.Scatter(x=years, y=debt_proj_pct, mode="lines+markers", name="Dluh/HDP %",
                              line=dict(color="#e74c3c", width=3)))
fig_debt.add_hline(y=60, line_dash="dash", annotation_text="Maastricht 60%", line_color="orange")
fig_debt.update_layout(height=350, xaxis_title="Rok", yaxis_title="Dluh/HDP (%)")
st.plotly_chart(fig_debt, use_container_width=True)

fig_debt_abs = go.Figure()
fig_debt_abs.add_trace(go.Scatter(x=years, y=debt_proj_abs, mode="lines+markers", name=f"Dluh ({cur})",
                                  line=dict(color="#f59e0b", width=3), fill="tozeroy"))
fig_debt_abs.update_layout(height=300, xaxis_title="Rok", yaxis_title=f"Dluh ({cur})")
st.plotly_chart(fig_debt_abs, use_container_width=True)

# Detail table
st.subheader("📋 Detailní přehled")
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
