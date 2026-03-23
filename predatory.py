import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Predatorske ceny - AKZO & moderni test", layout="wide", page_icon="\u2696\uFE0F")

# -- Presets --
PRESETS = {
    "ChemPro vs EcoChem (modelovy pripad)": dict(
        total_output=10_000, catalog_price=11.0,
        variable_costs=90_000, avoidable_costs=120_000,
        extended_costs=150_000, full_costs=210_000,
        wholesale_price=10.0, competitor_lraic=14.0,
        email_text=(
            "\u201eSledujte cenovou politiku EcoChem \u2013 na ka\u017ed\u00e9 pond\u011bl\u00ed p\u0159ipravte anal\u00fdzu. "
            "Mus\u00edme dr\u017eet katalogovou cenu v\u017edycky pod nimi. "
            "Ztr\u00e1ty budeme prozat\u00edm kr\u00fdt lo\u0148sk\u00fdmi rezervami.\u201c"
        ),
        context=(
            "Na trhu pr\u016fmyslov\u00fdch chemik\u00e1li\u00ed v \u010cR p\u016fsob\u00ed dominantn\u00ed firma ChemPro "
            "a men\u0161\u00ed konkurent EcoChem. ChemPro reaguje na vstup EcoChem agresivn\u00edm "
            "sn\u00ed\u017een\u00edm cen produktu Chemix20. \u00daOHS zah\u00e1jil \u0161et\u0159en\u00ed."
        ),
        dominant="ChemPro", competitor="EcoChem", product="Chemix20",
    ),
    "AKZO vs ECS (EU, C-62/86)": dict(
        total_output=50_000, catalog_price=1.80,
        variable_costs=70_000, avoidable_costs=78_000,
        extended_costs=85_000, full_costs=110_000,
        wholesale_price=0.0, competitor_lraic=2.40,
        email_text=(
            "We must take every step to ensure ECS does not survive "
            "in the flour additives market."
        ),
        context=(
            "AKZO (C-62/86, 1991): AKZO Chemie, dominantn\u00ed hr\u00e1\u010d na trhu organick\u00fdch peroxid\u016f, "
            "reagoval na vstup ECS na trh mou\u010dn\u00fdch p\u0159\u00edsad selektivn\u00edmi cenov\u00fdmi \u0161krty "
            "pod \u00farovn\u00ed n\u00e1klad\u016f. Komise ulo\u017eila pokutu 10 mil. ECU."
        ),
        dominant="AKZO Chemie", competitor="ECS", product="Benzoyl peroxide",
    ),
    "France Telecom / Wanadoo (2003/2009)": dict(
        total_output=500_000, catalog_price=29.90,
        variable_costs=12_000_000, avoidable_costs=13_500_000,
        extended_costs=14_500_000, full_costs=18_000_000,
        wholesale_price=0.0, competitor_lraic=35.0,
        email_text=(
            "Pre-empt the market during a key phase in its development."
        ),
        context=(
            "Wanadoo Interactive (dcerka France Telecom) stanovila predatorske ceny sluzeb "
            "eXtense a Wanadoo ADSL na francouzskem trhu vysokorychlostniho pripojeni (2001-2002). "
            "Komise ulozila pokutu 10,35 mil. EUR. SDEU potvrdil, ze recoupment nemusi byt prokazan."
        ),
        dominant="Wanadoo (France Telecom)", competitor="Konkurenti ADSL", product="ADSL sluzby",
    ),
    "Qualcomm vs Icera (2019)": dict(
        total_output=10_000_000, catalog_price=3.50,
        variable_costs=22_000_000, avoidable_costs=25_000_000,
        extended_costs=30_000_000, full_costs=42_000_000,
        wholesale_price=0.0, competitor_lraic=4.00,
        email_text=(
            "Targeted pricing offers for Huawei and ZTE to push Icera "
            "out of the UMTS chipset market."
        ),
        context=(
            "Qualcomm (2019): Komise ulozila pokutu 242 mil. EUR za predatorske ceny "
            "3G baseband chipsetu prodavanych pod LRAIC strategicky dulezitym zakaznikum "
            "(Huawei, ZTE) s cilem eliminovat britsky startup Icera (2009-2011)."
        ),
        dominant="Qualcomm", competitor="Icera", product="UMTS baseband chipset",
    ),
    "Post Danmark (C-209/10, 2012)": dict(
        total_output=1_000_000, catalog_price=2.00,
        variable_costs=1_500_000, avoidable_costs=1_600_000,
        extended_costs=1_800_000, full_costs=2_200_000,
        wholesale_price=0.0, competitor_lraic=2.30,
        email_text=(
            "V pripade Post Danmark nebyl prokazan umysl eliminovat konkurenci "
            "- chybely usvedcujici interni dokumenty."
        ),
        context=(
            "Post Danmark (C-209/10, 2012): PD nabizela selektivni ceny neadresne posty "
            "pod ATC, ale nad AIC. SDEU rozhodl, ze ceny nad AVC/AIC bez prokazaneho "
            "eliminacniho umyslu nejsou predatorske."
        ),
        dominant="Post Danmark", competitor="Forbruger-Kontakt (FK)", product="Neadresna posta",
    ),
}

