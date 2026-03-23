import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import datetime

st.set_page_config(page_title="Simulátor státního rozpočtu", layout="wide")
st.title("🏛️ Simulátor státního rozpočtu")
st.markdown("Centrální rozpočet (státní rozpočet) bez krajů, obcí a zdravotních pojišťoven.")

# ── PRESETY ──────────────────────────────────────────────────────────────────

PRESETS = {
    "Česká republika": dict(
        gdp=7800, pop=10.9, workforce=5.42, unemployment_rate=2.7,
        pensioners=2.90, outside_lf=2.45, avg_wage_month=46700,
        # Sociální zabezpečení (→ SR): důchodové + nemocenské + nezaměstnanost
        employer_social=24.8, employee_social=6.5,
        # Zdravotní pojištění (→ ZP, MIMO SR)
        employer_health=9.0, employee_health=4.5,
        income_tax_rate=15.0, corporate_tax=21.0,
        corp_profit_gdp_pct=15.0,
        vat_high=21.0, vat_low=12.0, vat_high_share=65.0,
        sr_share_social=100.0, sr_share_dpfo=60.0, sr_share_dppo=75.0,
        vat_sr_pct_gdp=5.3, excise_pct=2.2,
        transfers_received=120.0, capital_revenue=45.0,
        other_tax_revenue=35.0, non_tax_revenue=35.0,
        pension_month=21400, unemployment_benefit_month=14500,
        social_benefits_pct=2.6, education_pct=3.6, health_sr_pct=0.6,
        defense_pct=2.0, security_justice_pct=1.2, transport_pct=1.4,
        admin_pct=1.5, other_public_pct=1.9, agriculture_pct=0.7,
        industry_pct=0.9, culture_pct=0.4, housing_pct=0.3,
        environment_pct=0.4, research_pct=0.4, other_exp_pct=0.9,
        debt_to_gdp=43.3, interest_rate=2.8, currency="CZK (mld)",
    ),
    "Slovensko": dict(
        gdp=130, pop=5.46, workforce=2.60, unemployment_rate=5.5,
        pensioners=1.17, outside_lf=1.55, avg_wage_month=1600,
        employer_social=25.2, employee_social=9.4,
        employer_health=10.0, employee_health=4.0,
        income_tax_rate=19.0, corporate_tax=21.0,
        corp_profit_gdp_pct=15.0,
        vat_high=23.0, vat_low=10.0, vat_high_share=70.0,
        sr_share_social=100.0, sr_share_dpfo=65.0, sr_share_dppo=80.0,
        vat_sr_pct_gdp=6.8, excise_pct=2.5,
        transfers_received=2.5, capital_revenue=0.8,
        other_tax_revenue=0.6, non_tax_revenue=0.5,
        pension_month=680, unemployment_benefit_month=460,
        social_benefits_pct=3.2, education_pct=3.8, health_sr_pct=0.5,
        defense_pct=2.0, security_justice_pct=1.4, transport_pct=1.8,
        admin_pct=1.6, other_public_pct=2.5, agriculture_pct=0.9,
        industry_pct=0.7, culture_pct=0.4, housing_pct=0.3,
        environment_pct=0.5, research_pct=0.3, other_exp_pct=1.2,
        debt_to_gdp=59.7, interest_rate=3.6, currency="EUR (mld)",
    ),
    "Německo": dict(
        gdp=4100, pop=84.5, workforce=43.5, unemployment_rate=6.0,
        pensioners=21.5, outside_lf=15.8, avg_wage_month=4750,
        employer_social=12.4, employee_social=12.4,
        employer_health=8.4, employee_health=7.9,
        income_tax_rate=30.0, corporate_tax=30.0,
        corp_profit_gdp_pct=12.0,
        vat_high=19.0, vat_low=7.0, vat_high_share=75.0,
        sr_share_social=100.0, sr_share_dpfo=42.5, sr_share_dppo=50.0,
        vat_sr_pct_gdp=3.2, excise_pct=1.5,
        transfers_received=5.0, capital_revenue=12.0,
        other_tax_revenue=15.0, non_tax_revenue=25.0,
        pension_month=1600, unemployment_benefit_month=1150,
        social_benefits_pct=3.0, education_pct=0.8, health_sr_pct=5.0,
        defense_pct=1.5, security_justice_pct=0.5, transport_pct=1.0,
        admin_pct=1.0, other_public_pct=2.0, agriculture_pct=0.3,
        industry_pct=0.8, culture_pct=0.2, housing_pct=0.2,
        environment_pct=0.2, research_pct=0.6, other_exp_pct=1.5,
        debt_to_gdp=62.2, interest_rate=2.0, currency="EUR (mld)",
    ),
    "USA": dict(
        gdp=28700, pop=336.0, workforce=161.5, unemployment_rate=4.1,
        pensioners=57.0, outside_lf=110.3, avg_wage_month=5600,
        employer_social=6.2, employee_social=6.2,
        employer_health=1.45, employee_health=1.45,
        income_tax_rate=22.0, corporate_tax=21.0,
        corp_profit_gdp_pct=12.0,
        vat_high=0.0, vat_low=0.0, vat_high_share=100.0,
        sr_share_social=100.0, sr_share_dpfo=100.0, sr_share_dppo=100.0,
        vat_sr_pct_gdp=0.0, excise_pct=0.3,
        transfers_received=0.0, capital_revenue=50.0,
        other_tax_revenue=170.0, non_tax_revenue=200.0,
        pension_month=1950, unemployment_benefit_month=1450,
        social_benefits_pct=4.0, education_pct=0.3, health_sr_pct=5.5,
        defense_pct=3.4, security_justice_pct=0.4, transport_pct=0.5,
        admin_pct=0.4, other_public_pct=0.6, agriculture_pct=0.2,
        industry_pct=0.3, culture_pct=0.1, housing_pct=0.1,
        environment_pct=0.1, research_pct=0.5, other_exp_pct=0.5,
        debt_to_gdp=98.0, interest_rate=3.3, currency="USD (mld)",
    ),
    "Rusko": dict(
        gdp=198000, pop=146.0, workforce=73.5, unemployment_rate=2.4,
        pensioners=36.5, outside_lf=34.2, avg_wage_month=89000,
        employer_social=22.0, employee_social=0.0,
        employer_health=5.1, employee_health=0.0,
        income_tax_rate=13.0, corporate_tax=25.0,
        corp_profit_gdp_pct=15.0,
        vat_high=20.0, vat_low=10.0, vat_high_share=70.0,
        sr_share_social=0.0, sr_share_dpfo=0.0, sr_share_dppo=80.0,
        vat_sr_pct_gdp=5.0, excise_pct=1.3,
        transfers_received=100.0, capital_revenue=600.0,
        other_tax_revenue=5200.0, non_tax_revenue=10500.0,
        pension_month=24500, unemployment_benefit_month=13500,
        social_benefits_pct=0.5, education_pct=1.1, health_sr_pct=1.2,
        defense_pct=7.0, security_justice_pct=2.5, transport_pct=1.0,
        admin_pct=0.9, other_public_pct=1.8, agriculture_pct=0.5,
        industry_pct=0.8, culture_pct=0.3, housing_pct=0.4,
        environment_pct=0.2, research_pct=0.3, other_exp_pct=1.0,
        debt_to_gdp=16.7, interest_rate=8.5, currency="RUB (mld)",
    ),
    "Vlastní": dict(
        gdp=1000, pop=10.0, workforce=5.0, unemployment_rate=5.0,
        pensioners=2.0, outside_lf=2.74, avg_wage_month=2500,
        employer_social=20.0, employee_social=8.0,
        employer_health=5.0, employee_health=2.0,
        income_tax_rate=20.0, corporate_tax=20.0,
        corp_profit_gdp_pct=15.0,
        vat_high=20.0, vat_low=10.0, vat_high_share=65.0,
        sr_share_social=100.0, sr_share_dpfo=60.0, sr_share_dppo=75.0,
        vat_sr_pct_gdp=5.0, excise_pct=2.0,
        transfers_received=10.0, capital_revenue=5.0,
        other_tax_revenue=3.0, non_tax_revenue=3.0,
        pension_month=800, unemployment_benefit_month=500,
        social_benefits_pct=2.5, education_pct=3.5, health_sr_pct=0.5,
        defense_pct=2.0, security_justice_pct=1.2, transport_pct=1.4,
        admin_pct=1.5, other_public_pct=1.5, agriculture_pct=0.5,
        industry_pct=0.5, culture_pct=0.4, housing_pct=0.3,
        environment_pct=0.3, research_pct=0.3, other_exp_pct=0.5,
        debt_to_gdp=40.0, interest_rate=3.0, currency="jednotek (mld)",
    ),
}

