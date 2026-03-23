import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import datetime

st.set_page_config(page_title="Simulátor státního rozpočtu", layout="wide")
st.title("🏛️ Simulátor státního rozpočtu")
st.markdown("*Centrální rozpočet (státní rozpočet) – bez krajů, obcí a zdravotních pojišťoven*")

# ============================================================
# PRESETS – kalibrováno na STÁTNÍ ROZPOČET (central government) 2024
# ČR: MFČR skutečnost 2024, příjmy 2 056 mld, výdaje 2 327 mld, saldo -271 mld
# SR: MF SR 2024, DE: Bundeshaushalt 2024, USA: CBO FY2024, RU: MinFin RF 2024
# ============================================================
#
# MODEL: Příjmy se počítají HYBRIDNĚ:
#   - Pojistné, DPFO = ze mzdového fondu × sazba × koeficient (kolik jde do SR)
#   - DPH, DPPO, spotřební = z HDP × efektivní sazba
#   - Ostatní = přímo v mld (nebo % HDP)
# Výdaje: většina jako % HDP (snadná úprava), důchody ze struktury populace
# ============================================================

PRESETS = {
    "🇨🇿 Česká republika": dict(
        gdp=7800, pop=10.9, workforce=5.42, unemployment_rate=2.7,
        pensioners=2.90, outside_lf=2.45,
        avg_wage_month=46700,
        # Sazby (zákonné)
        income_tax_rate=15.0, employer_social=33.8, employee_social=11.6,
        corporate_tax=21.0,
        vat_high=21.0, vat_low=12.0, vat_high_share=65.0,
        # Koeficienty: kolik z celkového výnosu jde do STÁTNÍHO rozpočtu
        # Pojistné: téměř vše (810/810), DPFO: sdílená daň ~60% SR, DPPO: ~75% SR
        sr_share_social=100.0, sr_share_dpfo=60.0, sr_share_dppo=75.0,
        # DPH – efektivní výnos pro SR (po sdílení s obcemi/kraji): ~5.3% HDP
        vat_sr_pct_gdp=5.3,
        # Spotřební daně: 2.2% HDP do SR
        excise_pct=2.2,
        # Ostatní příjmy SR (mld)
        transfers_received=120.0, capital_revenue=45.0,
        other_tax_revenue=35.0, nontax_revenue=35.0,
        # Důchody
        pension_month=21400, unemployment_benefit_month=14500,
        # Výdaje (% HDP) – JEN centrální rozpočet
        social_benefits_pct=2.6,  # nemocenská, SSP, hmotná nouze (bez důchodů)
        education_pct=3.6, health_sr_pct=0.6,
        defense_pct=2.0, security_justice_pct=1.2,
        transport_pct=1.4, admin_pct=1.5,
        other_public_pct=1.9, agriculture_pct=0.7,
        industry_pct=0.9, culture_pct=0.4,
        housing_pct=0.3, environment_pct=0.4,
        research_pct=0.4, other_exp_pct=0.9,
        # Dluh
        debt_to_gdp=43.3, interest_rate=2.8,
        currency="CZK mld"
    ),
    "🇸🇰 Slovensko": dict(
        gdp=130, pop=5.46, workforce=2.60, unemployment_rate=5.5,
        pensioners=1.17, outside_lf=1.55,
        avg_wage_month=1600,
        income_tax_rate=19.0, employer_social=35.2, employee_social=13.4,
        corporate_tax=21.0,
        vat_high=23.0, vat_low=10.0, vat_high_share=70.0,
        sr_share_social=100.0, sr_share_dpfo=65.0, sr_share_dppo=80.0,
        vat_sr_pct_gdp=6.8,
        excise_pct=2.5,
        transfers_received=2.5, capital_revenue=0.8,
        other_tax_revenue=0.6, nontax_revenue=0.5,
        pension_month=680, unemployment_benefit_month=460,
        social_benefits_pct=3.2, education_pct=3.8, health_sr_pct=0.5,
        defense_pct=2.0, security_justice_pct=1.4,
        transport_pct=1.8, admin_pct=1.6,
        other_public_pct=2.5, agriculture_pct=0.9,
        industry_pct=0.7, culture_pct=0.4,
        housing_pct=0.3, environment_pct=0.5,
        research_pct=0.3, other_exp_pct=1.2,
        debt_to_gdp=59.7, interest_rate=3.6,
        currency="EUR mld"
    ),
    "🇩🇪 Německo": dict(
        gdp=4100, pop=84.5, workforce=43.5, unemployment_rate=6.0,
        pensioners=21.5, outside_lf=15.8,
        avg_wage_month=4750,
        income_tax_rate=30.0, employer_social=20.8, employee_social=20.3,
        corporate_tax=30.0,
        vat_high=19.0, vat_low=7.0, vat_high_share=75.0,
        sr_share_social=100.0, sr_share_dpfo=42.5, sr_share_dppo=50.0,
        vat_sr_pct_gdp=3.2,
        excise_pct=1.5,
        transfers_received=5.0, capital_revenue=12.0,
        other_tax_revenue=15.0, nontax_revenue=25.0,
        pension_month=1600, unemployment_benefit_month=1150,
        social_benefits_pct=3.0, education_pct=0.8, health_sr_pct=5.0,
        defense_pct=1.5, security_justice_pct=0.5,
        transport_pct=1.0, admin_pct=1.0,
        other_public_pct=2.0, agriculture_pct=0.3,
        industry_pct=0.8, culture_pct=0.2,
        housing_pct=0.2, environment_pct=0.2,
        research_pct=0.6, other_exp_pct=1.5,
        debt_to_gdp=62.2, interest_rate=2.0,
        currency="EUR mld"
    ),
    "🇺🇸 USA": dict(
        gdp=28700, pop=336.0, workforce=161.5, unemployment_rate=4.1,
        pensioners=57.0, outside_lf=110.3,
        avg_wage_month=5600,
        income_tax_rate=22.0, employer_social=7.65, employee_social=7.65,
        corporate_tax=21.0,
        vat_high=0.0, vat_low=0.0, vat_high_share=100.0,
        sr_share_social=100.0, sr_share_dpfo=100.0, sr_share_dppo=100.0,
        vat_sr_pct_gdp=0.0,
        excise_pct=0.3,
        transfers_received=0.0, capital_revenue=50.0,
        other_tax_revenue=170.0, nontax_revenue=200.0,
        pension_month=1950, unemployment_benefit_month=1450,
        social_benefits_pct=4.0, education_pct=0.3, health_sr_pct=5.5,
        defense_pct=3.4, security_justice_pct=0.4,
        transport_pct=0.5, admin_pct=0.4,
        other_public_pct=0.6, agriculture_pct=0.2,
        industry_pct=0.3, culture_pct=0.1,
        housing_pct=0.1, environment_pct=0.1,
        research_pct=0.5, other_exp_pct=0.5,
        debt_to_gdp=98.0, interest_rate=3.3,
        currency="USD mld"
    ),
    "🇷🇺 Rusko": dict(
        gdp=198000, pop=146.0, workforce=73.5, unemployment_rate=2.4,
        pensioners=36.5, outside_lf=34.2,
        avg_wage_month=89000,
        income_tax_rate=13.0, employer_social=30.0, employee_social=0.0,
        corporate_tax=25.0,
        vat_high=20.0, vat_low=10.0, vat_high_share=70.0,
        sr_share_social=0.0, sr_share_dpfo=0.0, sr_share_dppo=80.0,
        vat_sr_pct_gdp=5.0,
        excise_pct=1.3,
        transfers_received=100.0, capital_revenue=600.0,
        other_tax_revenue=5200.0, nontax_revenue=10500.0,
        pension_month=24500, unemployment_benefit_month=13500,
        social_benefits_pct=0.5, education_pct=1.1, health_sr_pct=1.2,
        defense_pct=7.0, security_justice_pct=2.5,
        transport_pct=1.0, admin_pct=0.9,
        other_public_pct=1.8, agriculture_pct=0.5,
        industry_pct=0.8, culture_pct=0.3,
        housing_pct=0.4, environment_pct=0.2,
        research_pct=0.3, other_exp_pct=1.0,
        debt_to_gdp=16.7, interest_rate=8.5,
        currency="RUB mld"
    ),
    "⚙️ Vlastní": dict(
        gdp=1000, pop=10.0, workforce=5.0, unemployment_rate=5.0,
        pensioners=2.0, outside_lf=2.74,
        avg_wage_month=2500,
        income_tax_rate=20.0, employer_social=25.0, employee_social=10.0,
        corporate_tax=20.0,
        vat_high=20.0, vat_low=10.0, vat_high_share=65.0,
        sr_share_social=100.0, sr_share_dpfo=60.0, sr_share_dppo=75.0,
        vat_sr_pct_gdp=5.0,
        excise_pct=2.0,
        transfers_received=10.0, capital_revenue=5.0,
        other_tax_revenue=3.0, nontax_revenue=3.0,
        pension_month=800, unemployment_benefit_month=500,
        social_benefits_pct=2.5, education_pct=3.5, health_sr_pct=0.5,
        defense_pct=2.0, security_justice_pct=1.2,
        transport_pct=1.4, admin_pct=1.5,
        other_public_pct=1.5, agriculture_pct=0.5,
        industry_pct=0.5, culture_pct=0.4,
        housing_pct=0.3, environment_pct=0.3,
        research_pct=0.3, other_exp_pct=0.5,
        debt_to_gdp=40.0, interest_rate=3.0,
        currency="jednotek"
    )
}

