import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Economics App Hub", layout="wide")

APPS = [
    {"name": "Predatorske ceny AKZO & moderni test", "url": "https://economics-predator.streamlit.app/"},
    {"name": "Koncentrace", "url": "https://economics-koncentrace.streamlit.app/"},
    {"name": "Public sector", "url": "https://economics-publsec.streamlit.app/"},
    {"name": "Makroekonomicky simulator rozpoctu", "url": "https://economics-paleta.streamlit.app/"},
    {"name": "Deficit simulator", "url": "https://economics-deficit.streamlit.app/"},
    {"name": "Smenarna Realny kurz & PPP", "url": "https://economics-real.streamlit.app/"},
    {"name": "ADAS", "url": "https://economics-adas.streamlit.app/"},
    {"name": "Portfolio", "url": "https://economics-portfolio.streamlit.app/"},
    {"name": "Budget 2", "url": "https://economics-bud2.streamlit.app/"},
    {"name": "Firma", "url": "https://economics-firma.streamlit.app/"},
    {"name": "Firma 2", "url": "https://economics-firma2.streamlit.app/"},
    {"name": "Ceska ekonomika: Hra", "url": "https://simeon-game.streamlit.app/"},
]

st.title("Economics Dashboard Hub")
st.caption("Single dashboard to launch and preview your Streamlit apps.")

left, right = st.columns([1, 2])

with left:
    st.subheader("Select app")
    app_names = [a["name"] for a in APPS]
    selected_name = st.selectbox("Available apps", app_names, index=0)
    selected_app = next(a for a in APPS if a["name"] == selected_name)

    st.markdown(f"**URL:** {selected_app['url']}")
    st.link_button("Open selected app in new tab", selected_app["url"], use_container_width=True)

    st.divider()
    st.subheader("Quick launch")
    for app in APPS:
        st.link_button(app["name"], app["url"], use_container_width=True)

with right:
    st.subheader(f"Embedded preview: {selected_app['name']}")
    st.info(
        "Some external Streamlit apps may block embedding in iframe. "
        "If preview is blank, use 'Open selected app in new tab'."
    )
    components.iframe(selected_app["url"], height=900, scrolling=True)

st.divider()
st.markdown("### Add more apps")
st.code(
    """APPS.append({"name": "My New App", "url": "https://my-new-app.streamlit.app/"})""",
    language="python",
)