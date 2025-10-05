import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration de la page
st.set_page_config(
    page_title="Analyse Financière Accor",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    .section-header {
        color: #1f77b4;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

class AnalyseFinanciereAccor:
    def __init__(self):
        self.charger_donnees()
        
    def charger_donnees(self):
        """Charge les données financières d'Accor"""
        # Compte de résultat
        self.compte_resultat = pd.DataFrame({
            'Poste': ['Chiffre d\'affaires', 'Charges d\'exploitation courantes', 
                     'Produits et charges non courants', 'Amortissements',
                     'Résultat opérationnel', 'Quote-part sociétés mises en équivalence',
                     'Résultat financier', 'Résultat avant impôts', 'Impôts sur les résultats',
                     'Résultat net de la période', 'Part du Groupe', 'Part intérêts minoritaires'],
            'S1_2024': [2677, -2173, -2, -159, 343, 49, -21, 372, -100, 272, 253, 19],
            'S1_2025': [2745, -2193, 2, -155, 399, -19, -52, 328, -69, 258, 233, 25]
        })
        
        # État de la situation financière
        self.bilan_actif = pd.DataFrame({
            'Poste': ['Ecarts d\'acquisition', 'Immobilisations incorporelles', 
                     'Immobilisations corporelles', 'Droits d\'utilisation',
                     'Titres mis en équivalence', 'Actifs financiers non courants',
                     'Actifs d\'impôts différés', 'Actifs sur contrats non courants',
                     'Stocks', 'Clients', 'Autres actifs courants', 
                     'Actifs sur contrats courants', 'Créances d\'impôt courant',
                     'Autres actifs financiers courants', 'Trésorerie et équivalents',
                     'Actifs destinés à être cédés'],
            'Dec_2024': [2398, 3197, 372, 680, 1367, 373, 268, 431, 39, 803, 504, 38, 30, 158, 1244, 155],
            'Juin_2025': [2332, 3023, 366, 612, 1325, 396, 253, 443, 36, 856, 553, 43, 68, 198, 1135, 192]
        })
        
        self.bilan_passif = pd.DataFrame({
            'Poste': ['Capital', 'Primes et réserves', 'Résultat de l\'exercice',
                     'Titres subordonnés à durée indéterminée', 'Intérêts minoritaires',
                     'Dettes financières non courantes', 'Dettes de loyers non courantes',
                     'Passifs d\'impôts différés', 'Provisions non courantes',
                     'Engagements de retraites', 'Passifs sur contrats non courants',
                     'Dettes financières courantes', 'Dettes de loyers courantes',
                     'Provisions courantes', 'Fournisseurs', 'Autres passifs courants',
                     'Passifs sur contrats courants', 'Passif programmes de fidélité',
                     'Dettes d\'impôt courant', 'Passifs destinés à être cédés'],
            'Dec_2024': [731, 2543, 610, 1148, 437, 2524, 627, 503, 36, 53, 27, 478, 128, 122, 557, 847, 96, 373, 144, 73],
            'Juin_2025': [735, 2390, 233, 991, 421, 3128, 578, 484, 34, 53, 28, 465, 110, 117, 497, 862, 127, 405, 100, 71]
        })
        
        # Flux de trésorerie
        self.flux_tresorerie = pd.DataFrame({
            'Poste': ['Résultat opérationnel', 'Amortissements', 'Dépréciations d\'actifs',
                     'Variation nette des provisions', 'Plus ou moins-values de cession',
                     'Rémunération en actions', 'Autres éléments sans impact trésorerie',
                     'Variation BFR', 'Variation actifs/passifs sur contrats',
                     'Intérêts reçus/(payés)', 'Impôts sur les sociétés payés',
                     'Flux activités opérationnelles', 'Flux d\'investissement',
                     'Flux activités de financement', 'Variation nette trésorerie'],
            'S1_2024': [343, 159, 30, -17, -65, 4, 17, -222, 60, -42, -108, 176, -143, -395, -362],
            'S1_2025': [399, 155, 4, 1, -9, 22, -2, -199, 35, -37, -127, 240, -115, -200, -75]
        })
        
        # Information sectorielle
        self.secteurs_ca = pd.DataFrame({
            'Secteur': ['Premium, Mid. & Eco. - Management & Franchise',
                       'Premium, Mid. & Eco. - Services aux Propriétaires',
                       'Premium, Mid. & Eco. - Actifs Hôteliers & Autres',
                       'Luxury & Lifestyle - Management & Franchise',
                       'Luxury & Lifestyle - Services aux Propriétaires',
                       'Luxury & Lifestyle - Actifs Hôteliers & Autres',
                       'Holding & Intercos'],
            'S1_2024': [431, 538, 505, 242, 716, 285, -39],
            'S1_2025': [427, 557, 491, 244, 718, 351, -43]
        })
        
        # Données pour les ratios
        self.calculer_ratios()
    
    def calculer_ratios(self):
        """Calcule les ratios financiers clés"""
        # Ratios de rentabilité
        ca_2024 = self.compte_resultat.loc[0, 'S1_2024']
        ca_2025 = self.compte_resultat.loc[0, 'S1_2025']
        resultat_net_2024 = self.compte_resultat.loc[9, 'S1_2024']
        resultat_net_2025 = self.compte_resultat.loc[9, 'S1_2025']
        resultat_op_2024 = self.compte_resultat.loc[4, 'S1_2024']
        resultat_op_2025 = self.compte_resultat.loc[4, 'S1_2025']
        
        self.ratios_rentabilite = pd.DataFrame({
            'Ratio': ['Marge nette (%)', 'Marge opérationnelle (%)', 'ROE (%)', 'ROA (%)'],
            'S1_2024': [
                (resultat_net_2024/ca_2024)*100,
                (resultat_op_2024/ca_2024)*100,
                (resultat_net_2024/5032)*100,  # Capitaux propres Groupe 2024
                (resultat_net_2024/12057)*100  # Total actif 2024
            ],
            'S1_2025': [
                (resultat_net_2025/ca_2025)*100,
                (resultat_op_2025/ca_2025)*100,
                (resultat_net_2025/4350)*100,  # Capitaux propres Groupe 2025
                (resultat_net_2025/11829)*100  # Total actif 2025
            ]
        })
        
        # Ratios de liquidité
        actifs_courants_2024 = 2970
        actifs_courants_2025 = 3080
        passifs_courants_2024 = 2819
        passifs_courants_2025 = 2753
        tresorerie_2024 = 1244
        tresorerie_2025 = 1135
        
        self.ratios_liquidite = pd.DataFrame({
            'Ratio': ['Current Ratio', 'Quick Ratio', 'Trésorerie/Passifs courants (%)'],
            'Dec_2024': [
                actifs_courants_2024/passifs_courants_2024,
                (actifs_courants_2024 - 39)/passifs_courants_2024,  # Exclure stocks
                (tresorerie_2024/passifs_courants_2024)*100
            ],
            'Juin_2025': [
                actifs_courants_2025/passifs_courants_2025,
                (actifs_courants_2025 - 36)/passifs_courants_2025,
                (tresorerie_2025/passifs_courants_2025)*100
            ]
        })
        
        # Ratios d'endettement
        dette_financiere_2024 = 3002
        dette_financiere_2025 = 3593
        capitaux_propres_2024 = 5469
        capitaux_propres_2025 = 4771
        
        self.ratios_endettement = pd.DataFrame({
            'Ratio': ['Dette Nette/Capitaux Propres', 'Dette Nette/EBITDA', 'Couverture des intérêts'],
            'Dec_2024': [
                (dette_financiere_2024 - 1244)/capitaux_propres_2024,
                (dette_financiere_2024 - 1244)/resultat_op_2024,
                resultat_op_2024/47  # Charges financières
            ],
            'Juin_2025': [
                (dette_financiere_2025 - 1135)/capitaux_propres_2025,
                (dette_financiere_2025 - 1135)/resultat_op_2025,
                resultat_op_2025/53  # Charges financières
            ]
        })

def main():
    st.markdown('<h1 class="main-header">🏨 Analyse Financière Accor - S1 2025</h1>', unsafe_allow_html=True)
    
    # Initialisation de l'analyse
    analyse = AnalyseFinanciereAccor()
    
    # Sidebar pour la navigation
    st.sidebar.title("Navigation")
    section = st.sidebar.radio(
        "Sélectionnez une section:",
        ["Vue d'ensemble", "Compte de résultat", "Bilan", "Flux de trésorerie", 
         "Analyse sectorielle", "Ratios financiers", "Contrôle de gestion"]
    )
    
    if section == "Vue d'ensemble":
        afficher_vue_ensemble(analyse)
    elif section == "Compte de résultat":
        afficher_compte_resultat(analyse)
    elif section == "Bilan":
        afficher_bilan(analyse)
    elif section == "Flux de trésorerie":
        afficher_flux_tresorerie(analyse)
    elif section == "Analyse sectorielle":
        afficher_analyse_sectorielle(analyse)
    elif section == "Ratios financiers":
        afficher_ratios_financiers(analyse)
    elif section == "Contrôle de gestion":
        afficher_controle_gestion(analyse)

def afficher_vue_ensemble(analyse):
    st.markdown('<h2 class="section-header">📊 Vue d\'ensemble des performances</h2>', unsafe_allow_html=True)
    
    # Métriques clés
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        ca_evolution = ((analyse.compte_resultat.loc[0, 'S1_2025'] - analyse.compte_resultat.loc[0, 'S1_2024']) / 
                       analyse.compte_resultat.loc[0, 'S1_2024'] * 100)
        st.metric(
            label="Chiffre d'affaires",
            value=f"{analyse.compte_resultat.loc[0, 'S1_2025']} M€",
            delta=f"{ca_evolution:.1f}%"
        )
    
    with col2:
        resultat_net_evolution = ((analyse.compte_resultat.loc[9, 'S1_2025'] - analyse.compte_resultat.loc[9, 'S1_2024']) / 
                                 analyse.compte_resultat.loc[9, 'S1_2024'] * 100)
        st.metric(
            label="Résultat net",
            value=f"{analyse.compte_resultat.loc[9, 'S1_2025']} M€",
            delta=f"{resultat_net_evolution:.1f}%"
        )
    
    with col3:
        st.metric(
            label="Marge opérationnelle",
            value=f"{analyse.ratios_rentabilite.loc[1, 'S1_2025']:.1f}%",
            delta=f"{analyse.ratios_rentabilite.loc[1, 'S1_2025'] - analyse.ratios_rentabilite.loc[1, 'S1_2024']:.1f}%"
        )
    
    with col4:
        st.metric(
            label="Trésorerie",
            value=f"{analyse.bilan_actif.loc[14, 'Juin_2025']} M€",
            delta=f"{analyse.bilan_actif.loc[14, 'Juin_2025'] - analyse.bilan_actif.loc[14, 'Dec_2024']} M€"
        )
    
    # Graphiques principaux
    col1, col2 = st.columns(2)
    
    with col1:
        # Évolution du compte de résultat
        fig = go.Figure()
        postes_principaux = ['Chiffre d\'affaires', 'Résultat opérationnel', 'Résultat net de la période']
        for poste in postes_principaux:
            ligne = analyse.compte_resultat[analyse.compte_resultat['Poste'] == poste]
            fig.add_trace(go.Bar(
                name=poste,
                x=['S1 2024', 'S1 2025'],
                y=[ligne['S1_2024'].values[0], ligne['S1_2025'].values[0]]
            ))
        
        fig.update_layout(
            title="Évolution des principaux postes du compte de résultat",
            barmode='group',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Structure du bilan
        actif_total_2025 = analyse.bilan_actif['Juin_2025'].sum()
        passif_total_2025 = analyse.bilan_passif['Juin_2025'].sum()
        
        categories_actif = ['Actifs non courants', 'Actifs courants']
        valeurs_actif = [
            analyse.bilan_actif['Juin_2025'].iloc[:8].sum(),
            analyse.bilan_actif['Juin_2025'].iloc[8:].sum()
        ]
        
        categories_passif = ['Capitaux propres', 'Dettes non courantes', 'Dettes courantes']
        valeurs_passif = [
            analyse.bilan_passif['Juin_2025'].iloc[:5].sum(),
            analyse.bilan_passif['Juin_2025'].iloc[5:11].sum(),
            analyse.bilan_passif['Juin_2025'].iloc[11:].sum()
        ]
        
        fig = make_subplots(1, 2, specs=[[{'type':'domain'}, {'type':'domain'}]],
                           subplot_titles=['Structure de l\'actif', 'Structure du passif'])
        
        fig.add_trace(go.Pie(labels=categories_actif, values=valeurs_actif, name="Actif"), 1, 1)
        fig.add_trace(go.Pie(labels=categories_passif, values=valeurs_passif, name="Passif"), 1, 2)
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

def afficher_compte_resultat(analyse):
    st.markdown('<h2 class="section-header">📈 Compte de résultat</h2>', unsafe_allow_html=True)
    
    # Tableau du compte de résultat
    st.dataframe(analyse.compte_resultat.style.format({
        'S1_2024': '{:.0f}',
        'S1_2025': '{:.0f}'
    }), use_container_width=True)
    
    # Graphiques d'analyse
    col1, col2 = st.columns(2)
    
    with col1:
        # Analyse de la marge
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='S1 2024',
            x=['Marge brute', 'Marge opérationnelle', 'Marge nette'],
            y=[analyse.ratios_rentabilite.loc[1, 'S1_2024'], 
               analyse.ratios_rentabilite.loc[1, 'S1_2024'],
               analyse.ratios_rentabilite.loc[0, 'S1_2024']]
        ))
        fig.add_trace(go.Bar(
            name='S1 2025',
            x=['Marge brute', 'Marge opérationnelle', 'Marge nette'],
            y=[analyse.ratios_rentabilite.loc[1, 'S1_2025'],
               analyse.ratios_rentabilite.loc[1, 'S1_2025'],
               analyse.ratios_rentabilite.loc[0, 'S1_2025']]
        ))
        fig.update_layout(title="Évolution des marges (%)", barmode='group')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Analyse des charges
        charges = analyse.compte_resultat.iloc[1:4]
        fig = px.bar(charges, x='Poste', y=['S1_2024', 'S1_2025'],
                    title="Évolution des principales charges")
        st.plotly_chart(fig, use_container_width=True)

def afficher_bilan(analyse):
    st.markdown('<h2 class="section-header">🏦 État de la situation financière</h2>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Actif", "Passif"])
    
    with tab1:
        st.subheader("Actif")
        st.dataframe(analyse.bilan_actif.style.format({
            'Dec_2024': '{:.0f}',
            'Juin_2025': '{:.0f}'
        }), use_container_width=True)
        
        # Graphique de l'évolution de l'actif
        fig = px.bar(analyse.bilan_actif, x='Poste', y=['Dec_2024', 'Juin_2025'],
                    title="Évolution de la structure de l'actif")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Passif")
        st.dataframe(analyse.bilan_passif.style.format({
            'Dec_2024': '{:.0f}',
            'Juin_2025': '{:.0f}'
        }), use_container_width=True)
        
        # Graphique de l'évolution du passif
        fig = px.bar(analyse.bilan_passif, x='Poste', y=['Dec_2024', 'Juin_2025'],
                    title="Évolution de la structure du passif")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

def afficher_flux_tresorerie(analyse):
    st.markdown('<h2 class="section-header">💸 Tableau des flux de trésorerie</h2>', unsafe_allow_html=True)
    
    st.dataframe(analyse.flux_tresorerie.style.format({
        'S1_2024': '{:.0f}',
        'S1_2025': '{:.0f}'
    }), use_container_width=True)
    
    # Analyse des flux
    col1, col2 = st.columns(2)
    
    with col1:
        flux_categories = ['Opérationnel', 'Investissement', 'Financement']
        flux_2024 = [176, -143, -395]
        flux_2025 = [240, -115, -200]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='S1 2024', x=flux_categories, y=flux_2024))
        fig.add_trace(go.Bar(name='S1 2025', x=flux_categories, y=flux_2025))
        fig.update_layout(title="Flux de trésorerie par activité")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Variation de la trésorerie
        dates = ['Début S1', 'Fin S1']
        tresorerie_2024 = [1279, 903]
        tresorerie_2025 = [1236, 1130]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(name='2024', x=dates, y=tresorerie_2024, mode='lines+markers'))
        fig.add_trace(go.Scatter(name='2025', x=dates, y=tresorerie_2025, mode='lines+markers'))
        fig.update_layout(title="Évolution de la trésorerie")
        st.plotly_chart(fig, use_container_width=True)

