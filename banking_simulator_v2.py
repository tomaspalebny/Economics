
import math
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="🏦 Bankovní systém a multiplikátor", layout="wide", page_icon="🏦")


def simulate_deposit_creation(initial_injection, required_ratio, excess_ratio=0.0, cash_leak_ratio=0.0, rounds=25):
    rows = []
    incoming_deposit = float(initial_injection)
    cum_deposits = 0.0
    cum_loans = 0.0
    cum_required = 0.0
    cum_excess = 0.0
    cum_cash = 0.0

    for i in range(1, rounds + 1):
        if incoming_deposit < 0.01:
            break
        required = incoming_deposit * required_ratio
        excess = incoming_deposit * excess_ratio
        total_reserves = required + excess
        loan = max(incoming_deposit - total_reserves, 0.0)
        cash_held = loan * cash_leak_ratio
        redeposit = loan - cash_held

        cum_deposits += incoming_deposit
        cum_loans += loan
        cum_required += required
        cum_excess += excess
        cum_cash += cash_held

        rows.append({
            "Kolo": i,
            "Nový vklad": round(incoming_deposit, 2),
            "Povinné rezervy": round(required, 2),
            "Dobrovolné rezervy": round(excess, 2),
            "Nový úvěr": round(loan, 2),
            "Hotovost mimo banky": round(cash_held, 2),
            "Nový vklad v další bance": round(redeposit, 2),
            "Kumulativní depozita": round(cum_deposits, 2),
            "Kumulativní úvěry": round(cum_loans, 2),
        })
        incoming_deposit = redeposit

    df = pd.DataFrame(rows)
    return df


def fmt_money(x):
    return f"{x:,.2f} Kč".replace(",", " ")


def bilance_table(assets, liabilities):
    max_len = max(len(assets), len(liabilities))
    a_items = list(assets.items()) + [("", "")] * (max_len - len(assets))
    l_items = list(liabilities.items()) + [("", "")] * (max_len - len(liabilities))
    rows = []
    for (an, av), (ln, lv) in zip(a_items, l_items):
        rows.append({"Aktiva": an, "Částka A": av, "Pasiva": ln, "Částka P": lv})
    return pd.DataFrame(rows)


def section_intro():
    st.title("🏦 Simulace bankovního systému a peněžního multiplikátoru")
    st.markdown("Materiál navazuje na témata **centrální banka, komerční banky, aktiva, pasiva, rezervy, run na banku a peněžní multiplikátor**.")


section_intro()

with st.sidebar:
    st.header("Nastavení modelu")
    mode = st.radio("Režim", ["Prostý model", "Realističtější model"], index=0)
    initial_injection = st.number_input("Počáteční nový vklad / přírůstek rezerv", min_value=100.0, value=1000.0, step=100.0)
    required_pct = st.slider("Povinné minimální rezervy (PMR) %", min_value=1, max_value=30, value=10, step=1)
    required_ratio = required_pct / 100

    if mode == "Realističtější model":
        excess_pct = st.slider("Dobrovolné rezervy %", min_value=0, max_value=20, value=2, step=1)
        cash_leak_pct = st.slider("Únik do hotovosti % z nového úvěru", min_value=0, max_value=50, value=10, step=1)
    else:
        excess_pct = 0
        cash_leak_pct = 0

    excess_ratio = excess_pct / 100
    cash_leak_ratio = cash_leak_pct / 100
    rounds = st.slider("Počet kol simulace", min_value=5, max_value=40, value=20, step=1)

    st.markdown("---")
    st.caption("Prostý model předpokládá žádné dobrovolné rezervy a žádnou hotovost mimo banky. V praxi proto multiplikátor obvykle nefunguje přesně podle vzorce 1/r.")


df = simulate_deposit_creation(
    initial_injection=initial_injection,
    required_ratio=required_ratio,
    excess_ratio=excess_ratio,
    cash_leak_ratio=cash_leak_ratio,
    rounds=rounds,
)

