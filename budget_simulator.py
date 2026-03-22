import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Makroekonomický simulátor rozpočtu – detailní", layout="wide")
st.title("🏛️ Simulátor státního rozpočtu")
st.markdown("*Detailnější verze – příjmy i výdaje po hlavních kapitolách veřejných financí*")

PRESETS = {
    "🇨🇿 Česká republika": dict(
        gdp=7800, pop=10.9, workforce=5.35, unemployment_rate=2.8, pensioners=2.88, outside_lf=2.52,
        avg_wage_month=45500, income_tax_rate=15.0, employer_social=33.8, employee_social=11.0,
        vat_high=21.0, vat_low=12.0, vat_high_share=65.0, corporate_tax=21.0,
        pension_month=20700, unemployment_benefit_month=14000,
        debt_to_gdp=44.0, interest_rate=3.8,
        health_pct=7.6, defense_pct=2.1, education_pct=4.5,
        consumption_share=48.0, corp_profit_share=22.0, eff_coverage=85.0,
        excise_pct=3.2, property_pct=0.4, customs_pct=0.2, environmental_pct=0.7, fees_pct=1.1, grants_pct=1.1, nontax_pct=4.0,
        family_pct=3.1, sickness_pct=1.2, housing_pct=0.8, public_order_pct=1.8, transport_pct=2.4, environment_exp_pct=0.8,
        agriculture_pct=0.9, admin_pct=3.2, subsidies_pct=3.7, culture_pct=0.7, currency="CZK mld"
    ),
    "🇸🇰 Slovensko": dict(
        gdp=133, pop=5.43, workforce=2.58, unemployment_rate=5.7, pensioners=1.15, outside_lf=1.54,
        avg_wage_month=1580, income_tax_rate=19.0, employer_social=35.2, employee_social=13.4,
        vat_high=23.0, vat_low=10.0, vat_high_share=70.0, corporate_tax=21.0,
        pension_month=660, unemployment_benefit_month=450,
        debt_to_gdp=59.0, interest_rate=3.4,
        health_pct=7.2, defense_pct=2.0, education_pct=4.2,
        consumption_share=50.0, corp_profit_share=20.0, eff_coverage=85.0,
        excise_pct=2.7, property_pct=0.5, customs_pct=0.2, environmental_pct=0.5, fees_pct=0.8, grants_pct=1.0, nontax_pct=1.6,
        family_pct=3.6, sickness_pct=1.3, housing_pct=0.6, public_order_pct=1.5, transport_pct=2.8, environment_exp_pct=0.9,
        agriculture_pct=1.0, admin_pct=3.0, subsidies_pct=6.0, culture_pct=0.6, currency="EUR mld"
    ),
    "🇩🇪 Německo": dict(
        gdp=4260, pop=84.7, workforce=42.0, unemployment_rate=6.1, pensioners=21.2, outside_lf=16.8,
        avg_wage_month=4580, income_tax_rate=30.0, employer_social=20.8, employee_social=20.3,
        vat_high=19.0, vat_low=7.0, vat_high_share=75.0, corporate_tax=30.0,
        pension_month=1550, unemployment_benefit_month=1100,
        debt_to_gdp=63.0, interest_rate=2.4,
        health_pct=9.6, defense_pct=2.1, education_pct=4.6,
        consumption_share=48.0, corp_profit_share=13.0, eff_coverage=55.0,
        excise_pct=2.2, property_pct=1.0, customs_pct=0.3, environmental_pct=1.8, fees_pct=1.1, grants_pct=0.9, nontax_pct=6.2,
        family_pct=3.3, sickness_pct=1.5, housing_pct=0.5, public_order_pct=1.7, transport_pct=1.8, environment_exp_pct=0.8,
        agriculture_pct=0.8, admin_pct=3.0, subsidies_pct=7.1, culture_pct=0.9, currency="EUR mld"
    ),
    "🇺🇸 USA": dict(
        gdp=29200, pop=336.0, workforce=161.0, unemployment_rate=4.0, pensioners=57.0, outside_lf=111.3,
        avg_wage_month=5400, income_tax_rate=22.0, employer_social=7.65, employee_social=7.65,
        vat_high=0.0, vat_low=0.0, vat_high_share=100.0, corporate_tax=21.0,
        pension_month=1900, unemployment_benefit_month=1400,
        debt_to_gdp=124.0, interest_rate=4.4,
        health_pct=8.5, defense_pct=3.4, education_pct=5.0,
        consumption_share=68.0, corp_profit_share=12.0, eff_coverage=80.0,
        excise_pct=0.7, property_pct=3.0, customs_pct=0.3, environmental_pct=0.2, fees_pct=1.5, grants_pct=0.0, nontax_pct=14.1,
        family_pct=1.8, sickness_pct=0.8, housing_pct=0.5, public_order_pct=2.0, transport_pct=1.5, environment_exp_pct=0.4,
        agriculture_pct=0.3, admin_pct=2.1, subsidies_pct=1.1, culture_pct=0.3, currency="USD mld"
    ),
    "🇷🇺 Rusko": dict(
        gdp=199000, pop=146.0, workforce=73.5, unemployment_rate=2.4, pensioners=36.0, outside_lf=34.7,
        avg_wage_month=85000, income_tax_rate=13.0, employer_social=30.0, employee_social=0.0,
        vat_high=22.0, vat_low=10.0, vat_high_share=70.0, corporate_tax=25.0,
        pension_month=23400, unemployment_benefit_month=12800,
        debt_to_gdp=18.0, interest_rate=8.5,
        health_pct=3.7, defense_pct=6.3, education_pct=3.6,
        consumption_share=45.0, corp_profit_share=18.0, eff_coverage=50.0,
        excise_pct=2.4, property_pct=0.6, customs_pct=1.3, environmental_pct=0.3, fees_pct=1.0, grants_pct=0.1, nontax_pct=6.9,
        family_pct=1.8, sickness_pct=0.8, housing_pct=0.9, public_order_pct=2.2, transport_pct=1.6, environment_exp_pct=0.4,
        agriculture_pct=0.7, admin_pct=2.2, subsidies_pct=3.8, culture_pct=0.5, currency="RUB mld"
    ),
    "⚙️ Vlastní": dict(
        gdp=1000, pop=10.0, workforce=5.0, unemployment_rate=5.0, pensioners=2.0, outside_lf=2.74,
        avg_wage_month=2500, income_tax_rate=20.0, employer_social=25.0, employee_social=10.0,
        vat_high=20.0, vat_low=10.0, vat_high_share=65.0, corporate_tax=20.0,
        pension_month=800, unemployment_benefit_month=500,
        debt_to_gdp=40.0, interest_rate=3.0,
        health_pct=7.0, defense_pct=2.0, education_pct=4.0,
        consumption_share=48.0, corp_profit_share=20.0, eff_coverage=80.0,
        excise_pct=1.5, property_pct=0.5, customs_pct=0.2, environmental_pct=0.4, fees_pct=0.6, grants_pct=0.3, nontax_pct=1.5,
        family_pct=2.0, sickness_pct=0.8, housing_pct=0.5, public_order_pct=1.5, transport_pct=1.5, environment_exp_pct=0.5,
        agriculture_pct=0.5, admin_pct=2.0, subsidies_pct=2.5, culture_pct=0.5, currency="jednotek"
    )
}

