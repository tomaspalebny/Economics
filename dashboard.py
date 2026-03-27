import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Economics App Hub", layout="wide")

APPS = {
    "Makroekonomie": [
        {"name": "Makroekonomicky simulator rozpoctu", "url": "https://economics-paleta.streamlit.app/"},
        {"name": "Deficit simulator", "url": "https://economics-deficit.streamlit.app/"},
        {"name": "Smenarna Realny kurz & PPP", "url": "https://economics-real.streamlit.app/"},
        {"name": "ADAS", "url": "https://economics-adas.streamlit.app/"},
        {"name": "Public sector", "url": "https://economics-publsec.streamlit.app/"},
        {"name": "Budget 2", "url": "https://economics-bud2.streamlit.app/"},
        {"name": "Portfolio", "url": "https://economics-portfolio.streamlit.app/"},
    ],
    "Mikroekonomie": [
        {"name": "Predatorske ceny AKZO & moderni test", "url": "https://economics-predator.streamlit.app/"},
        {"name": "Koncentrace", "url": "https://economics-koncentrace.streamlit.app/"},
        {"name": "Firma", "url": "https://economics-firma.streamlit.app/"},
        {"name": "Firma 2", "url": "https://economics-firma2.streamlit.app/"},
    ],
    "Soutěž": [
        {"name": "Predatorske ceny AKZO & moderni test", "url": "https://economics-predator.streamlit.app/"},
        {"name": "Koncentrace", "url": "https://economics-koncentrace.streamlit.app/"},    ],
    "Hry": [
        {"name": "Ceska ekonomika: Hra", "url": "https://simeon-game.streamlit.app/"},
    ],
}

st.title("Economics Dashboard Hub")
st.caption("Kategorizovany rozcestnik vasich Streamlit aplikaci.")

left, right = st.columns([1, 2])

with left:
    st.subheader("Vyber aplikace")
    category = st.selectbox("Kategorie", list(APPS.keys()))
    selected_name = st.selectbox("Aplikace", [a["name"] for a in APPS[category]])
    selected_app = next(a for a in APPS[category] if a["name"] == selected_name)

    st.markdown(f"**URL:** {selected_app['url']}")
    st.link_button("Otevrit v novem panelu", selected_app["url"], use_container_width=True)

    st.divider()
    st.subheader("Rychle odkazy")
    for group, apps in APPS.items():
        st.markdown(f"**{group}**")
        for app in apps:
            st.link_button(app["name"], app["url"], use_container_width=True)

with right:
    st.subheader(f"Nahled: {selected_app['name']}")
    st.warning(
        "U vlozeneho nahledu (iframe) muze dojit k chybe 'Smycka pri presmerovani' "
        "kvuli cookies. Pokud se to stane, otevrete appku tlacitkem v novem panelu."
    )
    show_iframe = st.checkbox("Zkusit vlozeny nahled (iframe)", value=False)

    if show_iframe:
        components.iframe(selected_app["url"], height=900, scrolling=True)
    else:
        st.info(
            "Vlozeny nahled je vypnuty, aby se predeslo redirect loop chybe. "
            "Pouzijte otevreni v novem panelu."
        )

st.divider()
st.markdown("### Jak pridat dalsi app")
st.code(
    """APPS["Nova kategorie"].append({"name": "Moje app", "url": "https://moje-app.streamlit.app/"})""",
    language="python",
)