simple_multiplier = 1 / required_ratio
simple_limit = initial_injection * simple_multiplier
actual_deposits = float(df["Kumulativní depozita"].iloc[-1]) if not df.empty else 0.0
actual_loans = float(df["Kumulativní úvěry"].iloc[-1]) if not df.empty else 0.0
actual_cash = float(df["Hotovost mimo banky"].sum()) if not df.empty else 0.0
actual_total_money = actual_deposits + actual_cash

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Multiplikátor",
    "🏛️ Centrální banka",
    "🏢 Komerční banky",
    "🧪 Příklady z cvičení",
    "🧩 Kvíz",
])

with tab1:
    st.header("Multiplikátor a tvorba depozit")
    st.latex(r"D = \frac{1}{r} \times R")
    st.markdown("Ve **prostém modelu** je přírůstek depozit dán převrácenou hodnotou rezervního poměru. V realitě proces tlumí dobrovolné rezervy bank a hotovost, kterou si veřejnost část úvěrů ponechá mimo bankovní systém.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("PMR", f"{required_pct} %")
    c2.metric("Teoretický multiplikátor 1/r", f"{simple_multiplier:.2f}")
    c3.metric("Kumulativní depozita v simulaci", fmt_money(actual_deposits))
    c4.metric("Kumulativní úvěry v simulaci", fmt_money(actual_loans))

    if mode == "Prostý model":
        st.info(f"Teoretický limit depozit při vstupu {fmt_money(initial_injection)} je {fmt_money(simple_limit)}.")
    else:
        st.warning("V tomto režimu jsou výsledky nižší než v prostém modelu, protože část peněz se zastaví v dobrovolných rezervách nebo unikne do hotovosti.")

    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["Kolo"], y=df["Nový vklad"], name="Nový vklad", marker_color="#1f77b4"))
    fig.add_trace(go.Bar(x=df["Kolo"], y=df["Povinné rezervy"], name="Povinné rezervy", marker_color="#ff7f0e"))
    if excess_pct > 0:
        fig.add_trace(go.Bar(x=df["Kolo"], y=df["Dobrovolné rezervy"], name="Dobrovolné rezervy", marker_color="#9467bd"))
    fig.add_trace(go.Bar(x=df["Kolo"], y=df["Nový úvěr"], name="Nový úvěr", marker_color="#2ca02c"))
    if cash_leak_pct > 0:
        fig.add_trace(go.Bar(x=df["Kolo"], y=df["Hotovost mimo banky"], name="Hotovost mimo banky", marker_color="#d62728"))
    fig.update_layout(barmode="group", height=420, xaxis_title="Kolo", yaxis_title="Kč", title="Jednotlivá kola multiplikačního procesu")
    st.plotly_chart(fig, use_container_width=True)

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df["Kolo"], y=df["Kumulativní depozita"], mode="lines+markers", name="Kumulativní depozita", line=dict(width=3, color="#1f77b4")))
    if mode == "Prostý model":
        fig2.add_hline(y=simple_limit, line_dash="dash", line_color="red", annotation_text=f"Teoretický limit {fmt_money(simple_limit)}")
    fig2.update_layout(height=360, xaxis_title="Kolo", yaxis_title="Kč", title="Konvergence kumulativních depozit")
    st.plotly_chart(fig2, use_container_width=True)

    with st.expander("Zobrazit tabulku kol"):
        st.dataframe(df, use_container_width=True, height=420)

    st.subheader("Srovnání dvou sazeb PMR")
    ca, cb = st.columns(2)
    with ca:
        rate_a = st.slider("Sazba A (%)", 1, 30, 5)
    with cb:
        rate_b = st.slider("Sazba B (%)", 1, 30, 15)

    cmp_rows = []
    deposit_a = initial_injection
    deposit_b = initial_injection
    for i in range(1, 16):
        cmp_rows.append({
            "Kolo": i,
            f"Nový vklad A ({rate_a} %)": round(deposit_a, 2),
            f"Nový vklad B ({rate_b} %)": round(deposit_b, 2),
        })
        deposit_a *= (1 - rate_a / 100)
        deposit_b *= (1 - rate_b / 100)
    cmp_df = pd.DataFrame(cmp_rows)

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(x=cmp_df["Kolo"], y=cmp_df[f"Nový vklad A ({rate_a} %)"] , name=f"PMR {rate_a} %", marker_color="#1f77b4"))
    fig3.add_trace(go.Bar(x=cmp_df["Kolo"], y=cmp_df[f"Nový vklad B ({rate_b} %)"] , name=f"PMR {rate_b} %", marker_color="#e377c2"))
    fig3.update_layout(barmode="group", height=380, xaxis_title="Kolo", yaxis_title="Kč", title="Nižší PMR znamenají pomalejší útlum a vyšší teoretický multiplikátor")
    st.plotly_chart(fig3, use_container_width=True)