st.sidebar.header("Vyberte preset ekonomiky")
preset_name = st.sidebar.selectbox("Ekonomika", list(PRESETS.keys()))
p = PRESETS[preset_name]
cur = p["currency"]
big = "CZK" in cur or "RUB" in cur

st.sidebar.markdown("---")
st.sidebar.header("📊 Základní parametry")
gdp = st.sidebar.number_input(f"HDP ({cur})", min_value=1.0, value=float(p["gdp"]), step=10.0 if not big else 100.0, format="%.0f")
pop = st.sidebar.number_input("Populace (mil)", min_value=0.1, value=float(p["pop"]), step=0.1, format="%.1f")
workforce = st.sidebar.number_input("Zaměstnaní (mil)", min_value=0.1, value=float(p["workforce"]), step=0.01, format="%.2f")
unemployment_rate = st.sidebar.number_input("Míra nezaměstnanosti (%)", min_value=0.0, max_value=50.0, value=float(p["unemployment_rate"]), step=0.1, format="%.1f")
pensioners = st.sidebar.number_input("Důchodci (mil)", min_value=0.0, value=float(p["pensioners"]), step=0.01, format="%.2f")
outside_lf = st.sidebar.number_input("Mimo pracovní sílu (mil)", min_value=0.0, value=float(p["outside_lf"]), step=0.01, format="%.2f")