st.title("\u2696\uFE0F Predatorske ceny \u2013 AKZO test & moderni pristup Komise")

# -- Sidebar --
st.sidebar.header("Parametry modelu")
preset_name = st.sidebar.selectbox("Preset / vzorovy pripad", list(PRESETS.keys()))
p = PRESETS[preset_name]

st.sidebar.markdown("---")
st.sidebar.subheader("Upravitelne parametry")

dominant = st.sidebar.text_input("Dominantni firma", p["dominant"])
competitor = st.sidebar.text_input("Konkurent", p["competitor"])
product = st.sidebar.text_input("Produkt", p["product"])

total_output = st.sidebar.number_input("Celkova vyroba (jedn.)", value=p["total_output"], min_value=1, step=1000)
catalog_price = st.sidebar.number_input("Katalogova cena (Kc/jedn.)", value=p["catalog_price"], min_value=0.01, step=0.5)
variable_costs = st.sidebar.number_input("Variabilni naklady - AVC zaklad (Kc)", value=p["variable_costs"], min_value=0, step=1000)
avoidable_costs = st.sidebar.number_input("Odvratitelne naklady - AAC zaklad (Kc)", value=p["avoidable_costs"], min_value=0, step=1000)
extended_costs = st.sidebar.number_input("Rozsirene naklady - LRAIC zaklad (Kc)", value=p["extended_costs"], min_value=0, step=1000)
full_costs = st.sidebar.number_input("Celkove naklady - ATC zaklad (Kc)", value=p["full_costs"], min_value=0, step=1000)
wholesale_price = st.sidebar.number_input("Wholesale cena vstupu (Kc/jedn.; 0 = N/A)", value=p["wholesale_price"], min_value=0.0, step=0.5)
competitor_lraic = st.sidebar.number_input("LRAIC konkurenta (Kc/jedn.)", value=p["competitor_lraic"], min_value=0.01, step=0.5)
email_text = st.sidebar.text_area("Interni e-mail / dokument", p["email_text"], height=120)

# -- Vypocty --
AVC = variable_costs / total_output
AAC = avoidable_costs / total_output
LRAIC = extended_costs / total_output
ATC = full_costs / total_output
price = catalog_price

# -- Kontext --
st.info(p["context"])

# -- 1) Nakladove benchmarky --
st.header("1\uFE0F\u20E3 Nakladove benchmarky na jednotku")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("AVC", f"{AVC:,.2f} Kc")
col2.metric("AAC", f"{AAC:,.2f} Kc")
col3.metric("LRAIC", f"{LRAIC:,.2f} Kc")
col4.metric("ATC", f"{ATC:,.2f} Kc")
col5.metric("Cena", f"{price:,.2f} Kc", delta=f"{price - ATC:+,.2f} vs ATC", delta_color="normal")

df_costs = pd.DataFrame({
    "Ukazatel": ["AVC", "AAC", "LRAIC", "ATC", "Cena"],
    "Kc / jedn.": [AVC, AAC, LRAIC, ATC, price],
    "Popis": [
        "Prumerne variabilni naklady (suroviny, energie, prima prace)",
        "Prumerne odvratitelne naklady (+ najem haly, leasing stroje)",
        "Dlouhodobe prumerne prirustkove naklady (rozsirena produkce)",
        "Prumerne celkove naklady (+ odpisy, administrativa)",
        f"Katalogova cena {product}",
    ]
})
st.dataframe(df_costs, use_container_width=True, hide_index=True)

# -- Graf --
fig = go.Figure()
benchmarks = {"AVC": AVC, "AAC": AAC, "LRAIC": LRAIC, "ATC": ATC}
colors_bench = {"AVC": "#e74c3c", "AAC": "#e67e22", "LRAIC": "#3498db", "ATC": "#2ecc71"}

all_values = [AVC, AAC, LRAIC, ATC, price]
y_min = min(all_values) * 0.7
y_max = max(all_values) * 1.3