with tab2:
    st.header("Centrální banka")
    st.markdown("Centrální banka provádí monetární politiku, sleduje stabilitu měny a působí také jako věřitel poslední instance. V této kartě je modelován dopad operací na volném trhu na rezervy bankovního systému a na teoretickou tvorbu depozit.")

    c1, c2, c3 = st.columns(3)
    with c1:
        base_reserves = st.number_input("Výchozí rezervy bankovního systému", min_value=0.0, value=10000.0, step=1000.0)
    with c2:
        operation = st.selectbox("Operace na volném trhu", [
            "Žádná operace",
            "Nákup obligací za 1 000 Kč",
            "Nákup obligací za 2 000 Kč",
            "Prodej obligací za 1 000 Kč",
            "Prodej obligací za 2 000 Kč",
            "Prodej obligací za 3 000 Kč",
        ])
    with c3:
        use_realistic = st.checkbox("Použít i realističtější model", value=True)

    op_delta = {
        "Žádná operace": 0.0,
        "Nákup obligací za 1 000 Kč": 1000.0,
        "Nákup obligací za 2 000 Kč": 2000.0,
        "Prodej obligací za 1 000 Kč": -1000.0,
        "Prodej obligací za 2 000 Kč": -2000.0,
        "Prodej obligací za 3 000 Kč": -3000.0,
    }[operation]

    new_reserves = max(base_reserves + op_delta, 0.0)
    old_theoretical = base_reserves * simple_multiplier
    new_theoretical = new_reserves * simple_multiplier
    delta_theoretical = new_theoretical - old_theoretical

    assets_before = {"Devizové rezervy a cenné papíry": "X", "Úvěry bankám": "Y"}
    liabilities_before = {"Oběživo": "A", "Rezervy bank": fmt_money(base_reserves)}
    asset_change_label = "Nákup obligací" if op_delta > 0 else "Prodej obligací" if op_delta < 0 else "Beze změny"
    assets_after = {"Devizové rezervy a cenné papíry": asset_change_label if op_delta != 0 else "X", "Úvěry bankám": "Y"}
    liabilities_after = {"Oběživo": "A", "Rezervy bank": fmt_money(new_reserves)}

    b1, b2, b3 = st.columns([2, 1, 2])
    with b1:
        st.markdown("### Před operací")
        st.dataframe(bilance_table(assets_before, liabilities_before), use_container_width=True, hide_index=True)
    with b2:
        if op_delta > 0:
            st.success(f"CB nakupuje obligace\n\n+{fmt_money(op_delta)} do rezerv")
        elif op_delta < 0:
            st.error(f"CB prodává obligace\n\n{fmt_money(abs(op_delta))} odčerpá z rezerv")
        else:
            st.info("Bez změny rezerv")
    with b3:
        st.markdown("### Po operaci")
        st.dataframe(bilance_table(assets_after, liabilities_after), use_container_width=True, hide_index=True)

    m1, m2, m3 = st.columns(3)
    m1.metric("Změna rezerv", fmt_money(op_delta))
    m2.metric("Teoretický přírůstek / pokles depozit", fmt_money(delta_theoretical))
    m3.metric("Nový teoretický objem depozit", fmt_money(new_theoretical))

    st.caption("Zde je záměrně použito označení teoretický objem depozit, nikoli skutečná peněžní zásoba. Ve skutečnosti záleží i na dobrovolných rezervách, chování veřejnosti a poptávce po úvěrech.")

    if use_realistic:
        delta_positive = max(op_delta, 0.0)
        realistic_up = simulate_deposit_creation(delta_positive, required_ratio, excess_ratio, cash_leak_ratio, rounds)
        realistic_up_total = float(realistic_up["Kumulativní depozita"].iloc[-1]) if not realistic_up.empty else 0.0
        realistic_down = simulate_deposit_creation(abs(min(op_delta, 0.0)), required_ratio, excess_ratio, cash_leak_ratio, rounds)
        realistic_down_total = float(realistic_down["Kumulativní depozita"].iloc[-1]) if not realistic_down.empty else 0.0
        realistic_delta = realistic_up_total - realistic_down_total
        st.metric("Odhad dopadu v realističtějším modelu", fmt_money(realistic_delta))