# ── SIDEBAR ──────────────────────────────────────────────────────────────────

st.sidebar.header("Vyberte preset ekonomiky")
preset_name = st.sidebar.selectbox("Ekonomika", list(PRESETS.keys()))
p = PRESETS[preset_name]
cur = p["currency"]
big = "CZK" in cur or "RUB" in cur

st.sidebar.markdown("---")
st.sidebar.header("📊 Makro parametry")

gdp = st.sidebar.number_input(f"HDP ({cur})", min_value=1.0, value=float(p["gdp"]),
                               step=100.0 if big else 10.0, format="%.0f")
pop = st.sidebar.number_input("Populace (mil)", min_value=0.1, value=float(p["pop"]),
                               step=0.1, format="%.1f")
workforce = st.sidebar.number_input("Zaměstnaní (mil)", min_value=0.1,
                                     value=float(p["workforce"]), step=0.01, format="%.2f")
unemployment_rate = st.sidebar.number_input("Míra nezaměstnanosti (%)", min_value=0.0,
                                             max_value=50.0, value=float(p["unemployment_rate"]),
                                             step=0.1, format="%.1f")
pensioners = st.sidebar.number_input("Důchodci (mil)", min_value=0.0,
                                      value=float(p["pensioners"]), step=0.01, format="%.2f")
