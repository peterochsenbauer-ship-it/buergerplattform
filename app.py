import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="Haushalts-Simulation VS", layout="wide")

st.title("Haushalts-Simulation – Villingen-Schwenningen")

st.markdown("""
Diese Simulation zeigt vereinfacht, wie politische Entscheidungen
den finanziellen Handlungsspielraum der Stadt beeinflussen können.
""")

# Grundwerte
EINWOHNER = 90000
MOTOR_BASIS = 100

# Haushaltsentwicklung
haushalt = pd.DataFrame({
    "Jahr":[2020,2021,2022,2023,2024],
    "Haushalt":[105,110,98,102,95]
})

# Sidebar
st.sidebar.header("Simulation einstellen")

# Szenario
szenario = st.sidebar.selectbox(
    "Szenario wählen",
    ["Status quo","Sparhaushalt","Investitionshaushalt"]
)

# Standardwerte
personal_default = 0
invest_default = 0
kultur_default = 0
vereine_default = 0

if szenario == "Sparhaushalt":
    personal_default = -5
    invest_default = -20
    kultur_default = -5
    vereine_default = -5

if szenario == "Investitionshaushalt":
    personal_default = 10
    invest_default = 30
    kultur_default = 10
    vereine_default = 5


# Slider
st.sidebar.subheader("Politische Entscheidungen")

personal = st.sidebar.slider(
    "Personalstellen Veränderung",
    -20,40,personal_default
)

investitionen = st.sidebar.slider(
    "Investitionen Infrastruktur",
    -50,80,invest_default
)

kultur = st.sidebar.slider(
    "Kultur & Veranstaltungen",
    -20,20,kultur_default
)

vereine = st.sidebar.slider(
    "Vereinsförderung",
    -20,20,vereine_default
)

# Einnahmen
st.sidebar.subheader("Neue Einnahmen")

grundsteuer_c = st.sidebar.checkbox("Grundsteuer C")
zweitwohnsitzsteuer = st.sidebar.checkbox("Zweitwohnsitzsteuer")
verpackungssteuer = st.sidebar.checkbox("Verpackungssteuer")

# Krisenmodus
st.sidebar.subheader("Sondersituation")

krise = st.sidebar.toggle(
    "Krisenmodus aktivieren"
)

# Einnahmen berechnen
steuer_einnahmen = 0

if grundsteuer_c:
    steuer_einnahmen += 20

if zweitwohnsitzsteuer:
    steuer_einnahmen += 10

if verpackungssteuer:
    steuer_einnahmen += 15

# Krisenkosten
krisenkosten = 40 if krise else 0

# Kosten
kosten = personal*2 + investitionen + kultur + vereine + krisenkosten

# Haushaltspool
pool = steuer_einnahmen - kosten

# Motor
motor = MOTOR_BASIS + pool

motor_anzeige = motor
if krise:
    motor_anzeige -= 10

# Kosten pro Einwohner
kosten_pro_buerger = pool*1000000 / EINWOHNER if pool != 0 else 0

# Lastenverteilung
v_rev_net = max(0, steuer_einnahmen*0.6)
s_rev_net = max(0, steuer_einnahmen*0.4)

if pool < 0:
    v_rev_net = abs(pool)*0.55
    s_rev_net = abs(pool)*0.45

v_pct = (v_rev_net/(v_rev_net+s_rev_net))*100 if (v_rev_net+s_rev_net)>0 else 0
s_pct = (s_rev_net/(v_rev_net+s_rev_net))*100 if (v_rev_net+s_rev_net)>0 else 0


# Investitionsverteilung (DYNAMISCH)

st.sidebar.subheader("Investitionsprioritäten")

schulen = st.sidebar.slider("Schulen",0,50,30)
strassen = st.sidebar.slider("Straßen",0,50,25)
kultur_i = st.sidebar.slider("Kulturprojekte",0,50,15)
sport = st.sidebar.slider("Sportanlagen",0,50,15)
soziales = st.sidebar.slider("Soziales",0,50,15)

total = schulen + strassen + kultur_i + sport + soziales

if total == 0:
    total = 1

labels = ["Schulen","Straßen","Kultur","Sport","Soziales"]

values = [
    schulen/total*investitionen,
    strassen/total*investitionen,
    kultur_i/total*investitionen,
    sport/total*investitionen,
    soziales/total*investitionen
]


# Gauge
def make_gauge(value,title):

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text':title},
        gauge={
            'axis':{'range':[0,100]},
            'steps':[
                {'range':[0,40],'color':"red"},
                {'range':[40,70],'color':"orange"},
                {'range':[70,100],'color':"green"}
            ]
        }
    ))

    return fig


# Haushaltsampel
def haushalts_ampel(motor):

    if motor >= 120:
        st.success("🟢 Haushalt stabil – Investitionen möglich")

    elif motor >= 90:
        st.warning("🟡 Haushalt angespannt")

    else:
        st.error("🔴 Haushalt unter Druck")


# Haushaltsentwicklung
st.subheader("Haushaltsentwicklung")

fig_hist = go.Figure()

fig_hist.add_trace(
    go.Scatter(
        x=haushalt["Jahr"],
        y=haushalt["Haushalt"],
        mode="lines+markers"
    )
)

st.plotly_chart(fig_hist,use_container_width=True)


# Layout
col1,col2 = st.columns(2)

with col1:

    st.metric(
        "Motor Stadtverwaltung",
        f"{motor_anzeige:.1f}",
        delta=f"{motor_anzeige-MOTOR_BASIS:.1f}"
    )

    haushalts_ampel(motor)

with col2:

    st.plotly_chart(
        make_gauge(v_pct,"Budgetkraft V"),
        use_container_width=True
    )

    st.plotly_chart(
        make_gauge(s_pct,"Budgetkraft S"),
        use_container_width=True
    )


# Investitionsdiagramm
st.subheader("Investitionsverteilung")

fig_pie = go.Figure(
    data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.3
    )]
)

st.plotly_chart(fig_pie,use_container_width=True)


# Kosten pro Bürger
st.subheader("Auswirkung pro Einwohner")

st.metric(
"Kosten / Entlastung pro Einwohner",
f"{kosten_pro_buerger:.2f} €"
)


# Erklärung
with st.expander("Erklärung für Bürger"):

    st.write("""
Der Motor symbolisiert die Handlungsfähigkeit der Stadtverwaltung.

Politische Entscheidungen beeinflussen Einnahmen und Ausgaben.

Wenn der Motor stark ist, kann die Stadt mehr investieren.
Wenn er schwach ist, müssen Ausgaben reduziert oder Einnahmen erhöht werden.
""")

st.caption("Simulation – vereinfachtes Modell")