# --- SIDEBAR ---
st.sidebar.header("Vyberte preset ekonomiky")
preset_name = st.sidebar.selectbox("Ekonomika", list(PRESETS.keys()))
p = PRESETS[preset_name]
cur = p["currency"]
big = "CZK" in cur or "RUB" in cur

st.sidebar.markdown("---")
st.sidebar.header("📊 Makro parametry")
gdp = st.sidebar.number_input(f"HDP ({cur})", min_value=1.0, value=float(p["gdp"]), step=100.0 if big else 10.0, format="%.0f")
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
st.sidebar.header("💵 Mzdy a dávky (měsíčně)")
ws = 500.0 if big else 10.0
avg_wage_month = st.sidebar.number_input("Průměrná mzda", min_value=100.0, value=float(p["avg_wage_month"]), step=ws, format="%.0f")
pension_month = st.sidebar.number_input("Průměrný důchod", min_value=0.0, value=float(p["pension_month"]), step=ws, format="%.0f")
unemp_benefit_month = st.sidebar.number_input("Podpora v nezam.", min_value=0.0, value=float(p["unemployment_benefit_month"]), step=ws, format="%.0f")

st.sidebar.markdown("---")
st.sidebar.header("💰 Zákonné sazby (%)")
income_tax = st.sidebar.number_input("DPFO (sazba)", min_value=0.0, max_value=60.0, value=float(p["income_tax_rate"]), step=0.5, format="%.1f")
employer_social = st.sidebar.number_input("Pojistné – zaměstnavatel", min_value=0.0, max_value=60.0, value=float(p["employer_social"]), step=0.5, format="%.1f")
employee_social = st.sidebar.number_input("Pojistné – zaměstnanec", min_value=0.0, max_value=40.0, value=float(p["employee_social"]), step=0.5, format="%.1f")
corporate_tax = st.sidebar.number_input("DPPO (sazba)", min_value=0.0, max_value=50.0, value=float(p["corporate_tax"]), step=0.5, format="%.1f")

