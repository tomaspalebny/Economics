import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Makroekonomický simulátor rozpočtu", layout="wide")
st.title("🏛️ Simulátor státního rozpočtu")
st.markdown("*Interaktivní nástroj pro výuku makroekonomie – 1. ročník VŠ*")

# --- PRESETS (based on 2024/2025 real data) ---
PRESETS = {
    "🇨🇿 Česká republika": dict(
        gdp=7800, pop=10.9, workforce=5.35, unemployment_rate=2.8, pensioners=2.88, outside_lf=2.52,
        avg_wage_month=45500, income_tax_rate=15.0, employer_social=33.8, employee_social=11.0,
        vat_high=21.0, vat_low=12.0, vat_high_share=65.0,
        corporate_tax=21.0, pension_month=20700, unemployment_benefit_month=14000,
        debt_to_gdp=44.0, interest_rate=3.8, health_pct=7.6, defense_pct=2.1, education_pct=4.5,
        other_spending_pct=7.5, currency="CZK mld"
    ),
    "🇸🇰 Slovensko": dict(
        gdp=133, pop=5.43, workforce=2.58, unemployment_rate=5.7, pensioners=1.15, outside_lf=1.54,
        avg_wage_month=1580, income_tax_rate=19.0, employer_social=35.2, employee_social=13.4,
        vat_high=23.0, vat_low=10.0, vat_high_share=70.0,
        corporate_tax=21.0, pension_month=660, unemployment_benefit_month=450,
        debt_to_gdp=59.0, interest_rate=3.4, health_pct=7.2, defense_pct=2.0, education_pct=4.2,
        other_spending_pct=8.5, currency="EUR mld"
    ),
    "🇩🇪 Německo": dict(
        gdp=4260, pop=84.7, workforce=42.0, unemployment_rate=6.1, pensioners=21.2, outside_lf=16.8,
        avg_wage_month=4580, income_tax_rate=30.0, employer_social=20.8, employee_social=20.3,
        vat_high=19.0, vat_low=7.0, vat_high_share=75.0,
        corporate_tax=30.0, pension_month=1550, unemployment_benefit_month=1100,
        debt_to_gdp=63.0, interest_rate=2.4, health_pct=9.6, defense_pct=2.1, education_pct=4.6,
        other_spending_pct=7.8, currency="EUR mld"
    ),
    "🇺🇸 USA": dict(
        gdp=29200, pop=336.0, workforce=161.0, unemployment_rate=4.0, pensioners=57.0, outside_lf=111.3,
        avg_wage_month=5400, income_tax_rate=22.0, employer_social=7.65, employee_social=7.65,
        vat_high=0.0, vat_low=0.0, vat_high_share=100.0,
        corporate_tax=21.0, pension_month=1900, unemployment_benefit_month=1400,
        debt_to_gdp=124.0, interest_rate=4.4, health_pct=8.5, defense_pct=3.4, education_pct=5.0,
        other_spending_pct=6.8, currency="USD mld"
    ),
    "🇷🇺 Rusko": dict(
        gdp=199000, pop=146.0, workforce=73.5, unemployment_rate=2.4, pensioners=36.0, outside_lf=34.7,
        avg_wage_month=85000, income_tax_rate=13.0, employer_social=30.0, employee_social=0.0,
        vat_high=22.0, vat_low=10.0, vat_high_share=70.0,
        corporate_tax=25.0, pension_month=23400, unemployment_benefit_month=12800,
        debt_to_gdp=18.0, interest_rate=8.5, health_pct=3.7, defense_pct=6.3, education_pct=3.6,
        other_spending_pct=9.5, currency="RUB mld"
    ),
    "⚙️ Vlastní": dict(
        gdp=1000, pop=10.0, workforce=5.0, unemployment_rate=5.0, pensioners=2.0, outside_lf=2.74,
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

big = "CZK" in cur or "RUB" in cur

st.sidebar.markdown("---")
st.sidebar.header("📊 Základní parametry")
gdp = st.sidebar.number_input(f"HDP ({cur})", min_value=1.0, value=float(p["gdp"]), step=10.0 if not big else 100.0, format="%.0f")
pop = st.sidebar.number_input("Populace (mil)", min_value=0.1, value=p["pop"], step=0.1, format="%.1f")
workforce = st.sidebar.number_input("Zaměstnaní (mil)", min_value=0.1, value=p["workforce"], step=0.01, format="%.2f")
unemployment_rate = st.sidebar.number_input("Míra nezaměstnanosti (%)", min_value=0.0, max_value=50.0, value=p["unemployment_rate"], step=0.1, format="%.1f")
pensioners = st.sidebar.number_input("Důchodci (mil)", min_value=0.0, value=p["pensioners"], step=0.01, format="%.2f")
outside_lf = st.sidebar.number_input("Mimo pracovní sílu (mil)", min_value=0.0, value=p["outside_lf"], step=0.01, format="%.2f")

labor_force = workforce / (1 - unemployment_rate / 100) if unemployment_rate < 100 else workforce
unemployed = labor_force - workforce
total_check = workforce + unemployed + pensioners + outside_lf
pop_diff = pop - total_check

if abs(pop_diff) > 0.05:
    st.sidebar.warning(f"⚠️ Součet skupin ({total_check:.2f}) ≠ populace ({pop:.1f}), rozdíl {pop_diff:+.2f} mil")
else:
    st.sidebar.success(f"✅ Populace OK: {total_check:.2f} mil")

st.sidebar.markdown("---")
st.sidebar.header("💵 Měsíční mzdy a dávky")
w_step = 500.0 if big else 10.0
avg_wage_month = st.sidebar.number_input("Průměrná měsíční mzda", min_value=100.0, value=float(p["avg_wage_month"]), step=w_step, format="%.0f")
pension_month = st.sidebar.number_input("Průměrný měsíční důchod", min_value=0.0, value=float(p["pension_month"]), step=w_step, format="%.0f")
unemp_benefit_month = st.sidebar.number_input("Měsíční podpora v nezam.", min_value=0.0, value=float(p["unemployment_benefit_month"]), step=w_step, format="%.0f")

st.sidebar.markdown("---")
st.sidebar.header("💰 Daňové sazby (%)")
income_tax = st.sidebar.number_input("Daň z příjmů FO", min_value=0.0, max_value=60.0, value=p["income_tax_rate"], step=0.1, format="%.1f")
employer_social = st.sidebar.number_input("Odvody zaměstnavatele", min_value=0.0, max_value=60.0, value=p["employer_social"], step=0.1, format="%.1f")
employee_social = st.sidebar.number_input("Odvody zaměstnance", min_value=0.0, max_value=40.0, value=p["employee_social"], step=0.1, format="%.1f")
corporate_tax = st.sidebar.number_input("Daň z příjmů PO", min_value=0.0, max_value=50.0, value=p["corporate_tax"], step=0.1, format="%.1f")

st.sidebar.markdown("---")
st.sidebar.header("🛒 DPH")
vat_high = st.sidebar.number_input("Základní sazba DPH (%)", min_value=0.0, max_value=35.0, value=p["vat_high"], step=0.5, format="%.1f")
vat_low = st.sidebar.number_input("Snížená sazba DPH (%)", min_value=0.0, max_value=25.0, value=p["vat_low"], step=0.5, format="%.1f")
vat_high_share = st.sidebar.number_input("Podíl zboží v základní sazbě (%)", min_value=0.0, max_value=100.0, value=p["vat_high_share"], step=1.0, format="%.0f")

st.sidebar.markdown("---")
st.sidebar.header("📤 Výdaje (% HDP)")
health_pct = st.sidebar.number_input("Zdravotnictví", min_value=0.0, max_value=15.0, value=p["health_pct"], step=0.1, format="%.1f")
defense_pct = st.sidebar.number_input("Obrana", min_value=0.0, max_value=12.0, value=p["defense_pct"], step=0.1, format="%.1f")
education_pct = st.sidebar.number_input("Vzdělávání", min_value=0.0, max_value=12.0, value=p["education_pct"], step=0.1, format="%.1f")
other_pct = st.sidebar.number_input("Ostatní výdaje", min_value=0.0, max_value=25.0, value=p["other_spending_pct"], step=0.1, format="%.1f")

st.sidebar.markdown("---")
st.sidebar.header("🏦 Státní dluh")
debt_to_gdp = st.sidebar.number_input("Dluh/HDP (%)", min_value=0.0, max_value=250.0, value=p["debt_to_gdp"], step=0.5, format="%.1f")
interest_rate = st.sidebar.number_input("Úroková sazba dluhu (%)", min_value=0.0, max_value=20.0, value=p["interest_rate"], step=0.1, format="%.1f")

# --- CALCULATIONS ---
avg_wage = avg_wage_month * 12
pension_avg = pension_month * 12
unemp_benefit = unemp_benefit_month * 12
total_wage_bill = workforce * 1e6 * avg_wage / 1e9

income_tax_rev = total_wage_bill * income_tax / 100
employer_social_rev = total_wage_bill * employer_social / 100
employee_social_rev = total_wage_bill * employee_social / 100
consumption_base = gdp * 0.45
vat_rev = consumption_base * ((vat_high_share / 100) * (vat_high / 100) + ((100 - vat_high_share) / 100) * (vat_low / 100))
corporate_tax_rev = gdp * 0.25 * corporate_tax / 100
other_rev = gdp * 0.02
total_revenue = income_tax_rev + employer_social_rev + employee_social_rev + vat_rev + corporate_tax_rev + other_rev

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
balance_gdp_pct = (balance / gdp * 100) if gdp > 0 else 0
new_debt = debt_total - balance
new_debt_to_gdp = (new_debt / gdp * 100) if gdp > 0 else 0

# --- DISPLAY ---
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Příjmy", f"{total_revenue:,.1f} {cur}")
c2.metric("Výdaje", f"{total_expenditure:,.1f} {cur}")
c3.metric("Saldo", f"{balance:,.1f} {cur}", delta=f"{balance_gdp_pct:+.1f}% HDP")
c4.metric("Dluh", f"{debt_total:,.1f} {cur}", delta=f"{debt_to_gdp:.1f}% HDP")
c5.metric("Dluh po roce", f"{new_debt:,.1f} {cur}", delta=f"{new_debt_to_gdp:.1f}% HDP ({new_debt_to_gdp - debt_to_gdp:+.1f} p.b.)")

st.markdown("---")

st.subheader("👥 Struktura populace")
pc = st.columns(6)
pc[0].metric("Zaměstnaní", f"{workforce:.2f} mil", delta=f"{workforce/pop*100:.1f}%")
pc[1].metric("Nezaměstnaní", f"{unemployed:.2f} mil", delta=f"{unemployment_rate:.1f}%")
pc[2].metric("Důchodci", f"{pensioners:.2f} mil", delta=f"{pensioners/pop*100:.1f}%")
pc[3].metric("Mimo prac. sílu", f"{outside_lf:.2f} mil", delta=f"{outside_lf/pop*100:.1f}%")
pc[4].metric("Součet", f"{total_check:.2f} mil")
pc[5].metric("Populace", f"{pop:.1f} mil", delta=f"Δ {pop_diff:+.2f}" if abs(pop_diff) > 0.05 else "✅ OK")

st.markdown("---")

col_left, col_right = st.columns(2)
rev_labels = ["Daň z příjmů FO", "Odvody zaměstnavatel", "Odvody zaměstnanec", "DPH", "Daň z příjmů PO", "Ostatní příjmy"]
rev_values = [income_tax_rev, employer_social_rev, employee_social_rev, vat_rev, corporate_tax_rev, other_rev]
exp_labels = ["Důchody", "Podpora v nezam.", "Zdravotnictví", "Obrana", "Vzdělávání", "Ostatní", "Úroky z dluhu"]
exp_values = [pension_spending, unemployment_spending, health_spending, defense_spending, education_spending, other_spending, interest_spending]

with col_left:
    st.subheader("Struktura příjmů")
    fig_rev = px.pie(names=rev_labels, values=rev_values, hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
    fig_rev.update_layout(height=400)
    st.plotly_chart(fig_rev, use_container_width=True)

with col_right:
    st.subheader("Struktura výdajů")
    fig_exp = px.pie(names=exp_labels, values=exp_values, hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_exp.update_layout(height=400)
    st.plotly_chart(fig_exp, use_container_width=True)

st.subheader("Příjmy vs. Výdaje")
fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(name="Příjmy", x=rev_labels, y=rev_values, marker_color="#2ecc71"))
fig_bar.add_trace(go.Bar(name="Výdaje", x=exp_labels, y=exp_values, marker_color="#e74c3c"))
fig_bar.update_layout(barmode="group", height=400, yaxis_title=cur)
st.plotly_chart(fig_bar, use_container_width=True)

st.subheader("🛒 Detail DPH")
vat_h_rev = consumption_base * (vat_high_share / 100) * (vat_high / 100)
vat_l_rev = consumption_base * ((100 - vat_high_share) / 100) * (vat_low / 100)
dc1, dc2, dc3 = st.columns(3)
dc1.metric(f"Základní sazba ({vat_high:.0f}%)", f"{vat_h_rev:,.1f} {cur}")
dc2.metric(f"Snížená sazba ({vat_low:.0f}%)", f"{vat_l_rev:,.1f} {cur}")
dc3.metric("DPH celkem", f"{vat_rev:,.1f} {cur}")

st.subheader("📈 10letá projekce dluhu")
debt_proj_pct, debt_proj_abs = [debt_to_gdp], [debt_total]
d = debt_total
for y in range(1, 11):
    ai = d * interest_rate / 100
    ey = total_expenditure - interest_spending + ai
    by = total_revenue - ey
    d = d - by
    debt_proj_pct.append((d / gdp * 100) if gdp > 0 else 0)
    debt_proj_abs.append(d)

lc, rc = st.columns(2)
with lc:
    fig_dp = go.Figure()
    fig_dp.add_trace(go.Scatter(x=list(range(11)), y=debt_proj_pct, mode="lines+markers", name="Dluh/HDP %", line=dict(color="#e74c3c", width=3)))
    fig_dp.add_hline(y=60, line_dash="dash", annotation_text="Maastricht 60%", line_color="orange")
    fig_dp.update_layout(height=350, xaxis_title="Rok", yaxis_title="Dluh/HDP (%)")
    st.plotly_chart(fig_dp, use_container_width=True)
with rc:
    fig_da = go.Figure()
    fig_da.add_trace(go.Scatter(x=list(range(11)), y=debt_proj_abs, mode="lines+markers", name=f"Dluh ({cur})", line=dict(color="#f59e0b", width=3), fill="tozeroy"))
    fig_da.update_layout(height=350, xaxis_title="Rok", yaxis_title=f"Dluh ({cur})")
    st.plotly_chart(fig_da, use_container_width=True)

st.subheader("📋 Detailní přehled")
all_labels = rev_labels + ["**PŘÍJMY CELKEM**"] + exp_labels + ["**VÝDAJE CELKEM**", "**SALDO**"]
all_values = rev_values + [total_revenue] + exp_values + [total_expenditure, balance]
data = {
    "Položka": all_labels,
    f"Hodnota ({cur})": [f"{v:,.1f}" if "CELKEM" not in l and l != "**SALDO**" else f"**{v:,.1f}**" for l, v in zip(all_labels, all_values)],
    "% HDP": [f"{v/gdp*100:.1f}%" if "CELKEM" not in l and l != "**SALDO**" else f"**{v/gdp*100:.1f}%**" for l, v in zip(all_labels, all_values)]
}
st.markdown(pd.DataFrame(data).to_markdown(index=False), unsafe_allow_html=True)

st.markdown("---")
st.caption("⚠️ Zjednodušený model pro výukové účely. Přednastavené hodnoty odpovídají přibližně stavu 2024/2025.")
