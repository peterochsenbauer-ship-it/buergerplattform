import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="Haushalts-Simulation VS", layout="wide")

st.title("Haushalts-Simulation – Villingen-Schwenningen")

st.markdown("""
Diese Simulation zeigt vereinfacht, wie sich finanzielle Entscheidungen
auf den Handlungsspielraum der Stadtverwaltung auswirken könnten.
""")

# Grundwerte
EINWOHNER = 90000
M_FIX = 100

# Haushaltsentwicklung (Beispieldaten)
haushalt = pd.DataFrame({
    "Jahr":[2020,2021,2022,2023,2024],
    "Haushalt":[105,110,98,102,95]
})

# Sidebar
st.sidebar.header("Simulation einstellen")

# Szenario Auswahl
st.sidebar.subheader("Haushaltsstrategie")

szenario = st.sidebar.radio(
    "Szenario wählen",
    [
        "Status quo",
        "Sparhaushalt",
        "Investitionshaushalt"
    ]
)

personal = st.sidebar.slider("Personalstellen Veränderung", -20, 40, 0)

investitionen = st.sidebar.slider(
    "Investitionen Infrastruktur",
    -50,50,0)

kultur = st.sidebar.slider(
    "Kultur & Veranstaltungen",
    -20,20,0)

vereine = st.sidebar.slider(
    "Vereinsförderung",
    -20,20,0)

st.sidebar.subheader("Neue Einnahmen prüfen")

grundsteuer_c = st.sidebar.checkbox("Grundsteuer C")

zweitwohnsitzsteuer = st.sidebar.checkbox("Zweitwohnsitzsteuer")

verpackungssteuer = st.sidebar.checkbox("Verpackungssteuer")

st.sidebar.subheader("Sondersituation")

krise = st.sidebar.toggle(
    "Krisenmodus aktivieren",
    help="Simuliert außergewöhnliche Belastungen für den Haushalt"
)

# Szenario Logik

if szenario == "Sparhaushalt":

    personal = -5
    investitionen = -20
    kultur = -5
    vereine = -5

elif szenario == "Investitionshaushalt":

    personal = 10
    investitionen = 30
    kultur = 10
    vereine = 5

# Einnahmen berechnen
steuer_einnahmen = 0

if grundsteuer_c:
    steuer_einnahmen += 20

if zweitwohnsitzsteuer:
    steuer_einnahmen += 10

if verpackungssteuer:
    steuer_einnahmen += 15

# Krisenkosten
krisenkosten = 0

if krise:
    krisenkosten = 40

# Gesamtkosten
kosten = personal*2 + investitionen + kultur + vereine + krisenkosten

# Haushaltspool
pool = steuer_einnahmen - kosten

# Motor
motor = M_FIX + pool

# Motorstottern im Krisenmodus
motor_anzeige = motor

if krise:
    motor_anzeige = motor - 10

# Lastenverteilung
v_rev_net = max(0, steuer_einnahmen*0.6)
s_rev_net = max(0, steuer_einnahmen*0.4)

if pool < 0:
    v_rev_net = abs(pool)*0.55
    s_rev_net = abs(pool)*0.45

v_pct = (v_rev_net/(v_rev_net+s_rev_net))*100 if (v_rev_net+s_rev_net)>0 else 0
s_pct = (s_rev_net/(v_rev_net+s_rev_net))*100 if (v_rev_net+s_rev_net)>0 else 0

# Kosten pro Bürger
kosten_pro_buerger = pool*1000000 / EINWOHNER if pool != 0 else 0


# Gauge Funktion
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


# Fairnessbalken
def fairness_balken(v_pct,s_pct):

    fig = go.Figure()

    fig.add_bar(
        x=["Lastenverteilung"],
        y=[v_pct],
        name="V"
    )

    fig.add_bar(
        x=["Lastenverteilung"],
        y=[s_pct],
        name="S"
    )

    fig.update_layout(
        barmode="stack",
        height=300
    )

    st.plotly_chart(fig,use_container_width=True)


# Haushaltsampel
def haushalts_ampel(motor):

    if motor >= 120:
        st.success("🟢 Haushalt stabil – Investitionen möglich")

    elif motor >= 90:
        st.warning("🟡 Haushalt angespannt – Entscheidungen müssen abgewogen werden")

    else:
        st.error("🔴 Haushalt unter Druck – Einsparungen oder neue Einnahmen nötig")


# Projektstatus
def projekt_status(motor):

    st.subheader("Städtische Projekte")

    if motor >= 120:

        st.write("✔ Neubau Hallenbad möglich")
        st.write("✔ Schulsanierungen möglich")
        st.write("✔ Ausbau Radwegenetz")

    elif motor >= 90:

        st.write("⚠ Hallenbad könnte verschoben werden")
        st.write("✔ Schulsanierung wahrscheinlich")
        st.write("⚠ Radwege werden reduziert")

    else:

        st.write("❗ Projekte unter Druck")

        st.write("❌ Hallenbad gestoppt")
        st.write("⚠ Schulsanierung reduziert")
        st.write("⚠ Radwege verschoben")


# Haushaltsentwicklung Diagramm
st.subheader("Haushaltsentwicklung")

fig_hist = go.Figure()

fig_hist.add_trace(
    go.Scatter(
        x=haushalt["Jahr"],
        y=haushalt["Haushalt"],
        mode="lines+markers",
        name="Haushaltslage"
    )
)

st.plotly_chart(fig_hist, use_container_width=True)


# Layout
col1,col2 = st.columns(2)

with col1:

    st.metric(
        "Motor Stadtverwaltung",
        f"{motor_anzeige:.1f}",
        delta=f"{motor_anzeige-M_FIX:.1f}"
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


# Krisenwarnung
if krise:

    st.warning(
    "⚠ Krisenmodus aktiv – außergewöhnliche Belastungen für den Haushalt."
    )

    st.info(
    "Der Motor der Stadtverwaltung gerät unter Druck und verliert Leistungsfähigkeit."
    )


# Lastenverteilung
st.subheader("Verteilung der finanziellen Last")

st.write(f"V zahlt {v_pct:.0f}% | S zahlt {s_pct:.0f}%")

fairness_balken(v_pct,s_pct)


# Investitionsverteilung
st.subheader("Investitionsverteilung")

labels = ["Schulen","Straßen","Kultur","Sport","Soziales"]

values = [30,25,15,15,15]

fig_pie = go.Figure(
    data=[go.Pie(labels=labels, values=values)]
)

st.plotly_chart(fig_pie, use_container_width=True)


# Kosten pro Bürger
st.subheader("Auswirkung pro Einwohner")

st.metric(
"Kosten / Entlastung pro Einwohner",
f"{kosten_pro_buerger:.2f} €"
)


# Projektstatus
projekt_status(motor)


# Erklärung
with st.expander("Erklärung für Bürger"):

    st.write("""
Der „Motor“ steht symbolisch für die Handlungsfähigkeit der Stadtverwaltung.

Wenn der Motor stark ist, hat die Stadt mehr finanziellen Spielraum.
Wenn er schwächer wird, müssen Ausgaben reduziert oder Einnahmen erhöht werden.

Die Regler erlauben es, verschiedene Szenarien auszuprobieren.

Der Krisenschalter simuliert außergewöhnliche Belastungen
(zum Beispiel wirtschaftliche Krisen oder unerwartete Ausgaben).
""")


# Disclaimer
st.caption("""
Diese Simulation ist ein vereinfachtes Modell und stellt keine offiziellen
Haushaltszahlen der Stadt dar. Die Ergebnisse dienen nur zur
Veranschaulichung möglicher Szenarien.
""")