st.sidebar.markdown("---")
st.sidebar.header("🛒 DPH (zákonné sazby)")
vat_high = st.sidebar.number_input("Základní sazba (%)", min_value=0.0, max_value=35.0, value=float(p["vat_high"]), step=0.5, format="%.1f")
vat_low = st.sidebar.number_input("Snížená sazba (%)", min_value=0.0, max_value=25.0, value=float(p["vat_low"]), step=0.5, format="%.1f")
vat_high_share = st.sidebar.number_input("Podíl v základní sazbě (%)", min_value=0.0, max_value=100.0, value=float(p["vat_high_share"]), step=1.0, format="%.0f")

st.sidebar.markdown("---")
st.sidebar.header("🔀 Sdílení daní → státní rozpočet (%)")
with st.sidebar.expander("ℹ️ Co to je?"):
    st.markdown("""
Daňové výnosy se dělí mezi stát, kraje a obce. Tyto koeficienty určují,
kolik % z celkového výnosu dané daně jde do **státního rozpočtu**:
- **ČR**: Pojistné 100%, DPFO ~60%, DPPO ~75%, DPH zadáno přímo
- **DE**: DPFO 42.5%, DPPO 50% (federální podíl)
- **USA**: Vše 100% (federální daně, žádné sdílení)
""")
sr_share_social = st.sidebar.number_input("Pojistné → SR (%)", min_value=0.0, max_value=100.0, value=float(p["sr_share_social"]), step=1.0, format="%.0f")
sr_share_dpfo = st.sidebar.number_input("DPFO → SR (%)", min_value=0.0, max_value=100.0, value=float(p["sr_share_dpfo"]), step=1.0, format="%.0f")
sr_share_dppo = st.sidebar.number_input("DPPO → SR (%)", min_value=0.0, max_value=100.0, value=float(p["sr_share_dppo"]), step=1.0, format="%.0f")
vat_sr_pct_gdp = st.sidebar.number_input("DPH do SR (% HDP)", min_value=0.0, max_value=15.0, value=float(p["vat_sr_pct_gdp"]), step=0.1, format="%.1f")
excise_pct = st.sidebar.number_input("Spotřební daně do SR (% HDP)", min_value=0.0, max_value=8.0, value=float(p["excise_pct"]), step=0.1, format="%.1f")

