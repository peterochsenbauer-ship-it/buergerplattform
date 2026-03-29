import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="Haushalts-Simulation VS", layout="wide")

st.title("Haushalts-Simulation – Doppelstadt Villingen-Schwenningen")

st.markdown("""
Diese Simulation zeigt vereinfacht, wie sich politische Entscheidungen
auf den Haushalt der Doppelstadt Villingen-Schwenningen auswirken können.

Die Stadt besteht aus zwei großen Stadtteilen:

**V = Villingen**  
**S = Schwenningen**
""")

# Grundwerte

EINWOHNER = 90000
EINWOHNER_V = 43000
EINWOHNER_S = 47000

M_FIX = 100


# Haushaltsentwicklung

haushalt = pd.DataFrame({
    "Jahr":[2020,2021,2022,2023,2024],
    "Haushalt":[105,110,98,102,95]
})


# Sidebar

st.sidebar.header("Simulation einstellen")

szenario = st.sidebar.radio(
    "Haushaltsstrategie",
    [
        "Status quo",
        "Sparhaushalt",
        "Investitionshaushalt"
    ]
)

personal = st.sidebar.slider("Personalstellen Veränderung",-20,40,0)

gesamtinvest = st.sidebar.slider(
    "Gesamtinvestitionen Infrastruktur",
    -50,80,0
)

kultur = st.sidebar.slider("Kultur & Veranstaltungen",-20,20,0)

vereine = st.sidebar.slider("Vereinsförderung",-20,20,0)


# Investitionsverteilung

st.sidebar.subheader("Investitionsverteilung")

anteil_v = st.sidebar.slider(
    "Investitionen Villingen %",
    0,100,50
)

anteil_s = 100 - anteil_v

st.sidebar.write(f"Schwenningen Anteil: {anteil_s}%")


# Haushaltsbereiche

st.sidebar.subheader("Investitionsstruktur")

schule = st.sidebar.slider("Schulen",0,100,30)
verkehr = st.sidebar.slider("Straßen / Verkehr",0,100,25)
kultur_i = st.sidebar.slider("Kultur",0,100,15)
sport = st.sidebar.slider("Sport",0,100,15)
soziales = st.sidebar.slider("Soziales",0,100,15)


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


# Szenario Logik

if szenario == "Sparhaushalt":

    personal = -5
    gesamtinvest = -20
    kultur = -5
    vereine = -5

elif szenario == "Investitionshaushalt":

    personal = 10
    gesamtinvest = 40
    kultur = 10
    vereine = 5


# Einnahmen

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

kosten = personal*2 + kultur + vereine + krisenkosten


# Haushaltsspielraum

pool = steuer_einnahmen - kosten


# Investitionen nach Stadtteil

invest_v = gesamtinvest * (anteil_v/100)
invest_s = gesamtinvest * (anteil_s/100)


# Bevölkerungsgewichtung

gewicht_v = EINWOHNER_V / EINWOHNER
gewicht_s = EINWOHNER_S / EINWOHNER


# Motorwerte

motor_v = M_FIX + pool + invest_v*gewicht_v
motor_s = M_FIX + pool + invest_s*gewicht_s


# Kriseneffekt

if krise:

    motor_v -= 10
    motor_s -= 10


# Kosten pro Bürger

kosten_pro_buerger = pool*1000000 / EINWOHNER if pool != 0 else 0


# Gauge

def gauge(value,title):

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text':title},
        gauge={
            'axis':{'range':[0,150]},
            'steps':[
                {'range':[0,60],'color':"red"},
                {'range':[60,100],'color':"orange"},
                {'range':[100,150],'color':"green"}
            ]
        }
    ))

    return fig


# Haushaltsampel

def haushalts_ampel(pool):

    if pool > 20:

        st.success("🟢 Haushalt stabil – Investitionen möglich")

    elif pool > -20:

        st.warning("🟡 Haushalt angespannt – Prioritäten nötig")

    else:

        st.error("🔴 Haushalt unter Druck – Einsparungen oder neue Einnahmen nötig")


# Haushaltsdiagramm

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


# Stadtteilentwicklung

st.subheader("Entwicklung der Stadtteile")

col1,col2 = st.columns(2)

with col1:

    st.plotly_chart(
        gauge(motor_v,"Villingen"),
        use_container_width=True
    )

with col2:

    st.plotly_chart(
        gauge(motor_s,"Schwenningen"),
        use_container_width=True
    )


haushalts_ampel(pool)


# Investitionsverteilung Stadtteile

st.subheader("Investitionsverteilung zwischen den Stadtteilen")

labels = ["Villingen","Schwenningen"]
values = [anteil_v,anteil_s]

fig_pie = go.Figure(
    data=[go.Pie(labels=labels,values=values)]
)

st.plotly_chart(fig_pie,use_container_width=True)


# Investitionsstruktur

st.subheader("Investitionsstruktur")

labels = [
    "Schulen",
    "Straßen",
    "Kultur",
    "Sport",
    "Soziales"
]

values = [
    schule,
    verkehr,
    kultur_i,
    sport,
    soziales
]

fig_struktur = go.Figure(
    data=[go.Pie(labels=labels,values=values)]
)

st.plotly_chart(fig_struktur,use_container_width=True)


# Bürgerkosten

st.subheader("Auswirkung pro Einwohner")

st.metric(
    "Kosten / Entlastung pro Einwohner",
    f"{kosten_pro_buerger:.2f} €"
)


# Projektstatus

st.subheader("Mögliche Projekte")

if pool > 20:

    st.write("✔ Neubau Hallenbad möglich")
    st.write("✔ Ausbau Radwegenetz")
    st.write("✔ Schulsanierungen")

elif pool > -20:

    st.write("⚠ Projekte müssen priorisiert werden")
    st.write("✔ Schulsanierung wahrscheinlich")
    st.write("⚠ Radwege teilweise")

else:

    st.write("❌ Große Projekte derzeit nicht finanzierbar")
    st.write("⚠ Nur notwendige Investitionen")


# Bürgererklärung

with st.expander("Erklärung der Simulation für Bürgerinnen und Bürger"):

    st.write("""
Diese Simulation zeigt vereinfacht, wie sich politische Entscheidungen
auf den Haushalt der Doppelstadt Villingen-Schwenningen auswirken können.

Die Stadt besteht aus zwei großen Stadtteilen: Villingen und Schwenningen.
Beide teilen sich einen gemeinsamen Haushalt, gleichzeitig müssen
Investitionen und Projekte zwischen den Stadtteilen verteilt werden.

Der Haushalt bestimmt, wie viel Geld für Infrastruktur,
Schulen, Straßen, Kultur, Sport oder soziale Einrichtungen
zur Verfügung steht.

Die beiden Anzeigen oben zeigen, wie sich politische Entscheidungen
auf die Entwicklung der beiden Stadtteile auswirken können.

Ein höherer Wert bedeutet mehr Handlungsspielraum für Investitionen
und eine stabilere finanzielle Situation.

In der Simulation können verschiedene Entscheidungen ausprobiert werden:

• Höhe der Investitionen  
• Verteilung zwischen Villingen und Schwenningen  
• Prioritäten bei Schulen, Verkehr oder Kultur  
• mögliche neue Einnahmen  

Die Ergebnisse zeigen, wie sich diese Entscheidungen auf den
finanziellen Handlungsspielraum der Stadt auswirken können.

Die dargestellten Werte sind keine offiziellen Haushaltszahlen.
Die Simulation dient ausschließlich dazu, Zusammenhänge verständlich
darzustellen und verschiedene Szenarien auszuprobieren.
""")