labor_force = workforce / (1 - unemployment_rate / 100) if unemployment_rate < 100 else workforce
unemployed = labor_force - workforce
total_check = workforce + unemployed + pensioners + outside_lf
pop_diff = pop - total_check
if abs(pop_diff) > 0.05:
    st.sidebar.warning(f"⚠️ Součet ({total_check:.2f}) ≠ populace ({pop:.1f}), Δ {pop_diff:+.2f} mil")
else:
    st.sidebar.success(f"✅ Populace OK: {total_check:.2f} mil")

st.sidebar.markdown("---")
st.sidebar.header("💵 Měsíční mzdy a dávky")
ws = 500.0 if big else 10.0
avg_wage_month = st.sidebar.number_input("Průměrná měsíční mzda", min_value=100.0, value=float(p["avg_wage_month"]), step=ws, format="%.0f")
pension_month = st.sidebar.number_input("Průměrný měsíční důchod", min_value=0.0, value=float(p["pension_month"]), step=ws, format="%.0f")
unemp_benefit_month = st.sidebar.number_input("Měsíční podpora v nezam.", min_value=0.0, value=float(p["unemployment_benefit_month"]), step=ws, format="%.0f")

st.sidebar.markdown("---")
st.sidebar.header("💰 Hlavní daňové sazby (%)")
income_tax = st.sidebar.number_input("Daň z příjmů FO", min_value=0.0, max_value=60.0, value=float(p["income_tax_rate"]), step=0.1, format="%.1f")
employer_social = st.sidebar.number_input("Odvody zaměstnavatele", min_value=0.0, max_value=60.0, value=float(p["employer_social"]), step=0.1, format="%.1f")
employee_social = st.sidebar.number_input("Odvody zaměstnance", min_value=0.0, max_value=40.0, value=float(p["employee_social"]), step=0.1, format="%.1f")
corporate_tax = st.sidebar.number_input("Daň z příjmů PO", min_value=0.0, max_value=50.0, value=float(p["corporate_tax"]), step=0.1, format="%.1f")

st.sidebar.markdown("---")
st.sidebar.header("🛒 DPH")
vat_high = st.sidebar.number_input("Základní sazba DPH (%)", min_value=0.0, max_value=35.0, value=float(p["vat_high"]), step=0.5, format="%.1f")
vat_low = st.sidebar.number_input("Snížená sazba DPH (%)", min_value=0.0, max_value=25.0, value=float(p["vat_low"]), step=0.5, format="%.1f")
vat_high_share = st.sidebar.number_input("Podíl zboží v základní sazbě (%)", min_value=0.0, max_value=100.0, value=float(p["vat_high_share"]), step=1.0, format="%.0f")

st.sidebar.markdown("---")
st.sidebar.header("🔧 Kalibrační parametry")
consumption_share = st.sidebar.number_input("Spotřební báze (% HDP)", min_value=10.0, max_value=80.0, value=float(p["consumption_share"]), step=0.5, format="%.1f")
corp_profit_share = st.sidebar.number_input("Zisková báze PO (% HDP)", min_value=1.0, max_value=40.0, value=float(p["corp_profit_share"]), step=0.5, format="%.1f")
eff_coverage = st.sidebar.number_input("Efektivní pokrytí mezd (%)", min_value=10.0, max_value=100.0, value=float(p["eff_coverage"]), step=1.0, format="%.0f")