outside_lf = st.sidebar.number_input("Mimo pracovní sílu (mil)", min_value=0.0,
                                      value=float(p["outside_lf"]), step=0.01, format="%.2f")

labor_force = workforce / (1 - unemployment_rate / 100) if unemployment_rate < 100 else workforce
unemployed = labor_force - workforce
total_check = workforce + unemployed + pensioners + outside_lf
pop_diff = pop - total_check
if abs(pop_diff) > 0.05:
    st.sidebar.warning(f"⚠ Součet {total_check:.2f} ≠ populace {pop:.1f}, Δ{pop_diff:+.2f} mil")
else:
    st.sidebar.success(f"✅ Populace OK ({total_check:.2f} mil)")

st.sidebar.markdown("---")
st.sidebar.header("💰 Mzdy a dávky (měsíční)")
ws = 500.0 if big else 10.0
avg_wage_month = st.sidebar.number_input("Průměrná mzda", min_value=100.0,
                                          value=float(p["avg_wage_month"]), step=ws, format="%.0f")
pension_month = st.sidebar.number_input("Průměrný důchod", min_value=0.0,
                                         value=float(p["pension_month"]), step=ws, format="%.0f")
unemp_benefit_month = st.sidebar.number_input("Podpora v nezam.", min_value=0.0,
                                               value=float(p["unemployment_benefit_month"]),
                                               step=ws, format="%.0f")

# ── ZÁKONNÉ SAZBY ────────────────────────────────────────────────────────────

st.sidebar.markdown("---")
st.sidebar.header("⚖️ Zákonné sazby")

income_tax = st.sidebar.number_input("DPFO sazba (%)", min_value=0.0, max_value=60.0,
                                      value=float(p["income_tax_rate"]), step=0.5, format="%.1f")
corporate_tax = st.sidebar.number_input("DPPO sazba (%)", min_value=0.0, max_value=50.0,
                                         value=float(p["corporate_tax"]), step=0.5, format="%.1f")
corp_profit_gdp_pct = st.sidebar.number_input("Zdanitelný zisk (% HDP)", min_value=0.0,
                                               max_value=40.0,
                                               value=float(p["corp_profit_gdp_pct"]),
                                               step=0.5, format="%.1f")

# ── SOCIÁLNÍ ZABEZPEČENÍ (→ SR) ─────────────────────────────────────────────

st.sidebar.markdown("---")
st.sidebar.header("🏛️ Sociální zabezpečení (→ SR)")
st.sidebar.caption("Důchodové, nemocenské, nezaměstnanost – jde do státního rozpočtu")

employer_social = st.sidebar.number_input("Zaměstnavatel – sociální (%)", min_value=0.0,
                                           max_value=50.0, value=float(p["employer_social"]),
                                           step=0.1, format="%.1f")
employee_social = st.sidebar.number_input("Zaměstnanec – sociální (%)", min_value=0.0,
                                           max_value=30.0, value=float(p["employee_social"]),
                                           step=0.1, format="%.1f")

