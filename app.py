import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# ----------------------------------------------------
# Seitenlayout
# ----------------------------------------------------

st.set_page_config(
    page_title="Haushalts-Simulation VS",
    layout="wide"
)

st.title("🏛 Haushalts-Simulation – Villingen-Schwenningen")

st.markdown("""
Diese Simulation zeigt vereinfacht, wie finanzielle Entscheidungen
den Handlungsspielraum der Stadtverwaltung beeinflussen können.

Bürger können hier verschiedene Szenarien ausprobieren und sehen,
wie sich Entscheidungen auf Haushalt, Projekte und Bürgerkosten auswirken.
""")

# ----------------------------------------------------
# Grundwerte
# ----------------------------------------------------

EINWOHNER = 90000
M_FIX = 100

# ----------------------------------------------------
# Sidebar
# ----------------------------------------------------

st.sidebar.header("Simulation einstellen")

personal = st.sidebar.slider(
    "Personalstellen Veränderung",
    -20, 40, 0
)

investitionen = st.sidebar.slider(
    "Investitionen Infrastruktur",
    -50, 50, 0
)

kultur = st.sidebar.slider(
    "Kultur & Veranstaltungen",
    -20, 20, 0
)

vereine = st.sidebar.slider(
    "Vereinsförderung",
    -20, 20, 0
)

st.sidebar.subheader("Neue Einnahmen prüfen")

grundsteuer_c = st.sidebar.checkbox("Grundsteuer C")
zweitwohnsitzsteuer = st.sidebar.checkbox("Zweitwohnsitzsteuer")
verpackungssteuer = st.sidebar.checkbox("Verpackungssteuer")

st.sidebar.subheader("Sondersituation")

krise = st.sidebar.toggle(
    "Krisenmodus aktivieren",
    help="Simuliert außergewöhnliche Belastungen für den Haushalt"
)

# ----------------------------------------------------
# Einnahmen
# ----------------------------------------------------

steuer_einnahmen = 0

if grundsteuer_c:
    steuer_einnahmen += 20

if zweitwohnsitzsteuer:
    steuer_einnahmen += 10

if verpackungssteuer:
    steuer_einnahmen += 15

# ----------------------------------------------------
# Krisenkosten
# ----------------------------------------------------

krisenkosten = 0

if krise:
    krisenkosten = 40

# ----------------------------------------------------
# Gesamtkosten
# ----------------------------------------------------

kosten = personal * 2 + investitionen + kultur + vereine + krisenkosten

# Haushaltspool
pool = steuer_einnahmen - kosten

# Motor
motor = M_FIX + pool

# Motorstottern im Krisenmodus
motor_anzeige = motor

if krise:
    motor_anzeige = motor - 10

# ----------------------------------------------------
# Lastenverteilung
# ----------------------------------------------------

v_rev_net = max(0, steuer_einnahmen * 0.6)
s_rev_net = max(0, steuer_einnahmen * 0.4)

if pool < 0:
    v_rev_net = abs(pool) * 0.55
    s_rev_net = abs(pool) * 0.45

gesamt_last = v_rev_net + s_rev_net

if gesamt_last > 0:

    v_pct = (v_rev_net / gesamt_last) * 100
    s_pct = (s_rev_net / gesamt_last) * 100

else:

    v_pct = 50
    s_pct = 50

# ----------------------------------------------------
# Kosten pro Bürger
# ----------------------------------------------------

kosten_pro_buerger = (pool * 1_000_000) / EINWOHNER if pool != 0 else 0

# ----------------------------------------------------
# Gauge Funktion
# ----------------------------------------------------

def make_gauge(value, title):

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "black"},
            'steps': [
                {'range': [0, 40], 'color': "red"},
                {'range': [40, 70], 'color': "orange"},
                {'range': [70, 100], 'color': "green"}
            ]
        }
    ))

    return fig

# ----------------------------------------------------
# Fairness Balken
# ----------------------------------------------------

def fairness_balken(v_pct, s_pct):

    fig = go.Figure()

    fig.add_bar(
        x=["Lastenverteilung"],
        y=[v_pct],
        name="Villingen"
    )

    fig.add_bar(
        x=["Lastenverteilung"],
        y=[s_pct],
        name="Schwenningen"
    )

    fig.update_layout(
        barmode="stack",
        height=300
    )

    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------
# Haushaltsampel
# ----------------------------------------------------

def haushalts_ampel(motor):

    if motor >= 120:
        st.success("🟢 Haushalt stabil – Investitionen möglich")

    elif motor >= 90:
        st.warning("🟡 Haushalt angespannt – Entscheidungen müssen abgewogen werden")

    else:
        st.error("🔴 Haushalt unter Druck – Einsparungen oder neue Einnahmen nötig")

