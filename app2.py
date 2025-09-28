import streamlit as st
import pandas as pd
import plotly.express as px

# Titre de l'application
st.title("Application Complète de Gestion Hôtelière")

# Chargement des données
@st.cache
def load_data():
    data = pd.read_csv("hotel_data.csv")
    return data

data = load_data()

# Sidebar pour les filtres
st.sidebar.header("Filtres")
selected_department = st.sidebar.selectbox("Département", ["Réception", "Restauration", "Housekeeping", "Maintenance", "Spa", "Boutique"])
selected_period = st.sidebar.selectbox("Période", ["Jour", "Semaine", "Mois", "Année"])

# Filtrage des données
filtered_data = data[data["Department"] == selected_department]

# KPI Globaux
st.header("KPI Globaux")
col1, col2, col3 = st.columns(3)
col1.metric("Taux d'occupation", "85%", "2%")
col2.metric("RevPAR", "$120", "-$5")
col3.metric("Revenu total", "$1,200,000", "$50,000")

# Analyse des Centres de Coûts
st.header("Analyse des Centres de Coûts")
cost_fig = px.bar(data, x="Department", y="Cost", title="Coûts par Département")
st.plotly_chart(cost_fig)

# Analyse des KPI Financiers
st.header("Analyse des KPI Financiers")
revenue_fig = px.line(data, x="Date", y="Revenue", title="Revenus Mensuels")
st.plotly_chart(revenue_fig)

# Analyse des Points de Vente
st.header("Analyse des Points de Vente")
sales_data = data[data["Type"] == "Point de Vente"]
sales_fig = px.bar(sales_data, x="Point de Vente", y="Revenus", title="Revenus par Point de Vente")
st.plotly_chart(sales_fig)

# Analyse des Ressources Humaines
st.header("Analyse des Ressources Humaines")
hr_data = data[data["Type"] == "Ressources Humaines"]
hr_fig = px.bar(hr_data, x="Department", y="Cost", title="Coûts de Main-d'œuvre par Département")
st.plotly_chart(hr_fig)

# Analyse Prédictive
st.header("Prévisions de Taux d'Occupation")
# Ici, vous pouvez intégrer un modèle de prédiction (par exemple, avec Prophet ou Scikit-learn)
# Exemple simple avec une régression linéaire
from sklearn.linear_model import LinearRegression
import numpy as np

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