st.sidebar.markdown("---")
st.sidebar.header("📥 Ostatní příjmy (% HDP)")
excise_pct = st.sidebar.number_input("Spotřební daně", min_value=0.0, max_value=10.0, value=float(p["excise_pct"]), step=0.1, format="%.1f")
property_pct = st.sidebar.number_input("Majetkové daně", min_value=0.0, max_value=8.0, value=float(p["property_pct"]), step=0.1, format="%.1f")
customs_pct = st.sidebar.number_input("Cla a dovozní dávky", min_value=0.0, max_value=5.0, value=float(p["customs_pct"]), step=0.1, format="%.1f")
environmental_pct = st.sidebar.number_input("Environmentální daně", min_value=0.0, max_value=5.0, value=float(p["environmental_pct"]), step=0.1, format="%.1f")
fees_pct = st.sidebar.number_input("Poplatky a správní příjmy", min_value=0.0, max_value=5.0, value=float(p["fees_pct"]), step=0.1, format="%.1f")
grants_pct = st.sidebar.number_input("Transfery a granty", min_value=0.0, max_value=8.0, value=float(p["grants_pct"]), step=0.1, format="%.1f")
nontax_pct = st.sidebar.number_input("Nedaňové a kapitálové příjmy", min_value=0.0, max_value=15.0, value=float(p["nontax_pct"]), step=0.1, format="%.1f")

st.sidebar.markdown("---")
st.sidebar.header("📤 Výdaje (% HDP)")
health_pct = st.sidebar.number_input("Zdravotnictví", min_value=0.0, max_value=15.0, value=float(p["health_pct"]), step=0.1, format="%.1f")
defense_pct = st.sidebar.number_input("Obrana", min_value=0.0, max_value=12.0, value=float(p["defense_pct"]), step=0.1, format="%.1f")
education_pct = st.sidebar.number_input("Vzdělávání", min_value=0.0, max_value=12.0, value=float(p["education_pct"]), step=0.1, format="%.1f")
family_pct = st.sidebar.number_input("Rodiny a děti", min_value=0.0, max_value=8.0, value=float(p["family_pct"]), step=0.1, format="%.1f")
sickness_pct = st.sidebar.number_input("Nemocenská a invalidita", min_value=0.0, max_value=8.0, value=float(p["sickness_pct"]), step=0.1, format="%.1f")
housing_pct = st.sidebar.number_input("Bydlení a komunální služby", min_value=0.0, max_value=5.0, value=float(p["housing_pct"]), step=0.1, format="%.1f")
public_order_pct = st.sidebar.number_input("Veřejný pořádek a justice", min_value=0.0, max_value=6.0, value=float(p["public_order_pct"]), step=0.1, format="%.1f")
transport_pct = st.sidebar.number_input("Doprava a infrastruktura", min_value=0.0, max_value=8.0, value=float(p["transport_pct"]), step=0.1, format="%.1f")
environment_exp_pct = st.sidebar.number_input("Životní prostředí", min_value=0.0, max_value=4.0, value=float(p["environment_exp_pct"]), step=0.1, format="%.1f")
agriculture_pct = st.sidebar.number_input("Zemědělství a venkov", min_value=0.0, max_value=4.0, value=float(p["agriculture_pct"]), step=0.1, format="%.1f")
admin_pct = st.sidebar.number_input("Veřejná správa", min_value=0.0, max_value=8.0, value=float(p["admin_pct"]), step=0.1, format="%.1f")
subsidies_pct = st.sidebar.number_input("Dotace a podpora podniků", min_value=0.0, max_value=10.0, value=float(p["subsidies_pct"]), step=0.1, format="%.1f")
culture_pct = st.sidebar.number_input("Kultura, sport, média", min_value=0.0, max_value=3.0, value=float(p["culture_pct"]), step=0.1, format="%.1f")

