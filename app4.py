# Streamlit Hotel KPI Dashboard
# File: app.py
# Description: Application Streamlit pour suivre les KPI hôteliers (occupancy, ADR, RevPAR, GOPPAR, revenus par département, coûts, etc.).
# Correction intégrée : utilisation de "with pd.ExcelWriter" au lieu de writer.save()

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from datetime import datetime, timedelta

st.set_page_config(page_title="Hotel KPI Dashboard", layout="wide")

# ----------------------
# Utils : génération et chargement des données
# ----------------------
@st.cache_data
def generate_synthetic_hotel_data(start_date='2024-01-01', end_date=None, hotel_name='Hôtel des Îles'):
    if end_date is None:
        end_date = datetime.today().strftime('%Y-%m-%d')
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    dates = pd.date_range(start, end, freq='D')

    room_types = ['Single', 'Double', 'Deluxe', 'Suite']
    channels = ['Direct', 'OTA', 'Corporate', 'Agency']

    rows = []
    np.random.seed(42)
    for d in dates:
        for rt in room_types:
            capacity = {'Single':10, 'Double':30, 'Deluxe':15, 'Suite':5}[rt]
            occupied = np.random.binomial(capacity, p=0.6 + 0.15 * np.sin((d.timetuple().tm_yday/365.0)*2*np.pi))
            adr = round({
                'Single': 60 + 10*np.random.randn(),
                'Double': 90 + 12*np.random.randn(),
                'Deluxe': 140 + 20*np.random.randn(),
                'Suite': 260 + 40*np.random.randn()
            }[rt], 2)
            room_revenue = occupied * adr
            fnb_revenue = round(room_revenue * np.random.uniform(0.05, 0.25), 2)
            spa_revenue = round(room_revenue * np.random.uniform(0.0, 0.08), 2)
            other_revenue = round(np.random.uniform(50, 250), 2)
            total_revenue = room_revenue + fnb_revenue + spa_revenue + other_revenue

            # Costs (approximation)
            rooms_cost = round(room_revenue * np.random.uniform(0.15, 0.30), 2)
            fnb_cost = round(fnb_revenue * np.random.uniform(0.25, 0.45), 2)
            spa_cost = round(spa_revenue * np.random.uniform(0.2, 0.4), 2)
            other_cost = round(other_revenue * np.random.uniform(0.3, 0.6), 2)
            total_cost = rooms_cost + fnb_cost + spa_cost + other_cost

            channel = np.random.choice(channels, p=[0.35, 0.4, 0.15, 0.1])

            rows.append({
                'hotel': hotel_name,
                'date': d,
                'room_type': rt,
                'capacity': capacity,
                'occupied': int(occupied),
                'adr': float(max(20, adr)),
                'room_revenue': round(room_revenue, 2),
                'fnb_revenue': fnb_revenue,
                'spa_revenue': spa_revenue,
                'other_revenue': other_revenue,
                'total_revenue': round(total_revenue, 2),
                'rooms_cost': rooms_cost,
                'fnb_cost': fnb_cost,
                'spa_cost': spa_cost,
                'other_cost': other_cost,
                'total_cost': round(total_cost, 2),
                'channel': channel
            })

    df = pd.DataFrame(rows)
    # Calculs dérivés
    df['occupancy_rate'] = df['occupied'] / df['capacity']
    df['revpar'] = df['room_revenue'] / df['capacity']
    df['gop'] = df['total_revenue'] - df['total_cost']
    df['goppar'] = df['gop'] / df['capacity']
    return df

@st.cache_data
def load_data(uploaded_file):
    if uploaded_file is None:
        return None
    try:
        df = pd.read_csv(uploaded_file, parse_dates=['date'])
        return df
    except Exception as e:
        st.error(f"Erreur lecture fichier: {e}")
        return None

# ----------------------
# Sidebar : paramètres global
# ----------------------
st.sidebar.header("Paramètres")
use_sample = st.sidebar.checkbox('Utiliser jeu de données fictif (hotel_data.csv généré)', value=True)
uploaded = st.sidebar.file_uploader('Ou téléversez votre propre CSV', type=['csv'])

if use_sample and uploaded is None:
    df = generate_synthetic_hotel_data(start_date=(datetime.today()-timedelta(days=365)).strftime('%Y-%m-%d'))
    try:
        df.to_csv('hotel_data.csv', index=False)
    except Exception:
        pass