with tab3:
    st.header("Komerční banky a bilance")
    st.markdown("Vklady jsou pro banku **pasiva**, zatímco rezervy, úvěry a držené cenné papíry jsou **aktiva**. Tato karta ukazuje, jak se jeden nový vklad šíří mezi bankami krok za krokem.")

    show_banks = st.slider("Kolik bank zobrazit", 1, 12, 6)
    current_deposit = initial_injection
    total_displayed = 0.0

    for i in range(1, show_banks + 1):
        required = current_deposit * required_ratio
        excess = current_deposit * excess_ratio
        total_reserves = required + excess
        loan = max(current_deposit - total_reserves, 0.0)
        cash_held = loan * cash_leak_ratio
        next_deposit = loan - cash_held
        total_displayed += current_deposit

        with st.expander(f"🏦 Banka {i}: nový vklad {fmt_money(current_deposit)}", expanded=(i <= 3)):
            left, right = st.columns(2)
            with left:
                assets = {
                    "Rezervy": fmt_money(total_reserves),
                    "Úvěry": fmt_money(loan),
                }
                st.dataframe(pd.DataFrame({"Aktiva": list(assets.keys()), "Částka": list(assets.values())}), hide_index=True, use_container_width=True)
            with right:
                liabilities = {"Vklady klientů": fmt_money(current_deposit)}
                st.dataframe(pd.DataFrame({"Pasiva": list(liabilities.keys()), "Částka": list(liabilities.values())}), hide_index=True, use_container_width=True)

            st.write(f"Povinné rezervy: {fmt_money(required)} | Dobrovolné rezervy: {fmt_money(excess)} | Nový úvěr: {fmt_money(loan)}")
            if cash_held > 0:
                st.write(f"Veřejnost si ponechá v hotovosti: {fmt_money(cash_held)} | Do další banky doputuje: {fmt_money(next_deposit)}")
            elif i < show_banks:
                st.write(f"Do další banky doputuje celý nový vklad: {fmt_money(next_deposit)}")
        current_deposit = next_deposit
        if current_deposit < 0.01:
            break

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Zobrazená kumulativní depozita", fmt_money(total_displayed))
    s2.metric("Celková hotovost mimo banky", fmt_money(actual_cash))
    s3.metric("Depozita + hotovost ze simulace", fmt_money(actual_total_money))
    s4.metric("Teoretický limit v prostém modelu", fmt_money(simple_limit))

    st.subheader("Likvidita a solventnost")
    st.markdown("Banka může být solventní, ale dočasně nelikvidní, pokud má kvalitní aktiva, ale nemá dost hotových prostředků na okamžité výběry. Při runu na banku může proto zasahovat centrální banka jako věřitel poslední instance.")

    run_share = st.slider("Kolik % vkladů chtějí klienti najednou vybrat", 0, 100, 30)
    sample_deposits = 1000.0
    sample_reserves = sample_deposits * (required_ratio + excess_ratio)
    withdrawal = sample_deposits * run_share / 100
    liquidity_gap = sample_reserves - withdrawal

    r1, r2, r3 = st.columns(3)
    r1.metric("Modelová banka: vklady", fmt_money(sample_deposits))
    r2.metric("Likvidní rezervy", fmt_money(sample_reserves))
    r3.metric("Požadovaný výběr", fmt_money(withdrawal))
    if liquidity_gap >= 0:
        st.success(f"Banka by run ustála z vlastních rezerv. Přebytek likvidity: {fmt_money(liquidity_gap)}")
    else:
        st.warning(f"Bance chybí okamžitá likvidita {fmt_money(abs(liquidity_gap))}. Přesto může být stále solventní, pokud hodnota jejích aktiv převyšuje závazky.")

