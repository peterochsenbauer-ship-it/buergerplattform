import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Bürgerhaushalt Simulation", layout="wide")

# -------------------------------------------------
# TITEL
# -------------------------------------------------

st.title("Bürgerhaushalt Simulation")
st.subheader("Doppelhaushalt Villingen-Schwenningen")

st.markdown("""
Diese Simulation zeigt vereinfacht den Haushalt der Stadt Villingen-Schwenningen.

Die Stadt besteht aus zwei Stadtteilen:

**V = Villingen**  
**S = Schwenningen**

Beide besitzen eigene Teilhaushalte, die zusammen den städtischen Gesamthaushalt bilden.
""")

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------

st.sidebar.header("Haushaltseinstellungen")

szenario = st.sidebar.radio(
    "Haushaltsszenario",
    ["Status Quo", "Investitionsoffensive"]
)

# Einnahmen
steuer_v = st.sidebar.slider("Steuereinnahmen Villingen (Mio €)", 0, 300, 150)
steuer_s = st.sidebar.slider("Steuereinnahmen Schwenningen (Mio €)", 0, 300, 140)

# -------------------------------------------------
# AUSGABENSTRUKTUR
# -------------------------------------------------

st.sidebar.subheader("Ausgabenstruktur")

schule_pct = st.sidebar.slider("Schulen (%)", 0, 100, 30)
infra_pct = st.sidebar.slider("Infrastruktur (%)", 0, 100, 30)
kultur_pct = st.sidebar.slider("Kultur (%)", 0, 100, 20)
gesund_pct = st.sidebar.slider("Gesundheit (%)", 0, 100, 20)

gesamt_pct = schule_pct + infra_pct + kultur_pct + gesund_pct

# Normalisierung falls >100
if gesamt_pct == 0:
    gesamt_pct = 1

schule_pct = schule_pct / gesamt_pct
infra_pct = infra_pct / gesamt_pct
kultur_pct = kultur_pct / gesamt_pct
gesund_pct = gesund_pct / gesamt_pct

# Gesamtausgaben
ausgaben_v_total = st.sidebar.slider("Gesamtausgaben Villingen", 0, 300, 120)
ausgaben_s_total = st.sidebar.slider("Gesamtausgaben Schwenningen", 0, 300, 110)

# Aufteilung
schule_v = ausgaben_v_total * schule_pct
infra_v = ausgaben_v_total * infra_pct
kultur_v = ausgaben_v_total * kultur_pct
gesund_v = ausgaben_v_total * gesund_pct

schule_s = ausgaben_s_total * schule_pct
infra_s = ausgaben_s_total * infra_pct
kultur_s = ausgaben_s_total * kultur_pct
gesund_s = ausgaben_s_total * gesund_pct

# -------------------------------------------------
# INVESTITIONEN
# -------------------------------------------------

st.sidebar.subheader("Investitionen")

if szenario == "Status Quo":
    invest_total = st.sidebar.slider("Gesamtinvestitionen Stadt", 0, 200, 60)

else:
    invest_total = st.sidebar.slider("Gesamtinvestitionen Stadt", 0, 200, 120)

anteil_v = st.sidebar.slider("Investitionsanteil Villingen (%)", 0, 100, 50)
anteil_s = 100 - anteil_v

invest_v = invest_total * anteil_v / 100
invest_s = invest_total * anteil_s / 100

# -------------------------------------------------
# SALDEN
# -------------------------------------------------

saldo_v = steuer_v - ausgaben_v_total - invest_v
saldo_s = steuer_s - ausgaben_s_total - invest_s

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
# TACHOS
# -------------------------------------------------

col1, col2 = st.columns(2)

with col1:
    st.subheader("Villingen")
    st.plotly_chart(gauge("Saldo Villingen", saldo_v), use_container_width=True)

with col2:
    st.subheader("Schwenningen")
    st.plotly_chart(gauge("Saldo Schwenningen", saldo_s), use_container_width=True)

# -------------------------------------------------
# GESAMTSALDO
# -------------------------------------------------

st.header("Gesamthaushalt")

st.metric(
    "Saldo Gesamtstadt",
    round(saldo_gesamt,2)
)

# -------------------------------------------------
# AUSGABENGRAFIK
# -------------------------------------------------