for name, val in benchmarks.items():
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[val, val],
        mode="lines",
        line=dict(dash="dash", color=colors_bench[name], width=2),
        name=f"{name} = {val:.2f} Kc",
        showlegend=True,
        hoverinfo="name+y",
    ))

fig.add_trace(go.Bar(
    x=[0.5], y=[price], width=[0.35],
    marker_color="#9b59b6" if price < AVC else ("#f39c12" if price < ATC else "#27ae60"),
    text=[f"Cena: {price:.2f} Kc"], textposition="outside",
    name=f"Cena {product}",
    showlegend=True,
))
fig.update_layout(
    title="Cena vs. nakladove benchmarky",
    yaxis_title="Kc / jednotka",
    yaxis=dict(range=[y_min, y_max]),
    xaxis=dict(visible=False),
    height=480,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5,
        font=dict(size=13),
    ),
    margin=dict(l=60, r=30, t=80, b=30),
)
st.plotly_chart(fig, use_container_width=True)

# -- 2) Klasicky AKZO test --
st.header("2\uFE0F\u20E3 Klasicky AKZO test (C-62/86)")

if price < AVC:
    akzo_zone = "\U0001F534 Cena < AVC \u2192 **Presumovana predace** (per se protipravni)"
    akzo_detail = ("Cena pod prumernymi variabilnimi naklady - podle AKZO presumovane "
                   "zneuziti dominantniho postaveni. Firma nepokryva ani variabilni naklady, "
                   "takove cenove chovani nema jine racionalni vysvetleni nez eliminaci konkurence.")
elif price < ATC:
    akzo_zone = "\U0001F7E1 AVC \u2264 Cena < ATC \u2192 **Predace podminena prokazanim umyslu**"
    akzo_detail = ("Cena mezi AVC a ATC - chovani muze byt zneuzitim, pokud je prokazan "
                   "umysl eliminovat konkurenta. Rozhodujici je analyza internich dokumentu, "
                   "kontextovych dukazu a obchodni logiky cenoveho chovani.")
else:
    akzo_zone = "\U0001F7E2 Cena \u2265 ATC \u2192 **Bezpecny pristav (safe harbour)**"
    akzo_detail = ("Cena nad prumernymi celkovymi naklady - podle judikatury AKZO i Post "
                   "Danmark (C-209/10) nemuze byt povazovana za predatorskou, i kdyby byla selektivni.")

st.markdown(akzo_zone)
st.markdown(akzo_detail)

# -- 3) Moderni pristup Komise --
st.header("3\uFE0F\u20E3 Moderni pristup Komise (Enforcement Priorities 2009)")

if price < AAC:
    modern_zone = "\U0001F534 Cena < AAC \u2192 **Presumovana predace** (obdoba AVC v modernim pojeti)"
    modern_detail = ("Cena pod prumernymi odvratitelnymi naklady - Komise toto povazuje za "
                     "silny indikator predace. AAC lepe zachycuje realnou ekonomickou obet firmy.")
elif price < LRAIC:
    modern_zone = "\U0001F7E1 AAC \u2264 Cena < LRAIC \u2192 **Seda zona - nutno zkoumat umysl a efekt**"
    modern_detail = ("Cena mezi AAC a LRAIC - equally efficient competitor by nemohl dlouhodobe "
                     "konkurovat. Komise zkouma zamer, strategicke dokumenty a trzni kontext.")
else:
    modern_zone = "\U0001F7E2 Cena \u2265 LRAIC \u2192 **Bezpecny pristav**"
    modern_detail = ("Cena nad LRAIC - stejne efektivni konkurent by mohl na trhu prezit. "
                     "Komise zpravidla nezahajuje rizeni.")

st.markdown(modern_zone)
st.markdown(modern_detail)

# -- Srovnavaci tabulka testu --
st.subheader("Srovnani pristupu")

comparison_df = pd.DataFrame({
    "Aspekt": ["Dolni benchmark", "Horni benchmark", "Seda zona", "Klicovy dukaz sede zony", "Recoupment pozadovan?"],
    "AKZO test (1991)": ["AVC", "ATC", "AVC \u2264 P < ATC", "Umysl eliminovat", "Ne v EU (France Telecom)"],
    "Moderni pristup (2009)": ["AAC", "LRAIC", "AAC \u2264 P < LRAIC", "Umysl + equally efficient competitor", "Ne v EU"],
})
st.dataframe(comparison_df, use_container_width=True, hide_index=True)

# -- 4) Interni e-mail & umysl --
st.header("4\uFE0F\u20E3 Interni e-mail a prokazani vytlacovaciho umyslu")

