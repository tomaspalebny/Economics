
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Predátorské ceny – AKZO & moderní test", layout="wide", page_icon="⚖️")

# ── Presets ──────────────────────────────────────────────────────────────
PRESETS = {
    "ChemPro vs EcoChem (modelový případ)": dict(
        total_output=10_000, catalog_price=11.0,
        variable_costs=90_000, avoidable_costs=120_000,
        extended_costs=150_000, full_costs=210_000,
        wholesale_price=10.0, competitor_lraic=14.0,
        email_text="„Sledujte cenovou politiku EcoChem – na každé pondělí připravte analýzu. Musíme držet katalogovou cenu vždycky pod nimi. Ztráty budeme prozatím krýt loňskými rezervami."",
        context="Na trhu průmyslových chemikálií v ČR působí dominantní firma ChemPro a menší konkurent EcoChem. ChemPro reaguje na vstup EcoChem agresivním snížením cen produktu Chemix20. ÚOHS zahájil šetření.",
        dominant="ChemPro", competitor="EcoChem", product="Chemix20",
    ),
    "AKZO vs ECS (EU, C-62/86)": dict(
        total_output=50_000, catalog_price=1.80,
        variable_costs=70_000, avoidable_costs=78_000,
        extended_costs=85_000, full_costs=110_000,
        wholesale_price=0.0, competitor_lraic=2.40,
        email_text="Interní dokumenty AKZO ukazovaly záměr eliminovat ECS z trhu plastových přísad – „We must take every step to ensure ECS does not survive in the flour additives market."",
        context="AKZO (C-62/86, 1991): AKZO Chemie, dominantní hráč na trhu organických peroxidů, reagoval na vstup ECS na trh moučných přísad selektivními cenovými škrty pod úrovní nákladů. Komise uložila pokutu 10 mil. ECU (sníženo na 7,5 mil.).",
        dominant="AKZO Chemie", competitor="ECS", product="Benzoyl peroxide",
    ),
    "France Télécom / Wanadoo (2003/2009)": dict(
        total_output=500_000, catalog_price=29.90,
        variable_costs=12_000_000, avoidable_costs=13_500_000,
        extended_costs=14_500_000, full_costs=18_000_000,
        wholesale_price=0.0, competitor_lraic=35.0,
        email_text="Interní strategické dokumenty Wanadoo potvrzovaly záměr předběhnout konkurenci na rodícím se trhu vysokorychlostního internetu: „pre-empt the market during a key phase in its development."",
        context="Wanadoo Interactive (dceřiná společnost France Télécom) stanovila predátorské ceny služeb eXtense a Wanadoo ADSL na francouzském trhu vysokorychlostního připojení (2001-2002). Komise uložila pokutu 10,35 mil. €. SDEU potvrdil, že recoupment nemusí být prokázán.",
        dominant="Wanadoo (France Télécom)", competitor="Konkurenti ADSL", product="ADSL služby",
    ),
    "Qualcomm vs Icera (2019)": dict(
        total_output=10_000_000, catalog_price=3.50,
        variable_costs=22_000_000, avoidable_costs=25_000_000,
        extended_costs=30_000_000, full_costs=42_000_000,
        wholesale_price=0.0, competitor_lraic=4.00,
        email_text="Interní dokumenty Qualcomm naznačovaly strategii cílených cenových nabídek pro Huawei a ZTE s cílem vytlačit Icera z trhu UMTS čipsetů.",
        context="Qualcomm (2019): Komise uložila pokutu 242 mil. € za predátorské ceny 3G baseband čipsetů prodávaných pod LRAIC strategicky důležitým zákazníkům (Huawei, ZTE) s cílem eliminovat britský startup Icera (2009–2011).",
        dominant="Qualcomm", competitor="Icera", product="UMTS baseband chipset",
    ),
    "Post Danmark (C-209/10, 2012)": dict(
        total_output=1_000_000, catalog_price=2.00,
        variable_costs=1_500_000, avoidable_costs=1_600_000,
        extended_costs=1_800_000, full_costs=2_200_000,
        wholesale_price=0.0, competitor_lraic=2.30,
        email_text="V případě Post Danmark nebyl prokázán úmysl eliminovat konkurenci – chyběly usvědčující interní dokumenty.",
        context="Post Danmark (C-209/10, 2012): PD nabízela selektivní ceny neadresné pošty pod ATC, ale nad AIC (průměrné odvratitelné náklady). SDEU rozhodl, že ceny nad AVC/AIC bez prokázaného eliminačního úmyslu nejsou predátorské. Stanovil „safe harbour" nad ATC.",
        dominant="Post Danmark", competitor="Forbruger-Kontakt (FK)", product="Neadresná pošta",
    ),
}

