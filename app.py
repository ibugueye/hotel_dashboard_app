import streamlit as st
import pandas as pd

# Charger les données
df = pd.read_csv("hotel_data_extended.csv")

# Titre
st.title("🏨 Tableau de bord global")

# Calcul des KPI
revenu_total = df['revenue'].sum()
cout_total = df['cost'].sum()
marge_globale = df['profit_margin'].mean()
taux_occ = df['occupancy_rate'].mean()

# Fonction helper pour créer une carte colorée
def kpi_card(title, value, bg_color):
    st.markdown(
        f"""
        <div style="background-color:{bg_color}; padding:20px; border-radius:10px; text-align:center; color:white; font-size:18px; font-weight:bold;">
            {title}<br>
            <span style="font-size:24px;">{value}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

# Colonnes pour afficher les KPI côte à côte
col1, col2, col3, col4 = st.columns(4)

with col1:
    kpi_card("💰 Revenu total", f"{revenu_total:,.0f} €", "#2E86C1")  # Bleu
with col2:
    kpi_card("📉 Coût total", f"{cout_total:,.0f} €", "#A93226")  # Rouge foncé
with col3:
    # Vert si marge > 20%, orange sinon
    color = "#27AE60" if marge_globale > 20 else "#E67E22"
    kpi_card("📈 Marge globale", f"{marge_globale:.1f} %", color)
with col4:
    # Vert si taux > 70%, orange si entre 50-70, rouge si < 50
    if taux_occ > 70:
        occ_color = "#27AE60"
    elif taux_occ > 50:
        occ_color = "#E67E22"
    else:
        occ_color = "#C0392B"
    kpi_card("🛎️ Taux d’occupation", f"{taux_occ:.1f} %", occ_color)