st.sidebar.markdown("---")
st.sidebar.header("📥 Ostatní příjmy SR")
amt = "mld" if not big else "mld"
transfers_received = st.sidebar.number_input(f"Přijaté transfery ({cur})", min_value=0.0, value=float(p["transfers_received"]), step=1.0 if not big else 10.0, format="%.1f")
capital_revenue = st.sidebar.number_input(f"Kapitálové příjmy ({cur})", min_value=0.0, value=float(p["capital_revenue"]), step=1.0 if not big else 10.0, format="%.1f")
other_tax_revenue = st.sidebar.number_input(f"Ostatní daňové ({cur})", min_value=0.0, value=float(p["other_tax_revenue"]), step=1.0 if not big else 10.0, format="%.1f")
nontax_revenue = st.sidebar.number_input(f"Nedaňové příjmy ({cur})", min_value=0.0, value=float(p["nontax_revenue"]), step=1.0 if not big else 10.0, format="%.1f")

st.sidebar.markdown("---")
st.sidebar.header("📤 Výdaje SR (% HDP)")
social_benefits_pct = st.sidebar.number_input("Sociální dávky (bez důchodů)", min_value=0.0, max_value=10.0, value=float(p["social_benefits_pct"]), step=0.1, format="%.1f")
education_pct = st.sidebar.number_input("Vzdělávání", min_value=0.0, max_value=10.0, value=float(p["education_pct"]), step=0.1, format="%.1f")
health_sr_pct = st.sidebar.number_input("Zdravotnictví (jen SR)", min_value=0.0, max_value=12.0, value=float(p["health_sr_pct"]), step=0.1, format="%.1f")
defense_pct = st.sidebar.number_input("Obrana", min_value=0.0, max_value=12.0, value=float(p["defense_pct"]), step=0.1, format="%.1f")
security_justice_pct = st.sidebar.number_input("Bezpečnost a justice", min_value=0.0, max_value=6.0, value=float(p["security_justice_pct"]), step=0.1, format="%.1f")
transport_pct = st.sidebar.number_input("Doprava a infrastruktura", min_value=0.0, max_value=6.0, value=float(p["transport_pct"]), step=0.1, format="%.1f")
admin_pct = st.sidebar.number_input("Veřejná správa", min_value=0.0, max_value=6.0, value=float(p["admin_pct"]), step=0.1, format="%.1f")
other_public_pct = st.sidebar.number_input("Ostatní veřejné služby", min_value=0.0, max_value=6.0, value=float(p["other_public_pct"]), step=0.1, format="%.1f")
agriculture_pct = st.sidebar.number_input("Zemědělství", min_value=0.0, max_value=4.0, value=float(p["agriculture_pct"]), step=0.1, format="%.1f")
industry_pct = st.sidebar.number_input("Průmysl a podnikání", min_value=0.0, max_value=4.0, value=float(p["industry_pct"]), step=0.1, format="%.1f")
culture_pct = st.sidebar.number_input("Kultura, sport, média", min_value=0.0, max_value=3.0, value=float(p["culture_pct"]), step=0.1, format="%.1f")
housing_pct = st.sidebar.number_input("Bydlení a územní rozvoj", min_value=0.0, max_value=3.0, value=float(p["housing_pct"]), step=0.1, format="%.1f")
environment_pct = st.sidebar.number_input("Životní prostředí", min_value=0.0, max_value=3.0, value=float(p["environment_pct"]), step=0.1, format="%.1f")
research_pct = st.sidebar.number_input("Výzkum a vývoj", min_value=0.0, max_value=3.0, value=float(p["research_pct"]), step=0.1, format="%.1f")
other_exp_pct = st.sidebar.number_input("Ostatní výdaje", min_value=0.0, max_value=5.0, value=float(p["other_exp_pct"]), step=0.1, format="%.1f")