st.warning(f"**Interni dokument:**\n\n{email_text}")

intent_points = [
    "**Systematicke monitorovani konkurenta** - pravidelna tydenni analyza cen naznacuje cilenou cenovou strategii, nikoli beznou trzni reakci.",
    "**Direktivni pokyn 'drzet cenu pod nimi'** - jde o klasicky dukaz eliminacniho zameru (srov. AKZO, kde interni memoranda hrala klicovou roli).",
    "**Kryti ztrat z rezerv** - firma si je vedoma, ze soucasne ceny generuji ztratu, a presto je udrzuje. To popira obhajobu 'meeting competition'.",
    "**Temporalni dimenze** - formulace 'prozatim' naznacuje dvoufazovou strategii: (i) kratkodobe ztraty -> (ii) budouci vytlaceni a recoupment.",
    "**Dukazni sila v pravu EU** - podle judikatury AKZO i Qualcomm (2019) jsou interni dokumenty primym dukazem subjektivniho umyslu a posunuji sedou zonu (AVC-ATC / AAC-LRAIC) smerem k zaveru o zneuziti.",
]
for pt in intent_points:
    st.markdown(f"- {pt}")

# -- 5) Recoupment --
st.header("5\uFE0F\u20E3 Recoupment - realnost zpetneho ziskani ztrat")

st.markdown(
    "V EU **neni recoupment nutnou podminkou** pro konstatovani predatorske ceny "
    "(France Telecom, C-202/07 P; Qualcomm T-671/19). "
    "Presto posouzeni recoupmentu pomaha hodnotit racionalitu strategie a skodlivost pro soutez."
)

total_loss = max(0, (ATC - price) * total_output)
st.metric("Mesicni ztrata pri soucasnych cenach", f"{total_loss:,.0f} Kc")

recoupment_factors = [
    ("Bariery vstupu", f"Vysoke bariery (regulace, patenty, kapitalova narocnost) usnadnuji recoupment - konkurenti se po eliminaci nevrati.", "\u2B06\uFE0F"),
    ("Trzni podil a dominance", f"Cim vyssi podil {dominant} na trhu po vytlaceni {competitor}, tim snazsi zvyseni cen.", "\u2B06\uFE0F"),
    ("Transparentnost trhu", "Na transparentnim trhu je snadnejsi monitorovat a potlacit budouci vstup.", "\u2B06\uFE0F"),
    ("Elasticita poptavky", "Nizka elasticita umoznuje po eliminaci konkurenta vyrazne zvysit ceny.", "\u2B06\uFE0F"),
    ("Regulatorni prostredi", "Silny soutezni urad (UOHS, Komise) snizuje pravdepodobnost uspesneho recoupmentu - firma riskuje pokutu.", "\u2B07\uFE0F"),
    ("Doba predace", "Cim dele musi firma drzet sub-cost ceny, tim vyssi kumulovane ztraty a nizsi navratnost.", "\u2B07\uFE0F"),
]

for factor, desc, arrow in recoupment_factors:
    st.markdown(f"- {arrow} **{factor}**: {desc}")

# -- 6) Margin squeeze --
st.header("6\uFE0F\u20E3 Bonus: Margin squeeze analyza")