st.title("⚖️ Predátorské ceny – AKZO test & moderní přístup Komise")

# ── Sidebar ──────────────────────────────────────────────────────────────
st.sidebar.header("Parametry modelu")
preset_name = st.sidebar.selectbox("Preset / vzorový případ", list(PRESETS.keys()))
p = PRESETS[preset_name]

st.sidebar.markdown("---")
st.sidebar.subheader("Upravitelné parametry")

dominant = st.sidebar.text_input("Dominantní firma", p["dominant"])
competitor = st.sidebar.text_input("Konkurent", p["competitor"])
product = st.sidebar.text_input("Produkt", p["product"])

total_output = st.sidebar.number_input("Celková výroba (jedn.)", value=p["total_output"], min_value=1, step=1000)
catalog_price = st.sidebar.number_input("Katalogová cena (Kč/jedn.)", value=p["catalog_price"], min_value=0.01, step=0.5)
variable_costs = st.sidebar.number_input("Variabilní náklady – AVC základ (Kč)", value=p["variable_costs"], min_value=0, step=1000)
avoidable_costs = st.sidebar.number_input("Odvratitelné náklady – AAC základ (Kč)", value=p["avoidable_costs"], min_value=0, step=1000)
extended_costs = st.sidebar.number_input("Rozšířené náklady – LRAIC základ (Kč)", value=p["extended_costs"], min_value=0, step=1000)
full_costs = st.sidebar.number_input("Celkové náklady – ATC základ (Kč)", value=p["full_costs"], min_value=0, step=1000)
wholesale_price = st.sidebar.number_input("Wholesale cena vstupu (Kč/jedn.; 0 = N/A)", value=p["wholesale_price"], min_value=0.0, step=0.5)
competitor_lraic = st.sidebar.number_input("LRAIC konkurenta (Kč/jedn.)", value=p["competitor_lraic"], min_value=0.01, step=0.5)
email_text = st.sidebar.text_area("Interní e-mail / dokument", p["email_text"], height=120)

# ── Výpočty ──────────────────────────────────────────────────────────────
AVC = variable_costs / total_output
AAC = avoidable_costs / total_output
LRAIC = extended_costs / total_output
ATC = full_costs / total_output
price = catalog_price

# ── Kontext ──────────────────────────────────────────────────────────────
st.info(p["context"])

# ── 1) Nákladové benchmarky ──────────────────────────────────────────────
st.header("1️⃣ Nákladové benchmarky na jednotku")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("AVC", f"{AVC:,.2f} Kč")
col2.metric("AAC", f"{AAC:,.2f} Kč")
col3.metric("LRAIC", f"{LRAIC:,.2f} Kč")
col4.metric("ATC", f"{ATC:,.2f} Kč")
col5.metric("Cena", f"{price:,.2f} Kč", delta=f"{price - ATC:+,.2f} vs ATC", delta_color="normal")

df_costs = pd.DataFrame({
    "Ukazatel": ["AVC", "AAC", "LRAIC", "ATC", "Cena"],
    "Kč / jedn.": [AVC, AAC, LRAIC, ATC, price],
    "Popis": [
        "Průměrné variabilní náklady (suroviny, energie, přímá práce)",
        "Průměrné odvratitelné náklady (+ nájem haly, leasing stroje)",
        "Dlouhodobé průměrné přírůstkové náklady (rozšířená produkce)",
        "Průměrné celkové náklady (+ odpisy, administrativa)",
        f"Katalogová cena {product}",
    ]
})
st.dataframe(df_costs, use_container_width=True, hide_index=True)