st.sidebar.markdown("---")
st.sidebar.header("🏦 Státní dluh")
debt_to_gdp = st.sidebar.number_input("Dluh/HDP (%)", min_value=0.0, max_value=250.0, value=float(p["debt_to_gdp"]), step=0.5, format="%.1f")
interest_rate = st.sidebar.number_input("Průměrná úroková sazba (%)", min_value=0.0, max_value=20.0, value=float(p["interest_rate"]), step=0.1, format="%.1f")

# ================= VÝPOČTY =================
avg_wage = avg_wage_month * 12
total_wage_bill = workforce * 1e6 * avg_wage / 1e9  # mld

# Celkový výnos pojistného (zaměstnavatel + zaměstnanec)
total_social_full = total_wage_bill * (employer_social + employee_social) / 100
social_sr = total_social_full * sr_share_social / 100

# DPFO – z efektivního mzdového fondu (slevy, odpočty → ~50-60% efektivní sazba)
dpfo_eff_rate = income_tax * 0.55  # efektivní sazba je cca 55% nominální (slevy na poplatníka atd.)
dpfo_full = total_wage_bill * dpfo_eff_rate / 100
dpfo_sr = dpfo_full * sr_share_dpfo / 100

# DPPO – z HDP přes ziskovou marži
corp_profit_base = gdp * 0.20  # ~20% HDP je zdanitelný zisk
dppo_full = corp_profit_base * corporate_tax / 100
dppo_sr = dppo_full * sr_share_dppo / 100

# DPH – přímo jako % HDP (po sdílení)
vat_sr = gdp * vat_sr_pct_gdp / 100

# Spotřební daně
excise_sr = gdp * excise_pct / 100

revenue_items = {
    "Pojistné na soc. zabezpečení": social_sr,
    "DPH": vat_sr,
    "Daň z příjmů PO (DPPO)": dppo_sr,
    "Daň z příjmů FO (DPFO)": dpfo_sr,
    "Spotřební daně": excise_sr,
    "Přijaté transfery (EU aj.)": transfers_received,
    "Kapitálové příjmy": capital_revenue,
    "Ostatní daňové příjmy": other_tax_revenue,
    "Nedaňové příjmy": nontax_revenue,
}
total_revenue = sum(revenue_items.values())

# VÝDAJE
pension_spending = pensioners * 1e6 * pension_month * 12 / 1e9
unemp_spending = unemployed * 1e6 * unemp_benefit_month * 12 / 1e9
social_benefits = gdp * social_benefits_pct / 100
education_sp = gdp * education_pct / 100
health_sp = gdp * health_sr_pct / 100
defense_sp = gdp * defense_pct / 100
security_sp = gdp * security_justice_pct / 100
transport_sp = gdp * transport_pct / 100
admin_sp = gdp * admin_pct / 100
other_public_sp = gdp * other_public_pct / 100
agriculture_sp = gdp * agriculture_pct / 100
industry_sp = gdp * industry_pct / 100
culture_sp = gdp * culture_pct / 100
housing_sp = gdp * housing_pct / 100
environment_sp = gdp * environment_pct / 100
research_sp = gdp * research_pct / 100
other_exp_sp = gdp * other_exp_pct / 100
debt_total = gdp * debt_to_gdp / 100
interest_sp = debt_total * interest_rate / 100