with tab4:
    st.header("Řešené příklady z cvičení")
    example = st.selectbox("Vyberte příklad", ["Příklad 1", "Příklad 2", "Příklad 3"])

    if example == "Příklad 1":
        deposits = 10000.0
        loans = 9250.0
        reserves = deposits - loans
        ratio = reserves / deposits
        multiplier = 1 / ratio
        delta_reserves = 250.0
        delta_deposits = delta_reserves * multiplier

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### Zadání")
            st.write("V ekonomice je 10 000 Kč, všechny peníze jsou uloženy v jedné bance a banka půjčí 9 250 Kč.")
        with c2:
            st.markdown("### Řešení")
            st.write(f"Rezervy banky jsou {fmt_money(reserves)} a rezervní poměr je {ratio*100:.2f} %.")
            st.write(f"Peněžní multiplikátor je {multiplier:.2f}. Zvýšení rezerv o 250 Kč by při stejném poměru umožnilo přírůstek depozit o {fmt_money(delta_deposits)}.")

        st.dataframe(
            pd.DataFrame({
                "Aktiva": ["Rezervy", "Úvěry"],
                "Částka A": [fmt_money(reserves), fmt_money(loans)],
                "Pasiva": ["Vklady", ""],
                "Částka P": [fmt_money(deposits), ""],
            }),
            hide_index=True,
            use_container_width=True,
        )

    elif example == "Příklad 2":
        req_res = 80.0
        ex_res = 40.0
        deposits = 800.0
        loans = 600.0
        bills = 80.0
        req_ratio = req_res / deposits
        ex_ratio = ex_res / deposits
        total_reserves = req_res + ex_res
        new_req_ratio = 0.05
        total_reserve_ratio = new_req_ratio + ex_ratio
        new_deposits = total_reserves / total_reserve_ratio
        new_loans = new_deposits - total_reserves - bills

        st.write(f"Původní míra PMR je {req_ratio*100:.2f} % a dobrovolné rezervy tvoří {ex_ratio*100:.2f} % vkladů.")
        st.write(f"Pokud PMR klesnou na 5 % a banky chtějí držet stejné procento dobrovolných rezerv, celkový rezervní poměr bude {total_reserve_ratio*100:.2f} %.")
        st.write(f"Při nezměněných celkových rezervách {fmt_money(total_reserves)} a nezměněných pokladničních poukázkách {fmt_money(bills)} vyjdou nové vklady na {fmt_money(new_deposits)} a nové úvěry na {fmt_money(new_loans)}.")

        original = pd.DataFrame({
            "Aktiva": ["Povinné rezervy", "Dobrovolné rezervy", "Úvěry", "Pokladniční poukázky"],
            "Původně": [fmt_money(req_res), fmt_money(ex_res), fmt_money(loans), fmt_money(bills)],
            "Po změně": [fmt_money(new_deposits * new_req_ratio), fmt_money(new_deposits * ex_ratio), fmt_money(new_loans), fmt_money(bills)],
        })
        st.dataframe(original, hide_index=True, use_container_width=True)

    else:
        st.write("Předpoklad: PMR jsou 10 %, banky nedrží dobrovolné rezervy.")
        st.write("a) Prodej vládních obligací za 1 mil. USD sníží rezervy o 1 mil. USD. V prostém modelu tedy peněžní nabídka klesne až o 10 mil. USD.")
        st.write("b) Pokud Fed sníží PMR na 5 %, ale banky si samy ponechají dalších 5 % dobrovolných rezerv, celkový rezervní poměr zůstane 10 % a multiplikátor se nezmění.")
        st.info("To je dobrý příklad toho, proč samotná změna PMR nemusí v praxi vyvolat očekávaný dopad na nabídku peněz.")

