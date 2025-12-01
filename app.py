"""
FitLife Nutrition AI - Application Utilisateur Finale (Version Corrigée)
Assistant Nutritionnel IA 
Auteurs: Asma Bélkahla & Monia Selleoui
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os

# Ajouter le dossier modules au path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

# Import des modules locaux
from modules.nutrition_calculator import NutritionalCalculator, UserProfile
from modules.food_recommender import FoodRecommendationEngine, NutritionalTarget
from modules.meal_plan_generator import MealPlanGenerator, MealPlanPreferences
from modules.nutrition_assistant import NutritionAssistant

# Configuration de la page
st.set_page_config(
    page_title="FitLife - Assistant Nutritionnel IA",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF6B35;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        transition: transform 0.3s;
        min-height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.3);
    }
    .metric-card h2 {
        font-size: 3rem;
        margin: 0.5rem 0;
    }
    .metric-card h3 {
        margin: 0.5rem 0;
        font-size: 1.3rem;
    }
    .metric-card p {
        font-size: 0.95rem;
        opacity: 0.9;
    }
    .food-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #f0f2f6;
        margin: 0.5rem 0;
        transition: all 0.3s;
    }
    .food-card:hover {
        border-color: #FF6B35;
        box-shadow: 0 4px 8px rgba(255,107,53,0.2);
    }
    .recommendation-badge {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .stButton>button {
        background: linear-gradient(135deg, #FF6B35 0%, #E55A2B 100%);
        color: white;
        border-radius: 25px;
        padding: 0.6rem 2rem;
        font-weight: bold;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(255,107,53,0.3);
    }
    .info-box {
        background: #f8f9fa;
        border-left: 4px solid #FF6B35;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .chat-user {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        margin-left: 10%;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .chat-assistant {
        background: linear-gradient(135deg, #F5F5F5 0%, #E0E0E0 100%);
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        margin-right: 10%;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialisation de la session
if 'profile' not in st.session_state:
    st.session_state.profile = None
if 'nutritional_needs' not in st.session_state:
    st.session_state.nutritional_needs = None
if 'weight_history' not in st.session_state:
    st.session_state.weight_history = []
if 'meal_plan' not in st.session_state:
    st.session_state.meal_plan = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'favorite_foods' not in st.session_state:
    st.session_state.favorite_foods = []
if 'recommender' not in st.session_state:
    st.session_state.recommender = None
if 'assistant' not in st.session_state:
    st.session_state.assistant = None
if 'meal_generator' not in st.session_state:
    st.session_state.meal_generator = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "🏠 Accueil"

# Chargement des données
@st.cache_data
def load_food_data():
    """Charge le dataset alimentaire"""
    try:
        dfs = []
        data_path = "data/nutrition"
        
        if os.path.exists(data_path):
            for i in range(1, 6):
                file_path = os.path.join(data_path, f"FOOD-DATA-GROUP{i}.csv")
                if os.path.exists(file_path):
                    df = pd.read_csv(file_path)
                    dfs.append(df)
        
        if dfs:
            combined_df = pd.concat(dfs, ignore_index=True)
            combined_df = combined_df.dropna(subset=['food'])
            combined_df = combined_df.fillna(0)
            return combined_df
    except Exception as e:
        st.error(f"⚠️ Erreur lors du chargement des données: {str(e)}")
    
    # Dataset de fallback
    return pd.DataFrame({
        'food': [
            'Poulet grillé', 'Riz complet', 'Brocoli', 'Saumon', 'Œufs',
            'Quinoa', 'Avocat', 'Amandes', 'Yaourt grec', 'Banane',
            'Épinards', 'Patate douce', 'Tofu', 'Lentilles', 'Pomme',
            'Thon', 'Flocons avoine', 'Fromage blanc', 'Pain complet', 'Tomate',
            'Pâtes complètes', 'Blanc de dinde', 'Concombre', 'Haricots verts', 'Kiwi'
        ],
        'Caloric Value': [165, 370, 34, 208, 155, 368, 160, 579, 59, 89, 23, 86, 76, 116, 52, 144, 389, 73, 247, 18, 348, 135, 15, 31, 61],
        'Protein': [31, 7.9, 2.8, 20, 13, 14, 2, 21, 10, 1.1, 2.9, 1.6, 8, 9, 0.3, 30, 13.2, 12.5, 13, 0.9, 12, 30, 0.7, 1.8, 1.1],
        'Carbohydrates': [0, 77, 6.6, 0, 1.1, 64, 9, 22, 3.6, 23, 3.6, 20, 1.9, 20, 14, 0, 66, 4, 49, 3.9, 75, 0, 3.6, 7, 15],
        'Fat': [3.6, 2.9, 0.4, 13, 11, 6, 15, 49, 0.4, 0.3, 0.4, 0.1, 5, 0.4, 0.2, 5, 7, 0.2, 3.3, 0.2, 1.5, 1, 0.1, 0.2, 0.5],
        'Dietary Fiber': [0, 3.5, 2.6, 0, 0, 7, 7, 12, 0, 2.6, 2.2, 3, 0.3, 7.9, 2.4, 0, 10.6, 0, 7, 1.2, 3.2, 0, 0.5, 2.7, 3],
        'Saturated Fats': [1, 0.6, 0.1, 3, 3.5, 0.7, 2.1, 3.8, 0.1, 0.1, 0.1, 0, 0.7, 0.1, 0, 1.3, 1.2, 0.1, 0.7, 0, 0.3, 0.3, 0, 0, 0.1],
        'Sugars': [0, 0.8, 1.7, 0, 0.6, 0, 0.7, 4.4, 3.6, 12, 0.4, 4.2, 0.6, 1.8, 10, 0, 0.8, 4, 5, 2.6, 2.7, 0, 1.7, 3.3, 9],
        'Sodium': [74, 7, 33, 59, 124, 7, 7, 1, 36, 1, 79, 55, 7, 2, 1, 354, 2, 50, 550, 5, 6, 60, 2, 1, 3],
        'Water': [65, 12, 89, 69, 76, 13, 73, 5, 81, 75, 92, 77, 85, 70, 86, 70, 8, 82, 35, 95, 11, 68, 96, 90, 83],
        'Vitamin A': [21, 0, 623, 40, 520, 0, 146, 1, 243, 64, 9376, 961, 85, 8, 54, 50, 0, 28, 0, 833, 0, 0, 105, 380, 87],
        'Vitamin B12': [0.3, 0, 0, 3.2, 0.9, 0, 0, 0, 1.3, 0, 0, 0, 0, 0.1, 0, 4.3, 0, 0.2, 0, 0, 0, 0.4, 0, 0, 0],
        'Vitamin C': [0, 0, 89, 0, 0, 0, 10, 0, 0, 8.7, 28, 2.4, 0.1, 1.5, 4.6, 0, 0, 0, 0, 14, 0, 0, 2.8, 12, 93],
        'Vitamin D': [0, 0, 0, 11, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'Calcium': [15, 23, 47, 12, 50, 47, 12, 264, 110, 5, 99, 30, 350, 19, 6, 10, 54, 103, 175, 10, 21, 11, 16, 37, 34],
        'Iron': [1.0, 1.5, 0.7, 0.8, 1.2, 4.6, 0.6, 3.7, 0.1, 0.3, 2.7, 0.6, 5.4, 3.3, 0.1, 1.3, 4.7, 0.1, 3.6, 0.3, 1.5, 0.7, 0.3, 1.0, 0.3],
        'Magnesium': [29, 143, 21, 29, 10, 197, 29, 268, 11, 27, 79, 25, 53, 36, 5, 29, 177, 11, 90, 11, 53, 30, 13, 25, 17],
        'Potassium': [256, 268, 316, 363, 126, 563, 485, 705, 141, 358, 558, 337, 121, 369, 107, 252, 429, 220, 240, 237, 169, 302, 147, 209, 312],
        'Nutrition Density': [8.5, 7.2, 9.1, 8.8, 7.9, 8.3, 7.5, 7.8, 8.0, 6.5, 9.5, 7.8, 7.6, 8.4, 7.1, 8.6, 7.9, 8.2, 6.8, 8.9, 7.0, 8.7, 9.2, 8.8, 8.1]
    })

# Charger les données
food_data = load_food_data()

# Initialiser les modules
@st.cache_resource
def initialize_ai_modules(_food_data):
    """Initialise tous les modules"""
    try:
        recommender = FoodRecommendationEngine(_food_data)
        meal_generator = MealPlanGenerator(_food_data, recommender)
        assistant = NutritionAssistant(_food_data, recommender)
        return recommender, meal_generator, assistant
    except Exception as e:
        st.error(f"❌ Erreur d'initialisation: {str(e)}")
        return None, None, None

# Initialiser
if st.session_state.recommender is None:
    recommender, meal_generator, assistant = initialize_ai_modules(food_data)
    st.session_state.recommender = recommender
    st.session_state.meal_generator = meal_generator
    st.session_state.assistant = assistant
else:
    recommender = st.session_state.recommender
    meal_generator = st.session_state.meal_generator
    assistant = st.session_state.assistant

# Fonction pour changer de page
def change_page(page_name):
    st.session_state.current_page = page_name
    st.rerun()

# Sidebar - Navigation
st.sidebar.markdown("# 🥗 FitLife AI")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["🏠 Accueil", "👤 Profil", "📊 Dashboard", 
     "🎯 Recommandations", "🍽️ Plan Alimentaire",
     "💬 Assistant", "📈 Suivi", "📚 Base Aliments"],
    index=["🏠 Accueil", "👤 Profil", "📊 Dashboard", 
           "🎯 Recommandations", "🍽️ Plan Alimentaire",
           "💬 Assistant", "📈 Suivi", "📚 Base Aliments"].index(st.session_state.current_page)
)

st.session_state.current_page = page

st.sidebar.markdown("---")

if st.session_state.profile:
    st.sidebar.success("✅ Profil configuré")
    st.sidebar.info(f"**Objectif:** {st.session_state.profile['goal']}")
    if st.session_state.nutritional_needs:
        st.sidebar.metric("Calories/jour", 
                         f"{st.session_state.nutritional_needs['target_calories']:.0f}")
else:
    st.sidebar.warning("⚠️ Configurez votre profil")

# ==================== PAGES ====================

# PAGE: ACCUEIL
if page == "🏠 Accueil":
    st.markdown('<h1 class="main-header">🥗 Bienvenue sur FitLife</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666; margin-bottom: 2rem;">Votre assistant nutritionnel intelligent pour atteindre vos objectifs</p>', unsafe_allow_html=True)
    
    # Fonctionnalités principales AVEC BOUTONS FONCTIONNELS
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h2>📊</h2>
            <h3>Analyse Personnalisée</h3>
            <p>Calculez vos besoins nutritionnels adaptés à votre profil</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📊 Voir Dashboard", key="card_dash", use_container_width=True):
            change_page("📊 Dashboard")
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h2>🎯</h2>
            <h3>Recommandations</h3>
            <p>Découvrez les aliments parfaits pour votre objectif</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🎯 Découvrir", key="card_reco", use_container_width=True):
            change_page("🎯 Recommandations")
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h2>📈</h2>
            <h3>Suivi Progrès</h3>
            <p>Suivez votre évolution et restez motivé(e)</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📈 Suivre", key="card_suivi", use_container_width=True):
            change_page("📈 Suivi")
    
    st.markdown("---")
    
    # Guide d'utilisation
    st.markdown("### 📖 Comment utiliser FitLife")
    
    st.markdown("""
    <div class="info-box">
        <h4>🚀 Premiers Pas</h4>
        <ol style="margin: 0.5rem 0;">
            <li><strong>Configurez votre profil</strong> - Renseignez vos informations (poids, taille, âge, objectif)</li>
            <li><strong>Consultez votre dashboard</strong> - Visualisez vos besoins nutritionnels</li>
            <li><strong>Découvrez les recommandations</strong> - Aliments adaptés à vos besoins</li>
            <li><strong>Générez votre plan alimentaire</strong> - Créez un menu personnalisé</li>
            <li><strong>Posez vos questions</strong> - L'assistant vous répond</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Objectifs disponibles
    st.markdown("### 🎯 Objectifs Disponibles")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        #### 🔥 Perte de poids
        - Déficit calorique calculé
        - Aliments faibles en calories
        - Riches en protéines et fibres
        """)
    
    with col2:
        st.markdown("""
        #### 🎯 Maintien
        - Équilibre nutritionnel
        - Maintien du poids actuel
        - Alimentation variée
        """)
    
    with col3:
        st.markdown("""
        #### 💪 Prise de masse
        - Surplus calorique optimal
        - Aliments riches en protéines
        - Développement musculaire
        """)
    
    st.markdown("---")
    
    # Call to action
    if not st.session_state.profile:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Créer mon profil maintenant", use_container_width=True, type="primary"):
                change_page("👤 Profil")
    else:
        st.success(f"""
        ✅ **Profil configuré avec succès!**
        
        Votre objectif: **{st.session_state.profile['goal']}**  
        Calories quotidiennes: **{st.session_state.nutritional_needs['target_calories']:.0f} kcal**
        
        👉 Explorez maintenant les autres fonctionnalités!
        """)

# PAGE: PROFIL
elif page == "👤 Profil":
    st.markdown('<h1 class="main-header">👤 Configuration du Profil</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        📝 <strong>Renseignez vos informations personnelles</strong> pour obtenir des recommandations adaptées.
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("profile_form"):
        st.markdown("### 📏 Informations Physiques")
        col1, col2 = st.columns(2)
        
        with col1:
            weight = st.number_input("Poids actuel (kg)", 30.0, 200.0, 70.0, 0.1)
            height = st.number_input("Taille (cm)", 120, 220, 170, 1)
            age = st.number_input("Âge", 15, 100, 25, 1)
        
        with col2:
            sex = st.selectbox("Sexe", ["Homme", "Femme"])
            target_weight = st.number_input("Poids cible (kg)", 30.0, 200.0, 65.0, 0.1)
            goal = st.selectbox("Objectif", ["Perte de poids", "Maintien", "Prise de masse"])
        
        st.markdown("### 🏃 Activité Physique")
        activity_level = st.select_slider(
            "Niveau d'activité quotidienne",
            options=['Sédentaire', 'Légèrement actif', 'Modérément actif', 'Très actif', 'Extrêmement actif'],
            value='Modérément actif'
        )
        
        st.markdown("---")
        submitted = st.form_submit_button("💾 Enregistrer mon profil", use_container_width=True, type="primary")
        
        if submitted:
            # Créer profil utilisateur
            profile_data = UserProfile(
                weight=weight,
                height=height,
                age=age,
                sex=sex,
                activity_level=activity_level,
                goal=goal,
                target_weight=target_weight
            )
            
            # Calculer besoins nutritionnels
            needs = NutritionalCalculator.calculate_complete_needs(profile_data)
            
            # Sauvegarder
            st.session_state.profile = {
                'weight': weight,
                'height': height,
                'age': age,
                'sex': sex,
                'target_weight': target_weight,
                'goal': goal,
                'activity_level': activity_level,
                'created_at': datetime.now()
            }
            
            st.session_state.nutritional_needs = needs
            
            # Mettre à jour le contexte de l'assistant
            if assistant:
                assistant.set_context(st.session_state.profile, needs)
            
            st.success("✅ Profil enregistré avec succès!")
            st.balloons()
            
            # Afficher les résultats
            st.markdown("---")
            st.markdown("### 📊 Vos Besoins Nutritionnels")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🔥 Métabolisme de base", f"{needs['bmr']:.0f} kcal")
            with col2:
                st.metric("⚡ Dépense quotidienne", f"{needs['tdee']:.0f} kcal")
            with col3:
                st.metric("🎯 Calories recommandées", f"{needs['target_calories']:.0f} kcal")
            with col4:
                if needs['duration_weeks'] > 0:
                    st.metric("⏱️ Durée estimée", f"{needs['duration_weeks']:.0f} sem")
            
            st.markdown("### 🥗 Répartition Quotidienne")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🥩 Protéines", f"{needs['macros']['proteins']:.0f}g")
            with col2:
                st.metric("🌾 Glucides", f"{needs['macros']['carbs']:.0f}g")
            with col3:
                st.metric("🥑 Lipides", f"{needs['macros']['fats']:.0f}g")

# PAGE: DASHBOARD
elif page == "📊 Dashboard":
    st.markdown('<h1 class="main-header">📊 Tableau de Bord</h1>', unsafe_allow_html=True)
    
    if not st.session_state.profile:
        st.warning("⚠️ Veuillez d'abord configurer votre profil")
        if st.button("Aller au profil"):
            change_page("👤 Profil")
    else:
        profile = st.session_state.profile
        needs = st.session_state.nutritional_needs
        
        # Métriques principales
        st.markdown("### 📊 Vos Objectifs Nutritionnels Quotidiens")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🔥 Calories", f"{needs['target_calories']:.0f} kcal")
        with col2:
            st.metric("🥩 Protéines", f"{needs['macros']['proteins']:.0f}g")
        with col3:
            st.metric("🌾 Glucides", f"{needs['macros']['carbs']:.0f}g")
        with col4:
            st.metric("🥑 Lipides", f"{needs['macros']['fats']:.0f}g")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Répartition des Macronutriments")
            fig = go.Figure(data=[go.Pie(
                labels=['Protéines', 'Glucides', 'Lipides'],
                values=[
                    needs['macros']['proteins_cal'],
                    needs['macros']['carbs_cal'],
                    needs['macros']['fats_cal']
                ],
                hole=0.4,
                marker_colors=['#FF6B6B', '#4ECDC4', '#FFE66D']
            )])
            fig.update_layout(height=400, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 🎯 Progression vers l'Objectif")
            current = profile['weight']
            target = profile['target_weight']
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=current,
                title={'text': "Poids Actuel (kg)"},
                delta={'reference': target},
                gauge={
                    'axis': {'range': [None, max(current, target) + 10]},
                    'bar': {'color': "#FF6B35"},
                    'threshold': {
                        'line': {'color': "green", 'width': 4},
                        'value': target
                    }
                }
            ))
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

# PAGE: RECOMMANDATIONS
elif page == "🎯 Recommandations":
    st.markdown('<h1 class="main-header">🎯 Recommandations Personnalisées</h1>', unsafe_allow_html=True)
    
    if not st.session_state.profile:
        st.warning("⚠️ Configurez votre profil pour des recommandations personnalisées")
        if st.button("Aller au profil"):
            change_page("👤 Profil")
    else:
        profile = st.session_state.profile
        needs = st.session_state.nutritional_needs
        
        st.markdown("### 🔍 Recherche d'Aliments")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            search = st.text_input("🔎 Rechercher un aliment", placeholder="Nom d'aliment...")
        with col2:
            n_results = st.number_input("Résultats", 5, 20, 10)
        
        if st.button("🎯 Obtenir recommandations", use_container_width=True, type="primary"):
            with st.spinner("🔍 Recherche en cours..."):
                meal_ratio = 0.30
                
                target = NutritionalTarget(
                    calories=needs['target_calories'] * meal_ratio,
                    proteins=needs['macros']['proteins'] * meal_ratio,
                    carbs=needs['macros']['carbs'] * meal_ratio,
                    fats=needs['macros']['fats'] * meal_ratio,
                    goal=profile['goal']
                )
                
                recommendations = recommender.recommend_foods(target, n_recommendations=n_results)
                
                if search:
                    recommendations = recommendations[
                        recommendations['food'].str.contains(search, case=False, na=False)
                    ]
                
                st.success(f"✅ {len(recommendations)} aliments recommandés")
                
                for idx, (_, food) in enumerate(recommendations.iterrows()):
                    with st.expander(f"#{idx+1} - {food['food']} ({food['match_percentage']:.0f}%)", expanded=(idx < 3)):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown("**📊 Valeurs /100g:**")
                            st.text(f"🔥 {food['Caloric Value']:.0f} kcal")
                            st.text(f"🥩 {food['Protein']:.1f}g protéines")
                            st.text(f"🌾 {food['Carbohydrates']:.1f}g glucides")
                            st.text(f"🥑 {food['Fat']:.1f}g lipides")
                        
                        with col2:
                            if food['Caloric Value'] > 0:
                                portion = min(200, target.calories * 0.4 / food['Caloric Value'] * 100)
                            else:
                                portion = 100
                            st.markdown(f"**Portion suggérée: {portion:.0f}g**")
                            st.text(f"🔥 {food['Caloric Value'] * portion / 100:.0f} kcal")
                        
                        with col3:
                            if st.button("⭐ Favoris", key=f"fav_{idx}"):
                                if food['food'] not in st.session_state.favorite_foods:
                                    st.session_state.favorite_foods.append(food['food'])
                                    st.success("✅ Ajouté!")

# PAGE: PLAN ALIMENTAIRE
elif page == "🍽️ Plan Alimentaire":
    st.markdown('<h1 class="main-header">🍽️ Plan Alimentaire Personnalisé</h1>', unsafe_allow_html=True)
    
    if not st.session_state.profile:
        st.warning("⚠️ Configurez votre profil d'abord")
        if st.button("Aller au profil"):
            change_page("👤 Profil")
    else:
        with st.form("meal_plan_form"):
            st.markdown("### ⚙️ Personnalisez votre plan")
            
            col1, col2 = st.columns(2)
            
            with col1:
                meals_per_day = st.slider("Repas par jour", 3, 6, 4)
                variety_days = st.slider("Variété (jours)", 1, 7, 7)
            
            with col2:
                budget = st.selectbox("Budget", ["Économique", "Moyen", "Élevé"])
                prep_time = st.selectbox("Temps", ["Rapide (<30min)", "Moyen", "Élaboré"])
            
            generate = st.form_submit_button("🎨 Générer", use_container_width=True, type="primary")
            
            if generate and meal_generator:
                with st.spinner("🳳 Création en cours..."):
                    preferences = MealPlanPreferences(
                        meals_per_day=meals_per_day,
                        variety_days=variety_days,
                        budget=budget,
                        prep_time=prep_time
                    )
                    
                    week_plan = meal_generator.generate_week_plan(
                        st.session_state.nutritional_needs,
                        preferences
                    )
                    
                    formatted_plan = meal_generator.format_plan_for_display(week_plan)
                    st.session_state.meal_plan = formatted_plan
                    
                    stats = meal_generator.calculate_plan_stats(week_plan)
                    
                    st.success("✅ Plan prêt!")
                    st.balloons()
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Calories moy", f"{stats['avg_daily_calories']:.0f}")
                    with col2:
                        st.metric("Protéines moy", f"{stats['avg_daily_proteins']:.0f}g")
                    with col3:
                        st.metric("Aliments uniques", stats['unique_foods_count'])
                    with col4:
                        st.metric("Variété", f"{stats['variety_score']:.0f}%")
        
        if st.session_state.meal_plan:
            st.markdown("---")
            st.markdown("### 📅 Votre Plan")
            
            days = list(st.session_state.meal_plan.keys())
            selected_day = st.selectbox("📆 Jour", days)
            
            if selected_day in st.session_state.meal_plan:
                day_meals = st.session_state.meal_plan[selected_day]
                
                total_cal = sum([meal.get('calories', 0) for meal in day_meals.values()])
                
                st.metric("Total jour", f"{total_cal:.0f} kcal")
                
                for meal_name, meal_data in day_meals.items():
                    with st.expander(f"🍽️ {meal_name}", expanded=True):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown("**Aliments:**")
                            for aliment in meal_data.get('aliments', []):
                                st.markdown(f"• {aliment}")
                        
                        with col2:
                            st.markdown("**Nutrition:**")
                            st.markdown(f"🔥 {meal_data.get('calories', 0):.0f} kcal")
                            st.markdown(f"🥩 {meal_data.get('proteines', 0):.0f}g")

# PAGE: ASSISTANT (CORRIGÉ - Réponses diversifiées)
elif page == "💬 Assistant":
    st.markdown('<h1 class="main-header">💬 Assistant Nutritionnel</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        💡 Posez vos questions sur la nutrition et recevez des conseils personnalisés
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.profile:
        st.warning("⚠️ Configurez votre profil pour des réponses personnalisées")
        if st.button("Configurer mon profil"):
            change_page("👤 Profil")
    else:
        # Questions rapides
        st.markdown("### 💡 Questions Fréquentes")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🳳 Petit-déjeuner", use_container_width=True):
                question = "Suggère-moi un petit-déjeuner protéiné"
                st.session_state.chat_history.append({"role": "user", "content": question})
                if assistant:
                    response = assistant.answer_query(question)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()
        
        with col2:
            if st.button("🏋️ Post-entraînement", use_container_width=True):
                question = "Que manger après l'entraînement?"
                st.session_state.chat_history.append({"role": "user", "content": question})
                if assistant:
                    response = assistant.answer_query(question)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()
        
        with col3:
            if st.button("💧 Hydratation", use_container_width=True):
                question = "Combien d'eau dois-je boire?"
                st.session_state.chat_history.append({"role": "user", "content": question})
                if assistant:
                    response = assistant.answer_query(question)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()
        
        st.markdown("---")
        
        # Historique du chat
        for msg in st.session_state.chat_history[-10:]:
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="chat-user">
                    <strong>👤 Vous:</strong> {msg["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-assistant">
                    <strong>🤖 Assistant:</strong><br>{msg["content"]}
                </div>
                """, unsafe_allow_html=True)
        
        # Zone de saisie
        st.markdown("---")
        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_input("💬 Votre question...", 
                                       key="chat_input", 
                                       placeholder="Ex: Analyse le saumon pour mon objectif")
        with col2:
            send = st.button("📤", use_container_width=True)
        
        if send and user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            with st.spinner("🤖 Réflexion..."):
                if assistant:
                    response = assistant.answer_query(user_input)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
            
            st.rerun()
        
        # Effacer historique
        if st.session_state.chat_history:
            st.markdown("---")
            if st.button("🗑️ Effacer l'historique"):
                st.session_state.chat_history = []
                st.rerun()