def afficher_analyse_sectorielle(analyse):
    st.markdown('<h2 class="section-header">🏢 Analyse sectorielle</h2>', unsafe_allow_html=True)
    
    # Chiffre d'affaires par secteur
    fig = px.bar(analyse.secteurs_ca, x='Secteur', y=['S1_2024', 'S1_2025'],
                title="Chiffre d'affaires par secteur d'activité")
    fig.update_layout(xaxis_tickangle=-45, height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # Analyse de la performance par division
    st.subheader("Performance par division")
    
    divisions_data = pd.DataFrame({
        'Division': ['Premium, Mid & Eco', 'Luxury & Lifestyle'],
        'CA_S1_2024': [1473, 1243],
        'CA_S1_2025': [1475, 1312],
        'EBE_S1_2024': [360, 196],
        'EBE_S1_2025': [385, 224]
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(divisions_data, x='Division', y=['CA_S1_2024', 'CA_S1_2025'],
                    title="Chiffre d'affaires par division")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(divisions_data, x='Division', y=['EBE_S1_2024', 'EBE_S1_2025'],
                    title="Excédent Brut d'Exploitation par division")
        st.plotly_chart(fig, use_container_width=True)

def afficher_ratios_financiers(analyse):
    st.markdown('<h2 class="section-header">📐 Ratios financiers</h2>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Rentabilité", "Liquidité", "Endettement"])
    
    with tab1:
        st.subheader("Ratios de rentabilité")
        st.dataframe(analyse.ratios_rentabilite.style.format({
            'S1_2024': '{:.2f}%',
            'S1_2025': '{:.2f}%'
        }), use_container_width=True)
        
        fig = px.line(analyse.ratios_rentabilite, x='Ratio', y=['S1_2024', 'S1_2025'],
                     title="Évolution des ratios de rentabilité")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Ratios de liquidité")
        st.dataframe(analyse.ratios_liquidite.style.format({
            'Dec_2024': '{:.2f}',
            'Juin_2025': '{:.2f}'
        }), use_container_width=True)
        
        fig = px.bar(analyse.ratios_liquidite, x='Ratio', y=['Dec_2024', 'Juin_2025'],
                    title="Évolution des ratios de liquidité")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Ratios d'endettement")
        st.dataframe(analyse.ratios_endettement.style.format({
            'Dec_2024': '{:.2f}',
            'Juin_2025': '{:.2f}'
        }), use_container_width=True)
        
        fig = px.bar(analyse.ratios_endettement, x='Ratio', y=['Dec_2024', 'Juin_2025'],
                    title="Évolution des ratios d'endettement")
        st.plotly_chart(fig, use_container_width=True)

def afficher_controle_gestion(analyse):
    st.markdown('<h2 class="section-header">🎯 Contrôle de gestion</h2>', unsafe_allow_html=True)
    
    # Analyse des écarts
    st.subheader("Analyse des écarts")
    
    ecarts_data = pd.DataFrame({
        'Poste': ['Chiffre d\'affaires', 'Résultat opérationnel', 'Résultat net'],
        'S1_2024': [2677, 343, 272],
        'S1_2025': [2745, 399, 258],
        'Écart': [68, 56, -14],
        'Écart %': [2.5, 16.3, -5.1]
    })
    
    st.dataframe(ecarts_data.style.format({
        'S1_2024': '{:.0f}',
        'S1_2025': '{:.0f}',
        'Écart': '{:.0f}',
        'Écart %': '{:.1f}%'
    }), use_container_width=True)
    
    # Indicateurs de performance
    st.subheader("Indicateurs clés de performance")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="RevPAR croissance",
            value="+4.6%",
            delta="vs S1 2024"
        )
    
    with col2:
        st.metric(
            label="Taux d'occupation",
            value="65%",
            delta="Stable"
        )
    
    with col3:
        st.metric(
            label="Dette financière nette",
            value="3 096 M€",
            delta="+601 M€"
        )
    
    # Alertes de contrôle
    st.subheader("🚨 Alertes de contrôle de gestion")
    
    alertes = []
    
    # Vérification de la trésorerie
    if analyse.bilan_actif.loc[14, 'Juin_2025'] < 1000:
        alertes.append("⚠️ Trésorerie inférieure à 1 milliard d'euros")
    
    # Vérification de l'endettement
    if analyse.ratios_endettement.loc[0, 'Juin_2025'] > 0.5:
        alertes.append("⚠️ Ratio d'endettement élevé")
    
    # Vérification de la rentabilité
    if analyse.ratios_rentabilite.loc[0, 'S1_2025'] < 5:
        alertes.append("⚠️ Marge nette inférieure à 5%")
    
    for alerte in alertes:
        st.warning(alerte)
    
    if not alertes:
        st.success("✅ Aucune alerte majeure détectée")

if __name__ == "__main__":
    main()