# ----------------------------------------------------
# Projektstatus
# ----------------------------------------------------

def projekt_status(motor):

    st.subheader("🏗 Mögliche Auswirkungen auf Projekte")

    if motor >= 120:

        st.write("✔ Infrastrukturprojekte können umgesetzt werden")
        st.write("✔ Kulturveranstaltungen bleiben gesichert")
        st.write("✔ Vereinsförderung bleibt stabil")

    elif motor >= 90:

        st.write("⚠ Einige Projekte könnten verschoben werden")
        st.write("⚠ Veranstaltungsbudgets könnten reduziert werden")

    else:

        st.write("❗ Einsparungen wahrscheinlich bei:")
        st.write("- Veranstaltungen")
        st.write("- Vereinsförderung")
        st.write("- Stadtentwicklungsprojekten")

# ----------------------------------------------------
# Investitionsdiagramm
# ----------------------------------------------------

st.subheader("📊 Verteilung der Investitionen")

invest_data = {
    "Bereich": ["Personal", "Infrastruktur", "Kultur", "Vereine"],
    "Wert": [
        abs(personal),
        abs(investitionen),
        abs(kultur),
        abs(vereine)
    ]
}

df = pd.DataFrame(invest_data)

fig = px.pie(
    df,
    values="Wert",
    names="Bereich",
    title="Investitionsstruktur"
)

st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------
# Layout Gauges
# ----------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "⚙ Motor Stadtverwaltung",
        f"{motor_anzeige:.1f}",
        delta=f"{motor_anzeige - M_FIX:.1f}"
    )

    haushalts_ampel(motor)

with col2:

    st.plotly_chart(
        make_gauge(v_pct, "Budgetkraft Villingen"),
        use_container_width=True
    )

    st.plotly_chart(
        make_gauge(s_pct, "Budgetkraft Schwenningen"),
        use_container_width=True
    )

# ----------------------------------------------------
# Krisenwarnung
# ----------------------------------------------------

if krise:

    st.warning(
        "⚠ Krisenmodus aktiv – außergewöhnliche Belastungen für den Haushalt."
    )

    st.info(
        "Der Motor der Stadtverwaltung gerät unter Druck und verliert Leistungsfähigkeit."
    )

# ----------------------------------------------------
# Lastenverteilung
# ----------------------------------------------------

st.subheader("⚖ Verteilung der finanziellen Last")

st.write(f"Villingen trägt etwa **{v_pct:.0f}%**, Schwenningen etwa **{s_pct:.0f}%**")

fairness_balken(v_pct, s_pct)

# ----------------------------------------------------
# Kosten pro Bürger
# ----------------------------------------------------

st.subheader("👥 Auswirkung pro Einwohner")

st.metric(
    "Kosten / Entlastung pro Einwohner",
    f"{kosten_pro_buerger:.2f} €"
)

# ----------------------------------------------------
# Projektstatus
# ----------------------------------------------------

projekt_status(motor)

# ----------------------------------------------------
# Bürgererklärung
# ----------------------------------------------------

with st.expander("📖 Erklärung für Bürgerinnen und Bürger"):

    st.write("""
Der **Motor der Stadtverwaltung** ist ein Symbol für die finanzielle Leistungsfähigkeit der Stadt.

Wenn der Motor stark läuft, kann die Stadt:

- Infrastrukturprojekte umsetzen
- Kulturveranstaltungen unterstützen
- Vereine fördern
- neue Projekte starten

Wenn der Motor schwächer wird, muss die Stadt:

- Ausgaben reduzieren
- Projekte verschieben
- neue Einnahmen prüfen
""")

    st.write("""
Die Regler auf der linken Seite erlauben es, verschiedene politische Entscheidungen
zu simulieren, zum Beispiel:

- mehr Personal
- mehr Investitionen
- Kürzungen bei Veranstaltungen
""")

    st.write("""
Der **Krisenmodus** simuliert außergewöhnliche Belastungen für den Haushalt,
z.B.:

- wirtschaftliche Krisen
- plötzliche Mehrkosten
- unerwartete Einnahmeausfälle
""")

# ----------------------------------------------------
# Disclaimer
# ----------------------------------------------------

st.caption("""
Diese Simulation ist ein vereinfachtes Modell und stellt keine offiziellen
Haushaltszahlen der Stadt Villingen-Schwenningen dar.

Die Ergebnisse dienen ausschließlich zur Veranschaulichung möglicher
politischer und finanzieller Szenarien.
""")