st.sidebar.markdown("---")
st.sidebar.header("🏦 Státní dluh")
debt_to_gdp = st.sidebar.number_input("Dluh/HDP (%)", min_value=0.0, max_value=250.0, value=float(p["debt_to_gdp"]), step=0.5, format="%.1f")
interest_rate = st.sidebar.number_input("Úroková sazba dluhu (%)", min_value=0.0, max_value=20.0, value=float(p["interest_rate"]), step=0.1, format="%.1f")

# Výpočty
avg_wage = avg_wage_month * 12
pension_avg = pension_month * 12
unemp_benefit = unemp_benefit_month * 12
total_wage_bill = workforce * 1e6 * avg_wage / 1e9
eff_wage_bill = total_wage_bill * eff_coverage / 100
consumption_base = gdp * consumption_share / 100
weighted_vat_rate = ((vat_high_share / 100) * (vat_high / 100) + ((100 - vat_high_share) / 100) * (vat_low / 100))
vat_high_rev = consumption_base * (vat_high_share / 100) * (vat_high / 100)
vat_low_rev = consumption_base * ((100 - vat_high_share) / 100) * (vat_low / 100)

# Příjmy
income_tax_rev = eff_wage_bill * income_tax / 100
employer_social_rev = eff_wage_bill * employer_social / 100
employee_social_rev = eff_wage_bill * employee_social / 100
vat_rev = consumption_base * weighted_vat_rate
corporate_tax_rev = gdp * corp_profit_share / 100 * corporate_tax / 100
excise_rev = gdp * excise_pct / 100
property_rev = gdp * property_pct / 100
customs_rev = gdp * customs_pct / 100
environmental_rev = gdp * environmental_pct / 100
fees_rev = gdp * fees_pct / 100
grants_rev = gdp * grants_pct / 100
nontax_rev = gdp * nontax_pct / 100

revenue_items = {
    "Daň z příjmů FO": income_tax_rev,
    "Sociální odvody zaměstnavatel": employer_social_rev,
    "Sociální odvody zaměstnanec": employee_social_rev,
    "DPH – základní sazba": vat_high_rev,
    "DPH – snížená sazba": vat_low_rev,
    "Daň z příjmů PO": corporate_tax_rev,
    "Spotřební daně": excise_rev,
    "Majetkové daně": property_rev,
    "Cla a dovozní dávky": customs_rev,
    "Environmentální daně": environmental_rev,
    "Poplatky a správní příjmy": fees_rev,
    "Transfery a granty": grants_rev,
    "Nedaňové a kapitálové příjmy": nontax_rev,
}
total_revenue = sum(revenue_items.values())

# Výdaje
pension_spending = pensioners * 1e6 * pension_avg / 1e9
unemployment_spending = unemployed * 1e6 * unemp_benefit / 1e9
health_spending = gdp * health_pct / 100
defense_spending = gdp * defense_pct / 100
education_spending = gdp * education_pct / 100
family_spending = gdp * family_pct / 100
sickness_spending = gdp * sickness_pct / 100
housing_spending = gdp * housing_pct / 100
public_order_spending = gdp * public_order_pct / 100
transport_spending = gdp * transport_pct / 100
environment_spending = gdp * environment_exp_pct / 100
agriculture_spending = gdp * agriculture_pct / 100
admin_spending = gdp * admin_pct / 100
subsidies_spending = gdp * subsidies_pct / 100
culture_spending = gdp * culture_pct / 100
debt_total = gdp * debt_to_gdp / 100
interest_spending = debt_total * interest_rate / 100

expenditure_items = {
    "Důchody": pension_spending,
    "Podpora v nezaměstnanosti": unemployment_spending,
    "Zdravotnictví": health_spending,
    "Vzdělávání": education_spending,
    "Obrana": defense_spending,
    "Rodiny a děti": family_spending,
    "Nemocenská a invalidita": sickness_spending,
    "Bydlení a komunální služby": housing_spending,
    "Veřejný pořádek a justice": public_order_spending,
    "Doprava a infrastruktura": transport_spending,
    "Životní prostředí": environment_spending,
    "Zemědělství a venkov": agriculture_spending,
    "Veřejná správa": admin_spending,
    "Dotace a podpora podniků": subsidies_spending,
    "Kultura, sport, média": culture_spending,
    "Úroky z dluhu": interest_spending,
}
total_expenditure = sum(expenditure_items.values())

