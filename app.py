import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# -------------------------------------------------
# SEITENEINSTELLUNG
# -------------------------------------------------

st.set_page_config(
    page_title="Bürgerhaushalt Villingen-Schwenningen",
    layout="wide"
)

# -------------------------------------------------
# TITEL
# -------------------------------------------------

st.title("Bürgerhaushalt Simulation")
st.subheader("Doppelhaushalt der Stadt Villingen-Schwenningen")

st.markdown("""
Diese interaktive Simulation zeigt vereinfacht, wie politische Entscheidungen den Haushalt der Stadt beeinflussen können.

Die Stadt besteht aus zwei Stadtteilen:

**V = Villingen**  
**S = Schwenningen**

Beide Stadtteile besitzen eigene Einnahmen und Ausgaben, gehören jedoch zu einem gemeinsamen städtischen Haushalt.
""")

# -------------------------------------------------
# SIDEBAR - EINSTELLUNGEN
# -------------------------------------------------

st.sidebar.header("Haushaltseinstellungen")

steuer_v = st.sidebar.slider(
    "Steuereinnahmen Villingen (Mio €)",
    0, 300, 150
)

steuer_s = st.sidebar.slider(
    "Steuereinnahmen Schwenningen (Mio €)",
    0, 300, 140
)

ausgaben_v = st.sidebar.slider(
    "Laufende Ausgaben Villingen (Mio €)",
    0, 300, 120
)

ausgaben_s = st.sidebar.slider(
    "Laufende Ausgaben Schwenningen (Mio €)",
    0, 300, 110
)

invest_total = st.sidebar.slider(
    "Gesamtinvestitionen Stadt (Mio €)",
    0, 200, 60
)

# -------------------------------------------------
# INVESTITIONSVERTEILUNG
# -------------------------------------------------

st.sidebar.subheader("Investitionsverteilung")

anteil_v = st.sidebar.slider(
    "Investitionsanteil Villingen (%)",
    0,
    100,
    50
)

anteil_s = 100 - anteil_v

invest_v = invest_total * anteil_v / 100
invest_s = invest_total * anteil_s / 100

# -------------------------------------------------
# SALDENBERECHNUNG
# -------------------------------------------------

saldo_v = steuer_v - ausgaben_v - invest_v
saldo_s = steuer_s - ausgaben_s - invest_s

saldo_gesamt = saldo_v + saldo_s

# -------------------------------------------------
# TACHO FUNKTION
# -------------------------------------------------

def gauge(title, value):

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title},
        gauge={
            "axis": {"range": [-150, 150]},
            "bar": {"color": "black"},
            "steps": [
                {"range": [-150, 0], "color": "#ffcccc"},
                {"range": [0, 75], "color": "#ccffcc"},
                {"range": [75, 150], "color": "#99ff99"},
            ],
        }
    ))

    return fig

# -------------------------------------------------
# HAUSHALTSTACHOS
# -------------------------------------------------

col1, col2 = st.columns(2)

with col1:
    st.subheader("Stadtteil Villingen (V)")
    st.plotly_chart(
        gauge("Haushaltssaldo Villingen (Mio €)", saldo_v),
        use_container_width=True
    )

with col2:
    st.subheader("Stadtteil Schwenningen (S)")
    st.plotly_chart(
        gauge("Haushaltssaldo Schwenningen (Mio €)", saldo_s),
        use_container_width=True
    )

# -------------------------------------------------
# GESAMTHAUSHALT
# -------------------------------------------------

st.header("Gesamthaushalt der Stadt")

st.metric(
    "Gesamtsaldo Villingen + Schwenningen (Mio €)",
    round(saldo_gesamt, 2)
)

# -------------------------------------------------
# INVESTITIONSGRAFIK
# -------------------------------------------------

st.header("Investitionsverteilung")

invest_df = pd.DataFrame({
    "Stadtteil": ["Villingen", "Schwenningen"],
    "Investitionen": [invest_v, invest_s]
})

st.bar_chart(invest_df.set_index("Stadtteil"))

# -------------------------------------------------
# HAUSHALTSENTWICKLUNG
# -------------------------------------------------

st.header("Haushaltsentwicklung (Simulation)")

jahre = list(range(2025, 2035))

entwicklung = []

v = saldo_v
s = saldo_s

for jahr in jahre:

    v = v + saldo_v * 0.25
    s = s + saldo_s * 0.25

    entwicklung.append({
        "Jahr": jahr,
        "Villingen": v,
        "Schwenningen": s
    })

df = pd.DataFrame(entwicklung)

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df["Jahr"],
    y=df["Villingen"],
    mode="lines+markers",
    name="Villingen"
))