st.header("Ausgabenstruktur")

ausgaben_df = pd.DataFrame({

    "Bereich":[
        "Schulen",
        "Infrastruktur",
        "Kultur",
        "Gesundheit"
    ],

    "Villingen":[
        schule_v,
        infra_v,
        kultur_v,
        gesund_v
    ],

    "Schwenningen":[
        schule_s,
        infra_s,
        kultur_s,
        gesund_s
    ]
})

st.bar_chart(ausgaben_df.set_index("Bereich"))

# -------------------------------------------------
# INVESTITIONSVERTEILUNG
# -------------------------------------------------

st.header("Investitionsverteilung")

invest_df = pd.DataFrame({

    "Stadtteil":[
        "Villingen",
        "Schwenningen"
    ],

    "Investitionen":[
        invest_v,
        invest_s
    ]
})

st.bar_chart(invest_df.set_index("Stadtteil"))

# -------------------------------------------------
# HAUSHALTSENTWICKLUNG
# -------------------------------------------------

st.header("Haushaltsentwicklung")

jahre = list(range(2025,2035))

entwicklung = []

v = saldo_v
s = saldo_s

for jahr in jahre:

    v = v + saldo_v*0.25
    s = s + saldo_s*0.25

    entwicklung.append({

        "Jahr":jahr,
        "Villingen":v,
        "Schwenningen":s

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

st.plotly_chart(fig,use_container_width=True)

# -------------------------------------------------
# BÜRGERERKLÄRUNG
# -------------------------------------------------

st.header("Bürgererklärung")

with st.expander("Wie funktioniert der Bürgerhaushalt?"):

    st.markdown("""

### Zweck der Simulation

Diese Simulation soll Bürgerinnen und Bürgern verständlich machen,
wie ein kommunaler Haushalt funktioniert.

Die Stadt Villingen-Schwenningen besteht aus zwei Stadtteilen:

**Villingen (V)**  
**Schwenningen (S)**

Beide verfügen über eigene Einnahmen und Ausgaben,
bilden jedoch zusammen den Gesamthaushalt der Stadt.

---

### Einnahmen

Die wichtigste Einnahmequelle der Städte sind Steuern:

• Gewerbesteuer  
• Einkommensteueranteil  
• Grundsteuer  
• weitere kommunale Abgaben

Diese Einnahmen werden genutzt,
um öffentliche Aufgaben zu finanzieren.

---

### Ausgabenbereiche

Der Haushalt wird in verschiedene Aufgabenbereiche aufgeteilt:

**Schulen**

Bau und Sanierung von Schulen, Ausstattung,
Lehrmittel, Betreuung.

**Infrastruktur**

Straßen, Brücken, öffentliche Gebäude,
öffentlicher Verkehr, Digitalisierung.

**Kultur**

Museen, Veranstaltungen, Bibliotheken,
kulturelle Einrichtungen.

**Gesundheitseinrichtungen**

Krankenhäuser, Gesundheitszentren,
Prävention und soziale Infrastruktur.

---

### Investitionen

Investitionen sind langfristige Ausgaben,
die Infrastruktur für viele Jahre schaffen.

Zum Beispiel:

• Neubau einer Schule  
• Sanierung von Straßen  
• Bau von Sportanlagen  
• digitale Infrastruktur

Diese Investitionen können
zwischen Villingen und Schwenningen verteilt werden.

---

### Bedeutung der Tachos

Die beiden Tachos zeigen den Haushaltssaldo der Stadtteile.

Berechnung:

Steuereinnahmen  
minus laufende Ausgaben  
minus Investitionen

Ergebnis:

• **positiv → Überschuss**

• **negativ → Defizit**

---

### Szenarien

**Status Quo**

Die Investitionen bleiben moderat
und orientieren sich an bisherigen Haushaltswerten.

**Investitionsoffensive**

Die Stadt erhöht bewusst die Investitionen,
um Infrastruktur schneller auszubauen.

Dies kann kurzfristig zu höheren Ausgaben führen,
aber langfristig positive wirtschaftliche Effekte haben.

---

### Hinweis

Die Simulation ist eine vereinfachte Darstellung
und ersetzt keinen realen kommunalen Haushalt.
""")