# ── Graf ──────────────────────────────────────────────────────────────
fig = go.Figure()
benchmarks = {"AVC": AVC, "AAC": AAC, "LRAIC": LRAIC, "ATC": ATC}
colors_bench = {"AVC": "#e74c3c", "AAC": "#e67e22", "LRAIC": "#3498db", "ATC": "#2ecc71"}
for name, val in benchmarks.items():
    fig.add_hline(y=val, line_dash="dash", line_color=colors_bench[name],
                  annotation_text=f"{name} = {val:.2f}", annotation_position="left")

fig.add_trace(go.Bar(
    x=[f"Cena {product}"], y=[price],
    marker_color="#9b59b6" if price < AVC else ("#f39c12" if price < ATC else "#27ae60"),
    text=[f"{price:.2f} Kč"], textposition="outside", name="Cena"
))
fig.update_layout(title="Cena vs. nákladové benchmarky", yaxis_title="Kč / jednotka",
                  height=420, showlegend=False)
st.plotly_chart(fig, use_container_width=True)

# ── 2) Klasický AKZO test ────────────────────────────────────────────────
st.header("2️⃣ Klasický AKZO test (C-62/86)")

if price < AVC:
    akzo_zone = "🔴 Cena < AVC → **Presumovaná predace** (per se protiprávní)"
    akzo_detail = "Cena pod průměrnými variabilními náklady – podle AKZO presumovaný zneužití dominantního postavení. Firma nepokrývá ani variabilní náklady, takové cenové chování nemá jiné racionální vysvětlení než eliminaci konkurence."
elif price < ATC:
    akzo_zone = "🟡 AVC ≤ Cena < ATC → **Predace podmíněna prokázáním úmyslu**"
    akzo_detail = "Cena mezi AVC a ATC – chování může být zneužitím, pokud je prokázán úmysl eliminovat konkurenta. Rozhodující je analýza interních dokumentů, kontextových důkazů a obchodní logiky cenového chování."
else:
    akzo_zone = "🟢 Cena ≥ ATC → **Bezpečný přístav (safe harbour)**"
    akzo_detail = "Cena nad průměrnými celkovými náklady – podle judikatury AKZO i Post Danmark (C-209/10) nemůže být považována za predátorskou, i kdyby byla selektivní."

st.markdown(akzo_zone)
st.markdown(akzo_detail)

# ── 3) Moderní přístup Komise ────────────────────────────────────────────
st.header("3️⃣ Moderní přístup Komise (Enforcement Priorities 2009)")

if price < AAC:
    modern_zone = "🔴 Cena < AAC → **Presumovaná predace** (obdoba AVC v moderním pojetí)"
    modern_detail = "Cena pod průměrnými odvratitelnými náklady – Komise toto považuje za silný indikátor predace. AAC lépe zachycuje reálnou ekonomickou oběť firmy."
elif price < LRAIC:
    modern_zone = "🟡 AAC ≤ Cena < LRAIC → **Šedá zóna – nutno zkoumat úmysl a efekt**"
    modern_detail = "Cena mezi AAC a LRAIC – equally efficient competitor by nemohl dlouhodobě konkurovat. Komise zkoumá záměr, strategické dokumenty a tržní kontext."
else:
    modern_zone = "🟢 Cena ≥ LRAIC → **Bezpečný přístav**"
    modern_detail = "Cena nad LRAIC – stejně efektivní konkurent by mohl na trhu přežít. Komise zpravidla nezahajuje řízení."

st.markdown(modern_zone)
st.markdown(modern_detail)

# ── Srovnávací tabulka testů ────────────────────────────────────────────
st.subheader("Srovnání přístupů")

comparison_df = pd.DataFrame({
    "Aspekt": ["Dolní benchmark", "Horní benchmark", "Šedá zóna", "Klíčový důkaz šedé zóny", "Recoupment požadován?"],
    "AKZO test (1991)": ["AVC", "ATC", "AVC ≤ P < ATC", "Úmysl eliminovat", "Ne v EU (France Télécom)"],
    "Moderní přístup (2009)": ["AAC", "LRAIC", "AAC ≤ P < LRAIC", "Úmysl + equally efficient competitor", "Ne v EU"],
})
st.dataframe(comparison_df, use_container_width=True, hide_index=True)

# ── 4) Interní e-mail & úmysl ───────────────────────────────────────────
st.header("4️⃣ Interní e-mail a prokázání vytlačovacího úmyslu")