else:
    df_upload = load_data(uploaded) if uploaded is not None else None
    df = df_upload if df_upload is not None else generate_synthetic_hotel_data(start_date=(datetime.today()-timedelta(days=365)).strftime('%Y-%m-%d'))

# ----------------------
# Top filters in UI
# ----------------------
st.title('📊 Dashboard KPI Hôteliers — Gestion & Contrôle de gestion')
col1, col2, col3 = st.columns([2,1,1])
with col1:
    hotel_list = df['hotel'].unique().tolist()
    hotel = st.selectbox('Hôtel', hotel_list, index=0)
with col2:
    min_date = df['date'].min()
    max_date = df['date'].max()
    date_range = st.date_input('Période', value=(min_date, max_date), min_value=min_date, max_value=max_date)
with col3:
    room_types = ['All'] + sorted(df['room_type'].unique().tolist())
    room_choice = st.selectbox('Type de chambre', room_types, index=0)

channels = ['All'] + sorted(df['channel'].unique().tolist())
channel_choice = st.multiselect('Canal de vente (filtre multiple)', channels, default=['All'])

# Apply filters
start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
mask = (df['date'] >= start_date) & (df['date'] <= end_date) & (df['hotel'] == hotel)
if room_choice != 'All':
    mask &= (df['room_type'] == room_choice)
if channel_choice and ('All' not in channel_choice):
    mask &= df['channel'].isin(channel_choice)

dff = df.loc[mask].copy()
if dff.empty:
    st.warning('Aucune donnée pour les filtres sélectionnés. Ajustez la période ou les filtres.')
    st.stop()

# ----------------------
# KPI calculations
# ----------------------
agg = dff.groupby('date').agg({
    'capacity':'sum',
    'occupied':'sum',
    'room_revenue':'sum',
    'total_revenue':'sum',
    'total_cost':'sum',
    'gop':'sum'
}).reset_index()
agg['occupancy_rate'] = agg['occupied'] / agg['capacity']
agg['adr'] = agg['room_revenue'] / agg['occupied'].replace(0, np.nan)
agg['revpar'] = agg['room_revenue'] / agg['capacity']
agg['goppar'] = agg['gop'] / agg['capacity']

kpi_cols = st.columns(5)
kpi_cols[0].metric('Occupancy rate (avg)', f"{(agg['occupancy_rate'].mean()*100):.1f}%")
kpi_cols[1].metric('ADR (avg)', f"€{agg['adr'].mean():.2f}")
kpi_cols[2].metric('RevPAR (avg)', f"€{agg['revpar'].mean():.2f}")
kpi_cols[3].metric('GOP (sum)', f"€{agg['gop'].sum():,.2f}")
kpi_cols[4].metric('GOPPAR (avg)', f"€{agg['goppar'].mean():.2f}")

# ----------------------
# Time series charts
# ----------------------
st.markdown('### 📈 Évolution des KPI')
fig1 = go.Figure()
fig1.add_trace(go.Scatter(x=agg['date'], y=agg['occupancy_rate'], name='Occupancy Rate', mode='lines+markers'))
fig1.add_trace(go.Scatter(x=agg['date'], y=agg['adr'], name='ADR', yaxis='y2', mode='lines'))
fig1.update_layout(
    xaxis_title='Date',
    yaxis_title='Occupancy rate',
    yaxis=dict(tickformat='.0%'),
    yaxis2=dict(title='ADR (€)', overlaying='y', side='right')
)
st.plotly_chart(fig1, use_container_width=True)

fig2 = px.line(agg, x='date', y='revpar', title='RevPAR — évolution')
st.plotly_chart(fig2, use_container_width=True)

# Revenue breakdown by department
st.markdown('### 🔍 Répartition des revenus')
rev_sum = dff[['room_revenue','fnb_revenue','spa_revenue','other_revenue']].sum().reset_index()
rev_sum.columns = ['department','amount']
rev_sum['department'] = rev_sum['department'].str.replace('_revenue','').str.upper()
fig3 = px.pie(rev_sum, names='department', values='amount', title='Répartition des revenus par département')
st.plotly_chart(fig3, use_container_width=True)