# PAGE: SUIVI
elif page == "📈 Suivi":
    st.markdown('<h1 class="main-header">📈 Suivi de Progression</h1>', unsafe_allow_html=True)
    
    if not st.session_state.profile:
        st.warning("⚠️ Configurez votre profil")
        if st.button("Aller au profil"):
            change_page("👤 Profil")
    else:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📝 Nouvel Enregistrement")
            with st.form("weight_form"):
                weight_date = st.date_input("Date", datetime.now())
                weight_val = st.number_input("Poids (kg)", 30.0, 200.0, 
                                             st.session_state.profile['weight'], 0.1)
                notes = st.text_area("Notes", placeholder="Comment vous sentez-vous?")
                
                if st.form_submit_button("💾 Enregistrer", use_container_width=True):
                    st.session_state.weight_history.append({
                        'date': weight_date,
                        'weight': weight_val,
                        'notes': notes
                    })
                    st.success(f"✅ Poids enregistré: {weight_val} kg")
                    st.balloons()
        
        with col2:
            if st.session_state.weight_history:
                st.markdown("### 📊 Statistiques")
                latest = st.session_state.weight_history[-1]['weight']
                initial = st.session_state.profile['weight']
                target = st.session_state.profile['target_weight']
                
                st.metric("Dernier poids", f"{latest:.1f} kg", 
                         f"{latest - initial:+.1f} kg")
                
                progress = abs(initial - latest)
                total = abs(initial - target)
                pct = (progress / total * 100) if total > 0 else 0
                
                st.progress(min(pct / 100, 1.0))
                st.caption(f"{pct:.1f}% atteint")
        
        # Graphique
        if st.session_state.weight_history:
            st.markdown("---")
            st.markdown("### 📈 Courbe d'Évolution")
            
            dates = [e['date'] for e in st.session_state.weight_history]
            weights = [e['weight'] for e in st.session_state.weight_history]
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=dates, y=weights,
                mode='lines+markers',
                name='Poids',
                line=dict(color='#FF6B35', width=3)
            ))
            
            target = st.session_state.profile['target_weight']
            fig.add_trace(go.Scatter(
                x=[dates[0], dates[-1]],
                y=[target, target],
                mode='lines',
                name='Objectif',
                line=dict(color='green', dash='dash')
            ))
            
            fig.update_layout(
                title="Évolution du Poids",
                xaxis_title="Date",
                yaxis_title="Poids (kg)",
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)