st.warning(f"**Interní dokument:**\n\n{email_text}")

intent_points = [
    "**Systematické monitorování konkurenta** – pravidelná týdenní analýza cen naznačuje cílenou cenovou strategii, nikoli běžnou tržní reakci.",
    "**Direktivní pokyn „držet cenu pod nimi"** – jde o klasický důkaz eliminačního záměru (srov. AKZO, kde interní memoranda hrála klíčovou roli).",
    "**Krytí ztrát z rezerv** – firma si je vědoma, že současné ceny generují ztrátu, a přesto je udržuje. To popírá obhajobu „meeting competition".",
    "**Temporální dimenze** – formulace „prozatím" naznačuje dvoufázovou strategii: (i) krátkodobé ztráty → (ii) budoucí vytlačení a recoupment.",
    "**Důkazní síla v právu EU** – podle judikatury AKZO i Qualcomm (2019) jsou interní dokumenty přímým důkazem subjektivního úmyslu a posunují šedou zónu (AVC–ATC / AAC–LRAIC) směrem k závěru o zneužití.",
]
for pt in intent_points:
    st.markdown(f"- {pt}")

# ── 5) Recoupment ────────────────────────────────────────────────────────
st.header("5️⃣ Recoupment – reálnost zpětného získání ztrát")

st.markdown("""
V EU **není recoupment nutnou podmínkou** pro konstatování predátorské ceny (France Télécom, C-202/07 P; Qualcomm T-671/19).
Přesto posouzení recoupmentu pomáhá hodnotit racionalitu strategie a škodlivost pro soutěž.
""")

total_loss = max(0, (ATC - price) * total_output)
st.metric("Měsíční ztráta při současných cenách", f"{total_loss:,.0f} Kč")

recoupment_factors = [
    ("Bariéry vstupu", "Vysoké bariéry (regulace, patenty, kapitálová náročnost) usnadňují recoupment – konkurenti se po eliminaci nevrátí.", "⬆️"),
    ("Tržní podíl a dominance", f"Čím vyšší podíl {dominant} na trhu po vytlačení {competitor}, tím snazší zvýšení cen.", "⬆️"),
    ("Transparentnost trhu", "Na transparentním trhu je snadnější monitorovat a potlačit budoucí vstup.", "⬆️"),
    ("Elasticita poptávky", "Nízká elasticita umožňuje po eliminaci konkurenta výrazně zvýšit ceny.", "⬆️"),
    ("Regulatorní prostředí", "Silný soutěžní úřad (ÚOHS, Komise) snižuje pravděpodobnost úspěšného recoupmentu – firma riskuje pokutu.", "⬇️"),
    ("Doba predace", "Čím déle musí firma držet sub-cost ceny, tím vyšší kumulované ztráty a nižší návratnost.", "⬇️"),
]

for factor, desc, arrow in recoupment_factors:
    st.markdown(f"- {arrow} **{factor}**: {desc}")

# ── 6) Margin squeeze ───────────────────────────────────────────────────
st.header("6️⃣ Bonus: Margin squeeze analýza")