expenditure_items = {
    "Důchody": pension_spending,
    "Podpora v nezaměstnanosti": unemp_spending,
    "Sociální dávky (ostatní)": social_benefits,
    "Vzdělávání": education_sp,
    "Zdravotnictví (SR)": health_sp,
    "Obrana": defense_sp,
    "Bezpečnost a justice": security_sp,
    "Doprava a infrastruktura": transport_sp,
    "Veřejná správa": admin_sp,
    "Ostatní veřejné služby": other_public_sp,
    "Zemědělství": agriculture_sp,
    "Průmysl a podnikání": industry_sp,
    "Kultura, sport, média": culture_sp,
    "Bydlení a územní rozvoj": housing_sp,
    "Životní prostředí": environment_sp,
    "Výzkum a vývoj": research_sp,
    "Ostatní výdaje": other_exp_sp,
    "Služba státního dluhu": interest_sp,
}
total_expenditure = sum(expenditure_items.values())

balance = total_revenue - total_expenditure
balance_gdp_pct = (balance / gdp * 100) if gdp > 0 else 0
debt_next = debt_total - balance
debt_next_pct = (debt_next / gdp * 100) if gdp > 0 else 0

# ================= ZOBRAZENÍ =================
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Příjmy SR", f"{total_revenue:,.0f} {cur}", delta=f"{total_revenue/gdp*100:.1f}% HDP")
c2.metric("Výdaje SR", f"{total_expenditure:,.0f} {cur}", delta=f"{total_expenditure/gdp*100:.1f}% HDP")
c3.metric("Saldo", f"{balance:,.0f} {cur}", delta=f"{balance_gdp_pct:+.1f}% HDP",
          delta_color="normal" if balance >= 0 else "inverse")
c4.metric("Státní dluh", f"{debt_total:,.0f} {cur}", delta=f"{debt_to_gdp:.1f}% HDP", delta_color="off")
c5.metric("Dluh po roce", f"{debt_next:,.0f} {cur}",
          delta=f"{debt_next_pct:.1f}% HDP ({debt_next_pct - debt_to_gdp:+.1f} p.b.)", delta_color="inverse")

st.markdown("---")
st.subheader("👥 Struktura populace")
pc = st.columns(6)
pc[0].metric("Zaměstnaní", f"{workforce:.2f} mil", delta=f"{workforce/pop*100:.1f}%", delta_color="off")
pc[1].metric("Nezaměstnaní", f"{unemployed:.2f} mil", delta=f"{unemployment_rate:.1f}%", delta_color="off")
pc[2].metric("Důchodci", f"{pensioners:.2f} mil", delta=f"{pensioners/pop*100:.1f}%", delta_color="off")
pc[3].metric("Mimo prac. sílu", f"{outside_lf:.2f} mil", delta=f"{outside_lf/pop*100:.1f}%", delta_color="off")
pc[4].metric("Součet", f"{total_check:.2f} mil")
pc[5].metric("Populace", f"{pop:.1f} mil",
             delta=f"Δ {pop_diff:+.2f}" if abs(pop_diff) > 0.05 else "✅ OK", delta_color="off")

st.markdown("---")

# GRAFY
col_l, col_r = st.columns(2)
with col_l:
    st.subheader("📥 Struktura příjmů SR")
    fig_rev = px.pie(names=list(revenue_items.keys()), values=list(revenue_items.values()),
                     hole=0.45, color_discrete_sequence=px.colors.qualitative.Set3)
    fig_rev.update_layout(height=480)
    st.plotly_chart(fig_rev, use_container_width=True)