fig.add_trace(go.Scatter(
    x=df["Jahr"],
    y=df["Schwenningen"],
    mode="lines+markers",
    name="Schwenningen"
))

st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------
# BÜRGERERKLÄRUNG
# -------------------------------------------------

st.header("Bürgererklärung")

with st.expander("Was zeigt diese Simulation?"):

    st.markdown("""
### Zweck der Simulation

Diese Simulation soll Bürgerinnen und Bürgern verständlich machen, wie ein kommunaler Haushalt funktioniert.

Dabei wird die Doppelstruktur der Stadt berücksichtigt:

• Stadtteil **Villingen (V)**  
• Stadtteil **Schwenningen (S)**  

Beide haben eigene Einnahmen und Ausgaben, bilden aber zusammen den Gesamthaushalt der Stadt.

---

### Steuereinnahmen

Die Steuereinnahmen setzen sich vereinfacht aus folgenden Quellen zusammen:

• Gewerbesteuer  
• Einkommensteueranteil  
• Grundsteuer  
• weitere kommunale Einnahmen

Diese Einnahmen stehen der Stadt zur Finanzierung öffentlicher Aufgaben zur Verfügung.

---

### Laufende Ausgaben

Laufende Ausgaben sind Kosten, die jedes Jahr entstehen, zum Beispiel:

• Schulen und Kindergärten  
• Straßenunterhalt  
• Feuerwehr und Sicherheit  
• Verwaltung  
• Kultur und Sport  
• soziale Leistungen

Diese Ausgaben sind oft langfristig gebunden und lassen sich nur begrenzt kurzfristig verändern.

---

### Investitionen

Investitionen sind größere Ausgaben für langfristige Projekte, zum Beispiel:

• Bau oder Sanierung von Schulen  
• neue Straßen oder Brücken  
• Digitalisierung der Verwaltung  
• Klimaschutzmaßnahmen  
• Infrastrukturprojekte

In der Simulation können diese Investitionen zwischen den beiden Stadtteilen aufgeteilt werden.

---

### Bedeutung der Tachos

Die beiden Tachos zeigen den **Haushaltssaldo der jeweiligen Stadtteile**.

Berechnung:

Steuereinnahmen  
minus laufende Ausgaben  
minus Investitionen  

Ergebnis = Haushaltsüberschuss oder Haushaltsdefizit.

---

### Farbbereiche

**Grün**

Der Haushalt ist ausgeglichen oder im Überschuss.

Die Stadt kann Rücklagen bilden oder Schulden abbauen.

**Rot**

Der Haushalt hat ein Defizit.

Langfristig müssten dann Schulden aufgenommen oder Ausgaben reduziert werden.

---

### Haushaltsentwicklung

Die Grafik zeigt eine vereinfachte Projektion der zukünftigen Haushaltsentwicklung.

Sie verdeutlicht, dass heutige Entscheidungen langfristige Auswirkungen haben können.

Ein dauerhaftes Defizit kann langfristig zu steigenden Schulden führen.

Ein Überschuss ermöglicht dagegen Investitionen oder Rücklagenbildung.

---

### Wichtig

Diese Simulation ist **eine vereinfachte Darstellung** eines kommunalen Haushalts.

Der reale Haushalt einer Stadt besteht aus vielen hundert Einzelpositionen und gesetzlichen Vorgaben.

Die Simulation dient ausschließlich dazu, die grundlegenden Zusammenhänge verständlich zu machen.
""")

with st.expander("Wie funktioniert der Doppelhaushalt der Stadt?"):

    st.markdown("""
Viele Städte planen ihren Haushalt für **zwei Jahre gleichzeitig**.  
Das nennt man einen **Doppelhaushalt**.

Dabei werden Einnahmen und Ausgaben für zwei Jahre im Voraus geplant.

Ziele eines Doppelhaushalts:

• mehr Planungssicherheit  
• langfristige Investitionsplanung  
• effizientere Verwaltung

In dieser Simulation wird vereinfacht dargestellt, wie sich Entscheidungen über mehrere Jahre auswirken können.

---

### Warum werden Villingen und Schwenningen getrennt dargestellt?

Villingen-Schwenningen besteht historisch aus zwei Städten, die heute gemeinsam verwaltet werden.

Viele Bürger identifizieren sich weiterhin stark mit ihrem jeweiligen Stadtteil.

Die Simulation zeigt daher getrennt:

• Einnahmen  
• Ausgaben  
• Investitionen  

für beide Stadtteile.

So wird sichtbar, wie sich politische Entscheidungen auf die beiden Teile der Stadt auswirken können.
""")