# PAGE: BASE ALIMENTS
elif page == "📚 Base Aliments":
    st.markdown('<h1 class="main-header">📚 Base de Données</h1>', unsafe_allow_html=True)
    
    st.markdown(f"### 🔍 {len(food_data)} aliments disponibles")
    
    # Filtres
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search = st.text_input("🔎 Rechercher", placeholder="Nom d'aliment...")
    with col2:
        min_protein = st.slider("Protéines min (g)", 0, 50, 0)
    with col3:
        max_calories = st.slider("Calories max", 0, 1000, 1000)
    
    # Filtrage
    filtered = food_data.copy()
    
    if search:
        filtered = filtered[filtered['food'].str.contains(search, case=False, na=False)]
    
    filtered = filtered[
        (filtered['Protein'] >= min_protein) &
        (filtered['Caloric Value'] <= max_calories)
    ]
    
    st.markdown(f"### 📊 {len(filtered)} résultats")
    
    # Affichage paginé
    items_per_page = 10
    total_pages = max(1, (len(filtered) - 1) // items_per_page + 1)
    
    if total_pages > 0:
        page_num = st.number_input("Page", 1, total_pages, 1)
        
        start_idx = (page_num - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, len(filtered))
        
        page_data = filtered.iloc[start_idx:end_idx]
        
        for idx, (_, row) in enumerate(page_data.iterrows()):
            with st.expander(f"🍽️ {row['food']} - {row['Caloric Value']:.0f} kcal", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 📊 Macronutriments")
                    st.markdown(f"""
                    - 🔥 Calories: {row['Caloric Value']:.0f} kcal
                    - 🥩 Protéines: {row['Protein']:.1f}g
                    - 🌾 Glucides: {row['Carbohydrates']:.1f}g
                    - 🥑 Lipides: {row['Fat']:.1f}g
                    - 🌿 Fibres: {row['Dietary Fiber']:.1f}g
                    """)
                
                with col2:
                    st.markdown("#### 💊 Vitamines & Minéraux")
                    st.markdown(f"""
                    - 🅰️ Vitamine A: {row['Vitamin A']:.1f}µg
                    - 🅱️ Vitamine B12: {row['Vitamin B12']:.2f}µg
                    - 🍊 Vitamine C: {row['Vitamin C']:.1f}mg
                    - 🦴 Calcium: {row['Calcium']:.0f}mg
                    """)

# Footer simplifié
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1.5rem;'>
    <p><strong>🥗 FitLife - Assistant Nutritionnel IA</strong></p>
    <p>Développé par Asma Bélkahla & Monia Selleoui</p>
    <p style='font-size: 0.9rem; margin-top: 1rem;'>
        🤖 IA 100% Locale | 📊 Scikit-learn | 🎨 Streamlit | 📈 Plotly
    </p>
</div>
""", unsafe_allow_html=True)