with col_r:
    st.subheader("📤 Struktura výdajů SR")
    fig_exp = px.pie(names=list(expenditure_items.keys()), values=list(expenditure_items.values()),
                     hole=0.45, color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_exp.update_layout(height=480)
    st.plotly_chart(fig_exp, use_container_width=True)

# Sloupcové grafy
st.subheader("📊 Příjmy podle kapitol")
rev_df = pd.DataFrame({
    "Položka": list(revenue_items.keys()),
    f"Hodnota ({cur})": list(revenue_items.values()),
    "% HDP": [v / gdp * 100 for v in revenue_items.values()]
}).sort_values(f"Hodnota ({cur})", ascending=True)
fig_rb = px.bar(rev_df, y="Položka", x=f"Hodnota ({cur})", orientation="h",
                text=rev_df[f"Hodnota ({cur})"].map(lambda x: f"{x:,.0f}"),
                color=f"Hodnota ({cur})", color_continuous_scale="Greens")
fig_rb.update_layout(height=420, showlegend=False)
st.plotly_chart(fig_rb, use_container_width=True)

st.subheader("📊 Výdaje podle kapitol")
exp_df = pd.DataFrame({
    "Položka": list(expenditure_items.keys()),
    f"Hodnota ({cur})": list(expenditure_items.values()),
    "% HDP": [v / gdp * 100 for v in expenditure_items.values()]
}).sort_values(f"Hodnota ({cur})", ascending=True)
fig_eb = px.bar(exp_df, y="Položka", x=f"Hodnota ({cur})", orientation="h",
                text=exp_df[f"Hodnota ({cur})"].map(lambda x: f"{x:,.0f}"),
                color=f"Hodnota ({cur})", color_continuous_scale="Reds")
fig_eb.update_layout(height=520, showlegend=False)
st.plotly_chart(fig_eb, use_container_width=True)

# Dluhová projekce
st.subheader("📈 10letá projekce státního dluhu")
debt_proj_pct, debt_proj_abs = [debt_to_gdp], [debt_total]
d = debt_total
primary_exp = total_expenditure - interest_sp
for _ in range(10):
    ai = d * interest_rate / 100
    bal_y = total_revenue - (primary_exp + ai)
    d = d - bal_y
    debt_proj_pct.append((d / gdp * 100) if gdp > 0 else 0)
    debt_proj_abs.append(d)

lc, rc = st.columns(2)
with lc:
    fig_dp = go.Figure()
    fig_dp.add_trace(go.Scatter(x=list(range(11)), y=debt_proj_pct, mode="lines+markers",
                                line=dict(color="#e74c3c", width=3), name="Dluh/HDP"))
    fig_dp.add_hline(y=60, line_dash="dash", annotation_text="Maastricht 60%", line_color="orange")
    fig_dp.update_layout(height=350, xaxis_title="Rok", yaxis_title="Dluh/HDP (%)")
    st.plotly_chart(fig_dp, use_container_width=True)
with rc:
    fig_da = go.Figure()
    fig_da.add_trace(go.Scatter(x=list(range(11)), y=debt_proj_abs, mode="lines+markers",
                                fill="tozeroy", line=dict(color="#f59e0b", width=3), name="Dluh"))
    fig_da.update_layout(height=350, xaxis_title="Rok", yaxis_title=f"Dluh ({cur})")
    st.plotly_chart(fig_da, use_container_width=True)

# Detailní tabulka
st.subheader("📋 Detailní přehled")
all_items = []
for k, v in revenue_items.items():
    all_items.append({"Sekce": "📥 Příjmy", "Položka": k, f"Hodnota ({cur})": f"{v:,.0f}", "% HDP": f"{v/gdp*100:.2f}%"})
all_items.append({"Sekce": "📥 Příjmy", "Položka": "CELKEM PŘÍJMY", f"Hodnota ({cur})": f"{total_revenue:,.0f}", "% HDP": f"{total_revenue/gdp*100:.1f}%"})
for k, v in expenditure_items.items():
    all_items.append({"Sekce": "📤 Výdaje", "Položka": k, f"Hodnota ({cur})": f"{v:,.0f}", "% HDP": f"{v/gdp*100:.2f}%"})
all_items.append({"Sekce": "📤 Výdaje", "Položka": "CELKEM VÝDAJE", f"Hodnota ({cur})": f"{total_expenditure:,.0f}", "% HDP": f"{total_expenditure/gdp*100:.1f}%"})
all_items.append({"Sekce": "⚖️", "Položka": "SALDO", f"Hodnota ({cur})": f"{balance:,.0f}", "% HDP": f"{balance_gdp_pct:+.1f}%"})

st.dataframe(pd.DataFrame(all_items), use_container_width=True, hide_index=True)

st.markdown("---")
st.caption(f"""⚠️ Výukový model – zjednodušená aproximace STÁTNÍHO ROZPOČTU (centrální vláda).
Nezahrnuje rozpočty krajů, obcí ani zdravotních pojišťoven.
Presety kalibrované na data 2024: ČR – MFČR (příjmy 2 056, výdaje 2 327, saldo −271 mld CZK) |
SR – MF SR | DE – Bundeshaushalt | USA – CBO FY2024 | RU – MinFin RF.
© {datetime.datetime.now().year}""")