if wholesale_price > 0:
    margin = price - wholesale_price
    margin_pct = (margin / price) * 100 if price > 0 else 0

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Wholesale cena", f"{wholesale_price:,.2f} Kč")
    col_b.metric("Retail cena", f"{price:,.2f} Kč")
    col_c.metric("Marže", f"{margin:,.2f} Kč ({margin_pct:.1f} %)")

    downstream_costs_estimate = AVC - wholesale_price if AVC > wholesale_price else AVC * 0.1
    viable = margin > downstream_costs_estimate

    st.markdown(f"""
**Analýza:** Rozdíl mezi wholesale cenou ({wholesale_price:.2f} Kč) a retail cenou ({price:.2f} Kč)
činí pouhých **{margin:.2f} Kč na jednotku** ({margin_pct:.1f} %).

Podle doktríny margin squeeze (Deutsche Telekom, TeliaSonera, Post Danmark II):
- Vertikálně integrovaná firma, která prodává vstup konkurentům za wholesale cenu a zároveň soutěží na downstream trhu,
  **nesmí nastavit spread tak úzký, že equally efficient competitor nemůže pokrýt downstream náklady**.
- Marže {margin:.2f} Kč pravděpodobně **{"nestačí" if not viable else "stačí"}** na pokrytí zpracovatelských a distribučních nákladů downstream operátora.
""")

    if margin < 2 and margin > 0:
        st.error("⚠️ **Indikace margin squeeze**: Spread je extrémně úzký. Equally efficient competitor nemůže na downstream trhu přežít.")
    elif margin <= 0:
        st.error("🔴 **Negativní marže**: Retail cena je nižší nebo rovna wholesale ceně – jde o zjevný margin squeeze i potenciální predaci.")
    else:
        st.success("✅ Spread se jeví jako dostatečný pro pokrytí rozumných downstream nákladů.")

    st.markdown(f"""
**LRAIC konkurenta ({competitor}):** {competitor_lraic:.2f} Kč/jedn.
Pokud {competitor} musí nakupovat vstup za wholesale cenu {wholesale_price:.2f} Kč a jeho LRAIC je {competitor_lraic:.2f} Kč,
pak jeho minimální retail cena by musela být ≥ {competitor_lraic:.2f} Kč. Dominantní firma prodává za {price:.2f} Kč,
což je **{"pod" if price < competitor_lraic else "nad"}** LRAIC konkurenta –
{"tím znemožňuje konkurentovi ziskové působení na trhu." if price < competitor_lraic else "konkurent může na trhu přežít."}
""")
else:
    st.info("Wholesale cena nebyla zadána (N/A) – margin squeeze analýza není relevantní pro tento případ.")

# ── Závěr ────────────────────────────────────────────────────────────────
st.header("📋 Závěrečné hodnocení ve 3 krocích")

st.subheader("(i) Nákladové benchmarky")
st.markdown(f"""
| Benchmark | Hodnota | Cena vs. benchmark |
|-----------|---------|-------------------|
| AVC | {AVC:.2f} Kč | {"✅ nad" if price >= AVC else "❌ pod"} |
| AAC | {AAC:.2f} Kč | {"✅ nad" if price >= AAC else "❌ pod"} |
| LRAIC | {LRAIC:.2f} Kč | {"✅ nad" if price >= LRAIC else "❌ pod"} |
| ATC | {ATC:.2f} Kč | {"✅ nad" if price >= ATC else "❌ pod"} |
""")

st.subheader("(ii) Právní test")
akzo_label = "Cena < AVC → presumovaná predace" if price < AVC else ("AVC ≤ Cena < ATC → predace s prokázáním úmyslu" if price < ATC else "Cena ≥ ATC → safe harbour")
modern_label = "Cena < AAC → presumovaná predace" if price < AAC else ("AAC ≤ Cena < LRAIC → šedá zóna" if price < LRAIC else "Cena ≥ LRAIC → safe harbour")

st.markdown(f"""
- **AKZO test:** {akzo_label}
- **Moderní test Komise:** {modern_label}
""")

st.subheader("(iii) Intent & Recoupment")
has_intent_evidence = any(kw in email_text.lower() for kw in ["musíme", "pod nimi", "eliminat", "must", "ensure", "survive", "pre-empt", "strateg"])
st.markdown(f"""
- **Úmysl:** {"✅ Interní dokumenty **poskytují** přímý důkaz eliminačního záměru." if has_intent_evidence else "⚠️ Interní dokumenty neposkytují jednoznačný důkaz eliminačního záměru."}
- **Recoupment:** V EU není nutnou podmínkou (France Télécom, Qualcomm), ale analýza faktorů (bariéry vstupu, tržní podíl, elasticita, regulace) ukazuje na {"realistickou" if total_loss < total_output * price * 0.5 else "spornou"} možnost zpětného získání ztrát.
- **Celkový závěr:** {"Silné indicie pro zneužití dominantního postavení prostřednictvím predátorských cen." if (price < ATC and has_intent_evidence) else "Na základě zadaných parametrů není zneužití jednoznačně prokázáno – závisí na dalším kontextu."}
""")

st.markdown("---")
st.caption("Aplikace pro výukové účely | Zdroje: AKZO (C-62/86), France Télécom (C-202/07 P), Qualcomm (T-671/19), Post Danmark (C-209/10), Guidance on Enforcement Priorities (2009)")