if wholesale_price > 0:
    margin = price - wholesale_price
    margin_pct = (margin / price) * 100 if price > 0 else 0

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Wholesale cena", f"{wholesale_price:,.2f} Kc")
    col_b.metric("Retail cena", f"{price:,.2f} Kc")
    col_c.metric("Marze", f"{margin:,.2f} Kc ({margin_pct:.1f} %)")

    downstream_costs_estimate = AVC - wholesale_price if AVC > wholesale_price else AVC * 0.1
    viable = margin > downstream_costs_estimate

    st.markdown(
        f"**Analyza:** Rozdil mezi wholesale cenou ({wholesale_price:.2f} Kc) a retail cenou ({price:.2f} Kc) "
        f"cini pouhych **{margin:.2f} Kc na jednotku** ({margin_pct:.1f} %).\n\n"
        f"Podle doktiny margin squeeze (Deutsche Telekom, TeliaSonera, Post Danmark II):\n"
        f"- Vertikalne integrovana firma, ktera prodava vstup konkurentum za wholesale cenu a zaroven soutezi na downstream trhu, "
        f"**nesmi nastavit spread tak uzky, ze equally efficient competitor nemuze pokryt downstream naklady**.\n"
        f"- Marze {margin:.2f} Kc pravdepodobne **{'nestaci' if not viable else 'staci'}** "
        f"na pokryti zpracovatelskych a distribucnich nakladu downstream operatora."
    )

    if margin < 2 and margin > 0:
        st.error("\u26A0\uFE0F **Indikace margin squeeze**: Spread je extremne uzky. Equally efficient competitor nemuze na downstream trhu prezit.")
    elif margin <= 0:
        st.error("\U0001F534 **Negativni marze**: Retail cena je nizsi nebo rovna wholesale cene - jde o zjevny margin squeeze i potencialni predaci.")
    else:
        st.success("\u2705 Spread se jevi jako dostatecny pro pokryti rozumnych downstream nakladu.")

    st.markdown(
        f"**LRAIC konkurenta ({competitor}):** {competitor_lraic:.2f} Kc/jedn.\n"
        f"Pokud {competitor} musi nakupovat vstup za wholesale cenu {wholesale_price:.2f} Kc a jeho LRAIC je {competitor_lraic:.2f} Kc, "
        f"pak jeho minimalni retail cena by musela byt >= {competitor_lraic:.2f} Kc. Dominantni firma prodava za {price:.2f} Kc, "
        f"coz je **{'pod' if price < competitor_lraic else 'nad'}** LRAIC konkurenta - "
        f"{'tim znemoznuje konkurentovi ziskove pusobeni na trhu.' if price < competitor_lraic else 'konkurent muze na trhu prezit.'}"
    )
else:
    st.info("Wholesale cena nebyla zadana (N/A) - margin squeeze analyza neni relevantni pro tento pripad.")

# -- Zaver --
st.header("\U0001F4CB Zaverecne hodnoceni ve 3 krocich")

st.subheader("(i) Nakladove benchmarky")
st.markdown(
    f"| Benchmark | Hodnota | Cena vs. benchmark |\n"
    f"|-----------|---------|-------------------|\n"
    f"| AVC | {AVC:.2f} Kc | {'\u2705 nad' if price >= AVC else '\u274C pod'} |\n"
    f"| AAC | {AAC:.2f} Kc | {'\u2705 nad' if price >= AAC else '\u274C pod'} |\n"
    f"| LRAIC | {LRAIC:.2f} Kc | {'\u2705 nad' if price >= LRAIC else '\u274C pod'} |\n"
    f"| ATC | {ATC:.2f} Kc | {'\u2705 nad' if price >= ATC else '\u274C pod'} |"
)

st.subheader("(ii) Pravni test")
if price < AVC:
    akzo_label = "Cena < AVC -> presumovana predace"
elif price < ATC:
    akzo_label = "AVC <= Cena < ATC -> predace s prokazanim umyslu"
else:
    akzo_label = "Cena >= ATC -> safe harbour"

if price < AAC:
    modern_label = "Cena < AAC -> presumovana predace"
elif price < LRAIC:
    modern_label = "AAC <= Cena < LRAIC -> seda zona"
else:
    modern_label = "Cena >= LRAIC -> safe harbour"

st.markdown(
    f"- **AKZO test:** {akzo_label}\n"
    f"- **Moderni test Komise:** {modern_label}"
)

st.subheader("(iii) Intent & Recoupment")
has_intent_evidence = any(kw in email_text.lower() for kw in [
    "musime", "pod nimi", "eliminat", "must", "ensure", "survive", "pre-empt", "strateg"
])
st.markdown(
    f"- **Umysl:** {'\u2705 Interni dokumenty **poskytuji** primy dukaz eliminacniho zameru.' if has_intent_evidence else '\u26A0\uFE0F Interni dokumenty neposkytuji jednoznacny dukaz eliminacniho zameru.'}\n"
    f"- **Recoupment:** V EU neni nutnou podminkou (France Telecom, Qualcomm), ale analyza faktoru "
    f"(bariery vstupu, trzni podil, elasticita, regulace) ukazuje na "
    f"{'realistickou' if total_loss < total_output * price * 0.5 else 'spornou'} moznost zpetneho ziskani ztrat.\n"
    f"- **Celkovy zaver:** "
    f"{'Silne indicie pro zneuziti dominantniho postaveni prostrednictvim predatorskych cen.' if (price < ATC and has_intent_evidence) else 'Na zaklade zadanych parametru neni zneuziti jednoznacne prokazano - zavisi na dalsim kontextu.'}"
)

st.markdown("---")
st.caption(
    "Aplikace pro vyukove ucely | Zdroje: AKZO (C-62/86), France Telecom (C-202/07 P), "
    "Qualcomm (T-671/19), Post Danmark (C-209/10), Guidance on Enforcement Priorities (2009)"
)
