import streamlit as st
import pandas as pd

df = pd.read_csv("hotel_data_extended.csv")

st.title("🏨 Tableau de bord global")

st.metric("Revenu total", f"{df['revenue'].sum():,.0f} €")
st.metric("Coût total", f"{df['cost'].sum():,.0f} €")
st.metric("Marge globale", f"{df['profit_margin'].mean():.1f} %")
st.metric("Taux d’occupation moyen", f"{df['occupancy_rate'].mean():.1f} %")