balance = total_revenue - total_expenditure
balance_gdp_pct = (balance / gdp * 100) if gdp > 0 else 0
debt_next = debt_total - balance
debt_next_pct = (debt_next / gdp * 100) if gdp > 0 else 0

# Metriky
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Příjmy", f"{total_revenue:,.1f} {cur}", delta=f"{total_revenue/gdp*100:.1f}% HDP")
c2.metric("Výdaje", f"{total_expenditure:,.1f} {cur}", delta=f"{total_expenditure/gdp*100:.1f}% HDP")
c3.metric("Saldo", f"{balance:,.1f} {cur}", delta=f"{balance_gdp_pct:+.1f}% HDP", delta_color="normal" if balance >= 0 else "inverse")
c4.metric("Dluh", f"{debt_total:,.1f} {cur}", delta=f"{debt_to_gdp:.1f}% HDP", delta_color="off")
c5.metric("Dluh po roce", f"{debt_next:,.1f} {cur}", delta=f"{debt_next_pct:.1f}% HDP ({debt_next_pct - debt_to_gdp:+.1f} p.b.)", delta_color="inverse")

st.markdown("---")
st.subheader("👥 Struktura populace")
pc = st.columns(6)
pc[0].metric("Zaměstnaní", f"{workforce:.2f} mil", delta=f"{workforce/pop*100:.1f}%", delta_color="off")
pc[1].metric("Nezaměstnaní", f"{unemployed:.2f} mil", delta=f"{unemployment_rate:.1f}%", delta_color="off")
pc[2].metric("Důchodci", f"{pensioners:.2f} mil", delta=f"{pensioners/pop*100:.1f}%", delta_color="off")
pc[3].metric("Mimo prac. sílu", f"{outside_lf:.2f} mil", delta=f"{outside_lf/pop*100:.1f}%", delta_color="off")
pc[4].metric("Součet", f"{total_check:.2f} mil")
pc[5].metric("Populace", f"{pop:.1f} mil", delta=f"Δ {pop_diff:+.2f}" if abs(pop_diff) > 0.05 else "✅ OK", delta_color="off")

st.markdown("---")
col_l, col_r = st.columns(2)
with col_l:
    st.subheader("Struktura příjmů")
    fig_rev = px.pie(names=list(revenue_items.keys()), values=list(revenue_items.values()), hole=0.45, color_discrete_sequence=px.colors.qualitative.Set3)
    fig_rev.update_layout(height=520)
    st.plotly_chart(fig_rev, use_container_width=True)