# ── ZDRAVOTNÍ POJIŠTĚNÍ (→ MIMO SR) ─────────────────────────────────────────

st.sidebar.markdown("---")
st.sidebar.header("🏥 Zdravotní pojištění (→ mimo SR)")
st.sidebar.caption("Jde zdravotním pojišťovnám, NE do státního rozpočtu")

employer_health = st.sidebar.number_input("Zaměstnavatel – zdravotní (%)", min_value=0.0,
                                           max_value=30.0, value=float(p["employer_health"]),
                                           step=0.1, format="%.1f")
employee_health = st.sidebar.number_input("Zaměstnanec – zdravotní (%)", min_value=0.0,
                                           max_value=20.0, value=float(p["employee_health"]),
                                           step=0.1, format="%.1f")

# ── DPH ──────────────────────────────────────────────────────────────────────

st.sidebar.markdown("---")
st.sidebar.header("🧾 DPH – zákonné sazby")

vat_high = st.sidebar.number_input("Základní sazba (%)", min_value=0.0, max_value=35.0,
                                    value=float(p["vat_high"]), step=0.5, format="%.1f")
vat_low = st.sidebar.number_input("Snížená sazba (%)", min_value=0.0, max_value=25.0,
                                   value=float(p["vat_low"]), step=0.5, format="%.1f")
vat_high_share = st.sidebar.number_input("Podíl v základní sazbě (%)", min_value=0.0,
                                          max_value=100.0, value=float(p["vat_high_share"]),
                                          step=1.0, format="%.0f")

# ── SDÍLENÍ DANÍ → SR ───────────────────────────────────────────────────────

st.sidebar.markdown("---")
st.sidebar.header("🔀 Sdílení daní → státní rozpočet")
with st.sidebar.expander("Co to je?"):
    st.markdown("""
Daňové výnosy se dělí mezi stát, kraje a obce. Tyto koeficienty určují,
kolik z celkového výnosu dané daně jde do státního rozpočtu.
- ČR: Pojistné 100%, DPFO sdílení daně ~60% SR, DPPO ~75% SR, DPH zadáno přímo
- DE: DPFO 42.5%, DPPO 50% (federální podíl)
- USA: Vše 100% (federální daně, žádné sdílení)
""")

sr_share_social = st.sidebar.number_input("Pojistné → SR (%)", min_value=0.0, max_value=100.0,
                                           value=float(p["sr_share_social"]), step=1.0, format="%.0f")
sr_share_dpfo = st.sidebar.number_input("DPFO → SR (%)", min_value=0.0, max_value=100.0,
                                         value=float(p["sr_share_dpfo"]), step=1.0, format="%.0f")
sr_share_dppo = st.sidebar.number_input("DPPO → SR (%)", min_value=0.0, max_value=100.0,
                                         value=float(p["sr_share_dppo"]), step=1.0, format="%.0f")
vat_sr_pct_gdp = st.sidebar.number_input("DPH do SR (% HDP)", min_value=0.0, max_value=15.0,
                                           value=float(p["vat_sr_pct_gdp"]), step=0.1, format="%.1f")
excise_pct = st.sidebar.number_input("Spotřební daně do SR (% HDP)", min_value=0.0,
                                      max_value=8.0, value=float(p["excise_pct"]),
                                      step=0.1, format="%.1f")

# ── OSTATNÍ PŘÍJMY SR ────────────────────────────────────────────────────────

st.sidebar.markdown("---")
st.sidebar.header("📥 Ostatní příjmy SR")
amt = "(mld)" if not big else "(mld)"

transfers_received = st.sidebar.number_input(f"Přijaté transfery ({cur})", min_value=0.0,
                                              value=float(p["transfers_received"]),
                                              step=1.0 if not big else 10.0, format="%.1f")
capital_revenue = st.sidebar.number_input(f"Kapitálové příjmy ({cur})", min_value=0.0,
                                           value=float(p["capital_revenue"]),
                                           step=1.0 if not big else 10.0, format="%.1f")
other_tax_revenue = st.sidebar.number_input(f"Ostatní daňové ({cur})", min_value=0.0,
                                             value=float(p["other_tax_revenue"]),
                                             step=1.0 if not big else 10.0, format="%.1f")
non_tax_revenue = st.sidebar.number_input(f"Nedaňové příjmy ({cur})", min_value=0.0,
                                           value=float(p["non_tax_revenue"]),
                                           step=1.0 