# Revenue & cost over time
st.markdown('### 💰 Revenus vs Coûts')
rc = dff.groupby('date').agg({'total_revenue':'sum','total_cost':'sum'}).reset_index()
fig4 = px.area(rc, x='date', y=['total_revenue','total_cost'], labels={'value':'€','variable':'Ligne'})
st.plotly_chart(fig4, use_container_width=True)

# ----------------------
# Breakdown by room type
# ----------------------
st.markdown('### 🛏️ Performance par type de chambre')
by_room = dff.groupby('room_type').agg({'capacity':'sum','occupied':'sum','room_revenue':'sum','gop':'sum'}).reset_index()
by_room['occupancy'] = by_room['occupied'] / by_room['capacity']
by_room['adr'] = by_room['room_revenue'] / by_room['occupied'].replace(0, np.nan)
by_room['revpar'] = by_room['room_revenue'] / by_room['capacity']
st.dataframe(by_room.style.format({'adr':'{:.2f}','revpar':'{:.2f}','occupancy':'{:.2%}','gop':'{:.2f}'}))

fig5 = px.bar(by_room, x='room_type', y='revpar', title='RevPAR par type de chambre')
st.plotly_chart(fig5, use_container_width=True)

# ----------------------
# Table and download
# ----------------------
st.markdown('### 📋 Données détaillées')
st.dataframe(dff.sort_values('date').reset_index(drop=True))

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='data')
    processed_data = output.getvalue()
    return processed_data

col_dl1, col_dl2 = st.columns(2)
with col_dl1:
    csv = dff.to_csv(index=False).encode('utf-8')
    st.download_button(label='Télécharger CSV', data=csv, file_name='hotel_data_filtered.csv', mime='text/csv')
with col_dl2:
    xlsx_data = to_excel(dff)
    st.download_button(label='Télécharger Excel', data=xlsx_data, file_name='hotel_data_filtered.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

# ----------------------
# Insights & simple actions
# ----------------------
st.markdown('### ✅ Insights rapides & recommandations')
insights = []
if agg['occupancy_rate'].mean() < 0.55:
    insights.append('- Occupancy faible: envisager promotions mid-week ou offres packages.')
if agg['adr'].mean() < 80:
    insights.append('- ADR relativement bas: revoir segmentation tarifaire et canaux OTA.')
if (by_room['revpar'].max() - by_room['revpar'].min()) / (by_room['revpar'].max()+1e-9) > 0.4:
    insights.append('- Grande variance de RevPAR entre types de chambre: optimiser tarif et overbooking par segment.')
if dff['channel'].value_counts(normalize=True).idxmax() == 'OTA':
    insights.append('- Forte dépendance aux OTA: renforcer canal direct (promos, fidélité).')

if not insights:
    st.write('Aucun signal critique détecté sur la période choisie. Continuez la surveillance régulière.')
else:
    for i in insights:
        st.write(i)

# ----------------------
# Simple scenario simulator
# ----------------------
st.markdown("### 🔮 Simulateur rapide — Impact d'une hausse d'ADR ou d'occupation")
sim_col1, sim_col2 = st.columns(2)
with sim_col1:
    adr_delta = st.slider('Augmenter ADR de (%)', min_value=0, max_value=50, value=0)
with sim_col2:
    occ_delta = st.slider('Augmenter Occupancy de (points %)', min_value=0, max_value=30, value=0)

sim_df = dff.copy()
sim_df['sim_adr'] = sim_df['adr'] * (1 + adr_delta/100)
sim_df['sim_occupied'] = (sim_df['occupied'] * (1 + occ_delta/100)).round().astype(int)
sim_df['sim_room_revenue'] = sim_df['sim_adr'] * sim_df['sim_occupied']
sim_total_revenue = sim_df['sim_room_revenue'].sum() + sim_df['fnb_revenue'].sum() + sim_df['spa_revenue'].sum() + sim_df['other_revenue'].sum()
orig_total_revenue = dff['total_revenue'].sum()
st.write(f"Revenu total actuel: €{orig_total_revenue:,.2f}")
st.write(f"Revenu total simulé: €{sim_total_revenue:,.2f}")
st.write(f"Delta: €{(sim_total_revenue - orig_total_revenue):,.2f}")

# ----------------------
# Footer
# ----------------------
st.markdown('---')
st.caption('Application prototype — Data Scientist: modèle de démonstration pour suivi KPI hôteliers. Personnalisez et intégrez vos propres règles de contrôle de gestion pour production.')