with tab5:
    st.header("Kvíz")
    score = 0
    total = 6

    q1 = st.radio("1. Jaký je prostý peněžní multiplikátor při PMR 5 %?", ["5", "10", "20", "25"], index=None)
    if q1 is not None:
        if q1 == "20":
            score += 1
            st.success("Správně: 1 / 0,05 = 20.")
        else:
            st.error("Správně je 20.")

    q2 = st.radio("2. Jsou vklady klientů pro komerční banku aktivem nebo pasivem?", ["Aktivem", "Pasivem"], index=None)
    if q2 is not None:
        if q2 == "Pasivem":
            score += 1
            st.success("Správně: vklad je závazek banky vůči klientovi.")
        else:
            st.error("Správně je pasivem.")

    q3 = st.radio("3. Co se typicky stane s rezervami bank, když centrální banka nakupuje obligace?", ["Klesnou", "Vzrostou", "Nezmění se"], index=None)
    if q3 is not None:
        if q3 == "Vzrostou":
            score += 1
            st.success("Správně: nákup obligací přidává rezervy do systému.")
        else:
            st.error("Správně je vzrostou.")

    q4 = st.radio("4. Co nejlépe vystihuje run na banku?", ["Banka rychle poskytuje nové úvěry", "Klienti hromadně vybírají vklady", "Centrální banka zvyšuje PMR"], index=None)
    if q4 is not None:
        if q4 == "Klienti hromadně vybírají vklady":
            score += 1
            st.success("Správně.")
        else:
            st.error("Správně je hromadný výběr vkladů.")

    q5 = st.radio("5. Co je M1 v ČR podle zadání?", ["Oběživo + termínovaná depozita", "Oběživo + šekovatelná korunová depozita", "Oběživo + devizové vklady"], index=None)
    if q5 is not None:
        if q5 == "Oběživo + šekovatelná korunová depozita":
            score += 1
            st.success("Správně.")
        else:
            st.error("Správně je oběživo + šekovatelná korunová depozita.")

    q6 = st.radio("6. Proč se může skutečný multiplikátor lišit od 1/r?", ["Protože banky mohou držet dobrovolné rezervy a veřejnost hotovost", "Protože aktiva a pasiva se nemusí rovnat", "Protože vklady nejsou součástí peněz"], index=None)
    if q6 is not None:
        if q6 == "Protože banky mohou držet dobrovolné rezervy a veřejnost hotovost":
            score += 1
            st.success("Správně.")
        else:
            st.error("Správně je první možnost.")

    answered = sum(x is not None for x in [q1, q2, q3, q4, q5, q6])
    if answered == total:
        st.markdown("---")
        st.metric("Skóre", f"{score} / {total}")
        if score == total:
            st.balloons()
            st.success("Výborně, máte vše správně.")
        elif score >= 4:
            st.info("Velmi dobré. Je vidět, že látce rozumíte.")
        else:
            st.warning("Doporučuji projít ještě jednou karty Multiplikátor a Komerční banky.")

st.markdown("---")
st.caption("Aplikace pro výuku: bankovní soustava, centrální banka, komerční banky, rezervy a peněžní multiplikátor.")