with col_r:
    st.subheader("Struktura výdajů")
    fig_exp = px.pie(names=list(expenditure_items.keys()), values=list(expenditure_items.values()), hole=0.45, color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_exp.update_layout(height=520)
    st.plotly_chart(fig_exp, use_container_width=True)

st.subheader("📥 Příjmy podle kapitol")
rev_df = pd.DataFrame({
    "Položka": list(revenue_items.keys()),
    f"Hodnota ({cur})": list(revenue_items.values()),
    "% HDP": [v / gdp * 100 for v in revenue_items.values()]
}).sort_values(f"Hodnota ({cur})", ascending=False)
fig_rev_bar = px.bar(rev_df, x="Položka", y=f"Hodnota ({cur})", text=rev_df[f"Hodnota ({cur})"].map(lambda x: f"{x:,.1f}"))
fig_rev_bar.update_layout(height=420, xaxis_tickangle=-35)
st.plotly_chart(fig_rev_bar, use_container_width=True)

st.subheader("📤 Výdaje podle kapitol")
exp_df = pd.DataFrame({
    "Položka": list(expenditure_items.keys()),
    f"Hodnota ({cur})": list(expenditure_items.values()),
    "% HDP": [v / gdp * 100 for v in expenditure_items.values()]
}).sort_values(f"Hodnota ({cur})", ascending=False)
fig_exp_bar = px.bar(exp_df, x="Položka", y=f"Hodnota ({cur})", text=exp_df[f"Hodnota ({cur})"].map(lambda x: f"{x:,.1f}"), color=f"Hodnota ({cur})", color_continuous_scale="Reds")
fig_exp_bar.update_layout(height=420, xaxis_tickangle=-35)
st.plotly_chart(fig_exp_bar, use_container_width=True)

st.subheader("🛒 Detail DPH")
dc1, dc2, dc3, dc4 = st.columns(4)
dc1.metric(f"Základní sazba ({vat_high:.1f}%)", f"{vat_high_rev:,.1f} {cur}")
dc2.metric(f"Snížená sazba ({vat_low:.1f}%)", f"{vat_low_rev:,.1f} {cur}")
dc3.metric("DPH celkem", f"{vat_rev:,.1f} {cur}")
dc4.metric("Spotřební báze", f"{consumption_base:,.1f} {cur}", delta=f"{consumption_share:.1f}% HDP")

st.subheader("📈 10letá projekce dluhu")
debt_proj_pct = [debt_to_gdp]
debt_proj_abs = [debt_total]
d = debt_total
primary_expenditure = total_expenditure - interest_spending
for _ in range(10):
    ai = d * interest_rate / 100
    total_exp_y = primary_expenditure + ai
    bal_y = total_revenue - total_exp_y
    d = d - bal_y
    debt_proj_pct.append((d / gdp * 100) if gdp > 0 else 0)
    debt_proj_abs.append(d)

lc, rc = st.columns(2)
with lc:
    fig_dp = go.Figure()
    fig_dp.add_trace(go.Scatter(x=list(range(11)), y=debt_proj_pct, mode="lines+markers", line=dict(color="#e74c3c", width=3), name="Dluh/HDP"))
    fig_dp.add_hline(y=60, line_dash="dash", annotation_text="Maastricht 60%", line_color="orange")
    fig_dp.update_layout(height=350, xaxis_title="Rok", yaxis_title="Dluh/HDP (%)")
    st.plotly_chart(fig_dp, use_container_width=True)
with rc:
    fig_da = go.Figure()
    fig_da.add_trace(go.Scatter(x=list(range(11)), y=debt_proj_abs, mode="lines+markers", fill="tozeroy", line=dict(color="#f59e0b", width=3), name="Dluh"))
    fig_da.update_layout(height=350, xaxis_title="Rok", yaxis_title=f"Dluh ({cur})")
    st.plotly_chart(fig_da, use_container_width=True)

st.subheader("📋 Detailní přehled rozpočtu")
summary_df = pd.concat([
    rev_df.assign(Sekce="Příjmy"),
    exp_df.assign(Sekce="Výdaje")
], ignore_index=True)
summary_df[f"Hodnota ({cur})"] = summary_df[f"Hodnota ({cur})"].map(lambda x: f"{x:,.1f}")
summary_df["% HDP"] = summary_df["% HDP"].map(lambda x: f"{x:.2f}%")
st.dataframe(summary_df[["Sekce", "Položka", f"Hodnota ({cur})", "% HDP"]], use_container_width=True, hide_index=True)

st.markdown("### Souhrn")
st.markdown(f"- Celkové příjmy: **{total_revenue:,.1f} {cur}** ({total_revenue/gdp*100:.1f}% HDP)")
st.markdown(f"- Celkové výdaje: **{total_expenditure:,.1f} {cur}** ({total_expenditure/gdp*100:.1f}% HDP)")
st.markdown(f"- Saldo: **{balance:,.1f} {cur}** ({balance_gdp_pct:+.1f}% HDP)")

st.markdown("---")
st.caption("⚠️ Výukový model. Kapitoly jsou detailnější než v původní verzi, ale stále jde o zjednodušenou aproximaci veřejných financí.")
