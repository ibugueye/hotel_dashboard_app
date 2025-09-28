import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.linear_model import LinearRegression
import numpy as np
from io import BytesIO
from reportlab.pdfgen import canvas

# Titre de l'application
st.title("Application de Gestion Hôtelière avec Indicateurs de Performance")

# Chargement des données depuis un fichier CSV
@st.cache_data
def load_data():
    file_path = 'hotel_data.csv'  # Remplacez par le chemin de votre fichier CSV
    data = pd.read_csv(file_path)
    
    # Vérifier si la colonne 'Date' existe
    if 'Date' in data.columns:
        data['Date'] = pd.to_datetime(data['Date'])  # Convertir en datetime si la colonne existe
    else:
        st.warning("La colonne 'Date' est manquante dans le fichier CSV.")
    
    return data

data = load_data()

# Sidebar pour les filtres
st.sidebar.header("Filtres")
selected_department = st.sidebar.selectbox("Département", data['Department'].unique())
selected_period = st.sidebar.selectbox("Période", ["Jour", "Semaine", "Mois", "Année"])

# Filtrage des données
filtered_data = data[data["Department"] == selected_department]

# Calcul des KPI
total_rooms = data['RoomCount'].sum()  # Exemple : total de chambres, à ajuster selon votre CSV
occupied_rooms = data['OccupiedRooms'].sum()  # Exemple : chambres occupées
revenue = data['Revenue'].sum()  # Total des revenus
cost = data['Cost'].sum()  # Total des coûts
occupancy_rate = (occupied_rooms / total_rooms) * 100 if total_rooms > 0 else 0
adr = revenue / occupied_rooms if occupied_rooms > 0 else 0
revpar = revenue / total_rooms if total_rooms > 0 else 0
trevpar = revenue / total_rooms if total_rooms > 0 else 0 
copar = cost / total_rooms if total_rooms > 0 else 0 

# Affichage des KPI
st.header("Indicateurs de Performance Clés")
col1, col2, col3 = st.columns(3)
col1.metric("Taux d'occupation", f"{occupancy_rate:.2f}%")
col2.metric("RevPAR", f"${revpar:.2f}")
col3.metric("ADR", f"${adr:.2f}")

st.subheader("Revenu total par chambre disponible (TRevPAR)")
st.write(f"${trevpar:.2f}")

st.subheader("Coût par chambre disponible (CoPAR)")
st.write(f"${copar:.2f}")

# Analyse des KPI Financiers
st.header("Analyse des KPI Financiers")
if 'Date' in data.columns:
    revenue_fig = px.line(data, x="Date", y="Revenue", title="Revenus Mensuels")
    st.plotly_chart(revenue_fig)
    st.write("Tableau des Revenus Mensuels")
    st.dataframe(data[["Date", "Revenue"]].groupby("Date").sum().reset_index())
else:
    st.warning("Impossible d'afficher les revenus mensuels sans colonne 'Date'.")

# Analyse des Points de Vente
st.header("Analyse des Points de Vente")
sales_data = data[data["Type"] == "Point de Vente"]
sales_fig = px.bar(sales_data, x="Point de Vente", y="Revenues", title="Revenus par Point de Vente")
st.plotly_chart(sales_fig)
st.write("Tableau des Revenus par Point de Vente")
st.dataframe(sales_data[["Point de Vente", "Revenues"]].groupby("Point de Vente").sum().reset_index())

# Analyse des Ressources Humaines
st.header("Analyse des Ressources Humaines")
hr_data = data[data["Type"] == "Ressources Humaines"]
hr_fig = px.bar(hr_data, x="Department", y="Cost", title="Coûts de Main-d'œuvre par Département")
st.plotly_chart(hr_fig)
st.write("Tableau des Coûts de Main-d'œuvre par Département")
st.dataframe(hr_data[["Department", "Cost"]].groupby("Department").sum().reset_index())

# Analyse Prédictive Budgétaire
st.header("Analyse Prédictive Budgétaire")
if 'Date' in data.columns:
    # Préparation des données pour la prédiction
    X = np.array(data['Date'].astype('datetime64[ns]').astype(int)).reshape(-1, 1)
    y = data['OccupancyRate']

    # Entraînement du modèle
    model = LinearRegression()
    model.fit(X, y)

    # Prédiction
    future_dates = pd.date_range(start=data['Date'].max(), periods=30, freq='D')
    future_X = np.array(future_dates.astype('datetime64[ns]').astype(int)).reshape(-1, 1)
    predictions = model.predict(future_X)

    # Affichage des prédictions
    prediction_fig = px.line(x=future_dates, y=predictions, title="Prévisions de Taux d'Occupation")
    st.plotly_chart(prediction_fig)
    st.write("Tableau des Prévisions de Taux d'Occupation")
    st.dataframe(pd.DataFrame({"Date": future_dates, "Taux d'Occupation Prévu": predictions}))
else:
    st.warning("Impossible de faire des prévisions sans colonne 'Date'.")

# Exportation des Rapports
st.header("Exportation des Rapports")
if st.button("Exporter le Rapport en PDF"):
    pdf = BytesIO()
    # Utilisation de ReportLab pour générer un PDF
    c = canvas.Canvas(pdf)
    c.drawString(100, 750, "Rapport de Gestion Hôtelière")
    c.save()
    pdf.seek(0)
    st.download_button("Télécharger le PDF", pdf, file_name="rapport_hotel.pdf")

if st.button("Exporter le Rapport en Excel"):
    excel = BytesIO()
    with pd.ExcelWriter(excel, engine='xlsxwriter') as writer:
        data.to_excel(writer, sheet_name='Données')
    excel.seek(0)
    st.download_button("Télécharger l'Excel", excel, file_name="rapport_hotel.xlsx")

# Alertes et Notifications
st.header("Alertes et Notifications")
if st.button("Vérifier les Alertes"):
    if occupancy_rate < 70:
        st.warning("⚠️ Taux d'occupation trop bas !")
    if cost > 1000000:  # Valeur exemple, à ajuster
        st.error("🚨 Coûts dépassent le budget !")

# Personnalisation des Tableaux de Bord
st.header("Personnalisation des Tableaux de Bord")
selected_kpis = st.multiselect("Sélectionnez les KPI à afficher", ["Taux d'occupation", "RevPAR", "ADR", "CoPAR"])
if "Taux d'occupation" in selected_kpis:
    st.metric("Taux d'occupation", f"{occupancy_rate:.2f}%")
if "RevPAR" in selected_kpis:
    st.metric("RevPAR", f"${revpar:.2f}")
if "ADR" in selected_kpis:
    st.metric("ADR", f"${adr:.2f}")
if "CoPAR" in selected_kpis:
    st.metric("CoPAR", f"${copar:.2f}")
