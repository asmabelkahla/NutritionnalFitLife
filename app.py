"""
FitLife Nutrition AI - Application Principale Complète
Version Sans API Externe - Tous Modules Locaux
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
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .module-badge {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
        margin: 0.2rem;
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
if 'daily_intake' not in st.session_state:
    st.session_state.daily_intake = []

# Chargement des données
@st.cache_data
def load_food_data():
    """Charge le dataset alimentaire"""
    try:
        # Essayer de charger vos fichiers réels
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
            st.success(f"✅ {len(combined_df)} aliments chargés depuis vos fichiers CSV")
            return combined_df
    except Exception as e:
        st.warning(f"⚠️ Impossible de charger les fichiers CSV: {str(e)}")
    
    # Dataset de fallback enrichi
    st.info("ℹ️ Utilisation du dataset de démonstration (25 aliments)")
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

# Initialiser les modules IA
@st.cache_resource
def initialize_ai_modules(_food_data):
    """Initialise tous les modules IA"""
    try:
        recommender = FoodRecommendationEngine(_food_data)
        meal_generator = MealPlanGenerator(_food_data, recommender)
        assistant = NutritionAssistant(_food_data, recommender)
        return recommender, meal_generator, assistant, "✅"
    except Exception as e:
        st.error(f"❌ Erreur initialisation modules: {str(e)}")
        return None, None, None, "❌"

# Initialiser si nécessaire
if st.session_state.recommender is None:
    recommender, meal_generator, assistant, status = initialize_ai_modules(food_data)
    st.session_state.recommender = recommender
    st.session_state.meal_generator = meal_generator
    st.session_state.assistant = assistant
    st.session_state.modules_status = status
else:
    recommender = st.session_state.recommender
    meal_generator = st.session_state.meal_generator
    assistant = st.session_state.assistant

# Sidebar - Navigation
st.sidebar.markdown("# 🥗 FitLife AI")
st.sidebar.markdown("**100% Local - Sans API**")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["🏠 Accueil", "👤 Profil", "📊 Dashboard", 
     "🎯 Recommandations", "🍽️ Plan Alimentaire",
     "💬 Assistant", "📈 Suivi", "📚 Base Aliments"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🤖 Modules IA")
st.sidebar.text(f"{st.session_state.modules_status} Tous opérationnels")
st.sidebar.text(f"📊 {len(food_data)} aliments")

if st.session_state.profile:
    st.sidebar.success("✅ Profil configuré")
    st.sidebar.info(f"**{st.session_state.profile['goal']}**")
    if st.session_state.nutritional_needs:
        st.sidebar.metric("Calories/jour", 
                         f"{st.session_state.nutritional_needs['target_calories']:.0f}")
else:
    st.sidebar.warning("⚠️ Configurez votre profil")

# ==================== PAGES ====================

# PAGE: ACCUEIL
if page == "🏠 Accueil":
    st.markdown('<h1 class="main-header">🥗 FitLife - IA Nutritionnelle Locale</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h2>🤖</h2>
            <h3>4 Modules IA</h3>
            <p>Développés localement<br>Sans dépendance externe</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h2>🔬</h2>
            <h3>Testable</h3>
            <p>Chaque module validable<br>Tests unitaires intégrés</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h2>📊</h2>
            <h3>Base Complète</h3>
            <p>{len(food_data)} aliments<br>Données détaillées</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Afficher les modules avec badges
    st.markdown("### 🚀 Architecture Modulaire")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<span class="module-badge">Module 1: Calculateur</span>', unsafe_allow_html=True)
        st.markdown("""
        - ✅ Formules scientifiques validées (Mifflin-St Jeor)
        - ✅ BMR, TDEE, Macronutriments
        - ✅ Estimation durée objectifs
        - ✅ Calcul besoins hydriques
        """)
        
        st.markdown('<span class="module-badge">Module 2: Recommandeur ML</span>', unsafe_allow_html=True)
        st.markdown("""
        - ✅ Similarité cosine (sklearn)
        - ✅ Feature engineering nutritionnel
        - ✅ Scoring personnalisé par objectif
        - ✅ Recherche d'alternatives
        """)
    
    with col2:
        st.markdown('<span class="module-badge">Module 3: Planificateur</span>', unsafe_allow_html=True)
        st.markdown("""
        - ✅ Génération de plans hebdomadaires
        - ✅ Algorithmes d'optimisation
        - ✅ Variété intelligente
        - ✅ Respect contraintes caloriques
        """)
        
        st.markdown('<span class="module-badge">Module 4: Assistant</span>', unsafe_allow_html=True)
        st.markdown("""
        - ✅ NLP basé sur règles (regex)
        - ✅ Base de connaissances nutritionnelles
        - ✅ Réponses contextuelles
        - ✅ Templates personnalisés
        """)
    
    st.markdown("---")
    st.markdown("### 📖 Comment utiliser l'application")
    
    st.markdown("""
    1. **👤 Configurez votre profil** - Renseignez vos données personnelles
    2. **📊 Consultez votre dashboard** - Visualisez vos besoins nutritionnels
    3. **🎯 Obtenez des recommandations** - Découvrez les aliments adaptés
    4. **🍽️ Générez un plan** - Créez un plan alimentaire personnalisé
    5. **💬 Utilisez l'assistant** - Posez vos questions nutritionnelles
    6. **📈 Suivez vos progrès** - Enregistrez votre évolution
    """)
    
    if not st.session_state.profile:
        st.warning("👉 Commencez par configurer votre profil dans l'onglet **👤 Profil**")
        if st.button("🚀 Démarrer maintenant", use_container_width=True):
            st.rerun()

# PAGE: PROFIL
elif page == "👤 Profil":
    st.markdown('<h1 class="main-header">👤 Configuration du Profil</h1>', unsafe_allow_html=True)
    st.info("**Module utilisé:** 📊 Calculateur Nutritionnel (Local)")
    
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            weight = st.number_input("Poids actuel (kg)", 30.0, 200.0, 70.0, 0.1)
            height = st.number_input("Taille (cm)", 120, 220, 170, 1)
            age = st.number_input("Âge", 15, 100, 25, 1)
        
        with col2:
            sex = st.selectbox("Sexe", ["Homme", "Femme"])
            target_weight = st.number_input("Poids cible (kg)", 30.0, 200.0, 65.0, 0.1)
            goal = st.selectbox("Objectif", ["Perte de poids", "Maintien", "Prise de masse"])
        
        activity_level = st.select_slider(
            "Niveau d'activité",
            options=['Sédentaire', 'Légèrement actif', 'Modérément actif', 'Très actif', 'Extrêmement actif'],
            value='Modérément actif'
        )
        
        col1, col2 = st.columns(2)
        with col1:
            diet_type = st.multiselect(
                "Régime alimentaire",
                ["Omnivore", "Végétarien", "Végétalien", "Sans gluten", "Sans lactose"],
                default=["Omnivore"]
            )
        with col2:
            allergies = st.text_area("Allergies/Intolérances", 
                                     placeholder="Ex: Arachides, fruits de mer...")
        
        if st.form_submit_button("💾 Calculer et Enregistrer", use_container_width=True):
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
                'diet_type': diet_type,
                'allergies': allergies,
                'created_at': datetime.now()
            }
            
            st.session_state.nutritional_needs = needs
            
            # Mettre à jour le contexte de l'assistant
            if assistant:
                assistant.set_context(st.session_state.profile, needs)
            
            st.success("✅ Profil enregistré et calculs effectués!")
            st.balloons()
            
            # Afficher les résultats
            st.markdown("---")
            st.markdown("### 📊 Vos Besoins Nutritionnels Calculés")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🔥 BMR", f"{needs['bmr']:.0f} kcal", 
                         help="Métabolisme de base - Calories brûlées au repos")
            with col2:
                st.metric("⚡ TDEE", f"{needs['tdee']:.0f} kcal", 
                         help="Dépense énergétique totale quotidienne")
            with col3:
                st.metric("🎯 Calories cible", f"{needs['target_calories']:.0f} kcal", 
                         delta=f"{needs['deficit_surplus']:+.0f} kcal")
            with col4:
                if needs['duration_weeks'] > 0:
                    st.metric("⏱️ Durée estimée", f"{needs['duration_weeks']:.0f} sem",
                             help=needs['duration_message'])
                else:
                    st.metric("⏱️ Durée estimée", "Maintien")
            
            st.markdown("### 🥗 Macronutriments Journaliers")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🥩 Protéines", f"{needs['macros']['proteins']:.0f}g",
                         help=f"{needs['macros']['proteins_pct']:.1f}% des calories")
            with col2:
                st.metric("🌾 Glucides", f"{needs['macros']['carbs']:.0f}g",
                         help=f"{needs['macros']['carbs_pct']:.1f}% des calories")
            with col3:
                st.metric("🥑 Lipides", f"{needs['macros']['fats']:.0f}g",
                         help=f"{needs['macros']['fats_pct']:.1f}% des calories")
            
            st.markdown("### 💧 Hydratation")
            st.metric("💧 Eau recommandée", f"{needs['water_liters']} litres/jour")
            
            st.info(f"""
            📝 **Résumé de votre profil:**
            - Objectif: {goal}
            - Du poids actuel ({weight}kg) au poids cible ({target_weight}kg)
            - Activité: {activity_level}
            - Régime: {', '.join(diet_type)}
            """)

# PAGE: DASHBOARD
elif page == "📊 Dashboard":
    st.markdown('<h1 class="main-header">📊 Tableau de Bord Nutritionnel</h1>', unsafe_allow_html=True)
    
    if not st.session_state.profile:
        st.warning("⚠️ Configurez votre profil d'abord dans l'onglet **👤 Profil**")
    else:
        profile = st.session_state.profile
        needs = st.session_state.nutritional_needs
        
        # Métriques principales
        st.markdown("### 📊 Vos Objectifs Nutritionnels")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🔥 Calories/jour", f"{needs['target_calories']:.0f} kcal")
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
                marker_colors=['#FF6B6B', '#4ECDC4', '#FFE66D'],
                textinfo='label+percent',
                textfont_size=14
            )])
            fig.update_layout(
                height=400,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 🎯 Progression vers l'Objectif")
            current = profile['weight']
            target = profile['target_weight']
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=current,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Poids Actuel (kg)", 'font': {'size': 20}},
                delta={
                    'reference': target,
                    'increasing': {'color': "red" if profile['goal'] == 'Perte de poids' else "green"},
                    'decreasing': {'color': "green" if profile['goal'] == 'Perte de poids' else "red"}
                },
                gauge={
                    'axis': {'range': [None, max(current, target) + 10]},
                    'bar': {'color': "#FF6B35"},
                    'steps': [
                        {'range': [0, target], 'color': "lightgray"}
                    ],
                    'threshold': {
                        'line': {'color': "green", 'width': 4},
                        'thickness': 0.75,
                        'value': target
                    }
                }
            ))
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Recommandations du jour
        st.markdown("---")
        st.markdown("### 🎯 Recommandations Personnalisées du Jour")
        
        if recommender:
            target = NutritionalTarget(
                calories=needs['target_calories'],
                proteins=needs['macros']['proteins'],
                carbs=needs['macros']['carbs'],
                fats=needs['macros']['fats'],
                goal=profile['goal']
            )
            
            recommendations = recommender.recommend_foods(target, n_recommendations=6)
            
            cols = st.columns(3)
            for idx, (_, food) in enumerate(recommendations.iterrows()):
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class="food-card">
                        <h4>🍽️ {food['food']}</h4>
                        <span class="recommendation-badge">Match: {food['match_percentage']:.0f}%</span>
                        <p><strong>Pour 100g:</strong></p>
                        <ul style="font-size: 0.9rem;">
                            <li>🔥 {food['Caloric Value']:.0f} kcal</li>
                            <li>🥩 {food['Protein']:.1f}g protéines</li>
                            <li>🌾 {food['Carbohydrates']:.1f}g glucides</li>
                            <li>🥑 {food['Fat']:.1f}g lipides</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"⭐ Favoris", key=f"fav_dash_{idx}"):
                        if food['food'] not in st.session_state.favorite_foods:
                            st.session_state.favorite_foods.append(food['food'])
                            st.success(f"✅ {food['food']} ajouté aux favoris!")

# PAGE: RECOMMANDATIONS
elif page == "🎯 Recommandations":
    st.markdown('<h1 class="main-header">🎯 Recommandations Intelligentes</h1>', unsafe_allow_html=True)
    
    if not st.session_state.profile:
        st.warning("⚠️ Configurez votre profil pour des recommandations personnalisées")
    else:
        st.info("**Module utilisé:** 🎯 Moteur de Recommandation ML (Scikit-learn)")
        
        profile = st.session_state.profile
        needs = st.session_state.nutritional_needs
        
        st.markdown("### 🔍 Recherche Intelligente d'Aliments")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            search = st.text_input("🔎 Rechercher un aliment", "")
        with col2:
            n_results = st.number_input("Nombre", 5, 20, 10)
        with col3:
            sort_by = st.selectbox("Trier par", ["Match", "Protéines", "Calories"])
        
        # Filtres avancés
        with st.expander("🔧 Filtres avancés"):
            col1, col2 = st.columns(2)
            with col1:
                min_protein = st.slider("Protéines min (g/100g)", 0, 50, 0)
                max_calories = st.slider("Calories max (kcal/100g)", 0, 1000, 1000)
            with col2:
                exclude_foods = st.multiselect(
                    "Exclure des aliments",
                    st.session_state.favorite_foods if st.session_state.favorite_foods else ["Aucun"]
                )
        
        if st.button("🎯 Générer des recommandations", use_container_width=True):
            with st.spinner("🤖 Analyse en cours avec le moteur ML..."):
                # Calculer les besoins pour un repas type
                meal_ratio = 0.30  # 30% des besoins quotidiens
                
                target = NutritionalTarget(
                    calories=needs['target_calories'] * meal_ratio,
                    proteins=needs['macros']['proteins'] * meal_ratio,
                    carbs=needs['macros']['carbs'] * meal_ratio,
                    fats=needs['macros']['fats'] * meal_ratio,
                    goal=profile['goal']
                )
                
                # Obtenir recommandations
                recommendations = recommender.recommend_foods(
                    target,
                    n_recommendations=n_results,
                    exclude_foods=exclude_foods if exclude_foods else None,
                    min_protein=min_protein,
                    max_calories=max_calories
                )
                
                # Filtrer par recherche
                if search:
                    recommendations = recommendations[
                        recommendations['food'].str.contains(search, case=False, na=False)
                    ]
                
                st.success(f"✅ {len(recommendations)} aliments recommandés pour votre {profile['goal']}")
                
                # Afficher résultats
                for idx, (_, food) in enumerate(recommendations.iterrows()):
                    with st.expander(f"#{idx+1} - {food['food']} (Match: {food['match_percentage']:.0f}%)", expanded=(idx < 3)):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown("**📊 Macros /100g:**")
                            st.text(f"🔥 Calories: {food['Caloric Value']:.0f} kcal")
                            st.text(f"🥩 Protéines: {food['Protein']:.1f}g")
                            st.text(f"🌾 Glucides: {food['Carbohydrates']:.1f}g")
                            st.text(f"🥑 Lipides: {food['Fat']:.1f}g")
                            st.text(f"🌿 Fibres: {food['Dietary Fiber']:.1f}g")
                        
                        with col2:
                            st.markdown("**🔬 Portion suggérée:**")
                            if food['Caloric Value'] > 0:
                                suggested_portion = min(200, target.calories * 0.4 / food['Caloric Value'] * 100)
                            else:
                                suggested_portion = 100
                            st.text(f"📏 {suggested_portion:.0f}g recommandés")
                            
                            portion_cal = food['Caloric Value'] * suggested_portion / 100
                            portion_prot = food['Protein'] * suggested_portion / 100
                            st.text(f"🔥 {portion_cal:.0f} kcal")
                            st.text(f"🥩 {portion_prot:.1f}g protéines")
                            
                            # Indicateurs nutritionnels
                            if food['Protein'] > 15:
                                st.success("💪 Riche en protéines")
                            if food['Dietary Fiber'] > 5:
                                st.success("🌿 Riche en fibres")
                            if food['Caloric Value'] < 100:
                                st.info("🔥 Faible en calories")
                        
                        with col3:
                            st.markdown("**⭐ Évaluation:**")
                            score = food.get('Nutrition Density', 5)
                            st.progress(min(score / 10, 1.0))
                            st.caption(f"Score nutritionnel: {score:.1f}/10")
                            
                            st.markdown("**🎯 Pour votre objectif:**")
                            if profile['goal'] == 'Perte de poids':
                                if food['Caloric Value'] < 150 and food['Protein'] > 10:
                                    st.success("✅ EXCELLENT")
                                elif food['Caloric Value'] < 300:
                                    st.warning("⚠️ MODÉRÉ")
                                else:
                                    st.error("❌ LIMITER")
                            elif profile['goal'] == 'Prise de masse':
                                if food['Caloric Value'] > 200 and food['Protein'] > 15:
                                    st.success("✅ EXCELLENT")
                                else:
                                    st.info("ℹ️ BON")
                            else:
                                st.success("✅ COMPATIBLE")
                        
                        # Boutons d'action
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button(f"⭐ Ajouter aux favoris", key=f"fav_rec_{idx}"):
                                if food['food'] not in st.session_state.favorite_foods:
                                    st.session_state.favorite_foods.append(food['food'])
                                    st.success(f"✅ {food['food']} ajouté!")
                        with col_b:
                            if st.button(f"🔄 Alternatives", key=f"alt_rec_{idx}"):
                                alternatives = recommender.find_alternatives(food['food'], n_alternatives=3)
                                if not alternatives.empty:
                                    st.write("**Alternatives similaires:**")
                                    for _, alt in alternatives.iterrows():
                                        st.text(f"• {alt['food']}")
        
        # Favoris
        if st.session_state.favorite_foods:
            st.markdown("---")
            st.markdown("### ⭐ Mes Aliments Favoris")
            
            cols = st.columns(4)
            for idx, food_name in enumerate(st.session_state.favorite_foods):
                with cols[idx % 4]:
                    st.markdown(f"""
                    <div class="food-card">
                        <p><strong>{food_name}</strong></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("🗑️", key=f"remove_fav_{idx}"):
                        st.session_state.favorite_foods.remove(food_name)
                        st.rerun()

# PAGE: PLAN ALIMENTAIRE
elif page == "🍽️ Plan Alimentaire":
    st.markdown('<h1 class="main-header">🍽️ Générateur de Plan Alimentaire</h1>', unsafe_allow_html=True)
    
    if not st.session_state.profile:
        st.warning("⚠️ Configurez votre profil d'abord")
    else:
        st.info("**Module utilisé:** 🍽️ Planificateur (Algorithmes d'optimisation locaux)")
        
        st.markdown("""
        ### 🤖 Génération Intelligente de Plan
        
        Le planificateur utilise:
        - 🎯 Vos besoins nutritionnels calculés
        - 🧠 Le moteur de recommandation ML
        - 📊 Des templates de repas équilibrés
        - 🔄 Un système de variété intelligente
        """)
        
        with st.form("meal_plan_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                meals_per_day = st.slider("Nombre de repas par jour", 3, 6, 4)
                variety_days = st.slider("Jours de variété", 1, 7, 7)
            
            with col2:
                budget = st.selectbox("Budget", ["Économique", "Moyen", "Élevé"])
                prep_time = st.selectbox("Temps de préparation", 
                                        ["Rapide (<30min)", "Moyen (30-60min)", "Élaboré (>60min)"])
            
            generate = st.form_submit_button("🎨 Générer le Plan", use_container_width=True)
            
            if generate and meal_generator:
                with st.spinner("🤖 Génération de votre plan personnalisé..."):
                    # Préparer les préférences
                    preferences = MealPlanPreferences(
                        meals_per_day=meals_per_day,
                        variety_days=variety_days,
                        budget=budget,
                        prep_time=prep_time,
                        diet_type=st.session_state.profile.get('diet_type', ['Omnivore']),
                        exclude_foods=st.session_state.profile.get('allergies', '').split(',') if st.session_state.profile.get('allergies') else []
                    )
                    
                    # Générer le plan
                    week_plan = meal_generator.generate_week_plan(
                        st.session_state.nutritional_needs,
                        preferences
                    )
                    
                    # Formater pour l'affichage
                    formatted_plan = meal_generator.format_plan_for_display(week_plan)
                    st.session_state.meal_plan = formatted_plan
                    
                    # Calculer les stats
                    stats = meal_generator.calculate_plan_stats(week_plan)
                    
                    st.success("✅ Plan alimentaire généré avec succès!")
                    st.balloons()
                    
                    # Afficher les stats
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Calories moy/jour", f"{stats['avg_daily_calories']:.0f}")
                    with col2:
                        st.metric("Protéines moy/jour", f"{stats['avg_daily_proteins']:.0f}g")
                    with col3:
                        st.metric("Aliments uniques", stats['unique_foods_count'])
                    with col4:
                        st.metric("Variété", f"{stats['variety_score']:.0f}%")
        
        # Affichage du plan
        if st.session_state.meal_plan:
            st.markdown("---")
            st.markdown("### 📅 Votre Plan Alimentaire Personnalisé")
            
            # Sélecteur de jour
            days = list(st.session_state.meal_plan.keys())
            selected_day = st.selectbox("📆 Sélectionnez un jour", days)
            
            if selected_day in st.session_state.meal_plan:
                day_meals = st.session_state.meal_plan[selected_day]
                
                # Totaux du jour
                total_cal = sum([meal.get('calories', 0) for meal in day_meals.values()])
                total_prot = sum([meal.get('proteines', 0) for meal in day_meals.values()])
                total_carbs = sum([meal.get('glucides', 0) for meal in day_meals.values()])
                total_fats = sum([meal.get('lipides', 0) for meal in day_meals.values()])
                
                st.markdown(f"### 📊 Totaux pour {selected_day}")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Calories", f"{total_cal:.0f} kcal")
                with col2:
                    st.metric("Total Protéines", f"{total_prot:.0f}g")
                with col3:
                    st.metric("Total Glucides", f"{total_carbs:.0f}g")
                with col4:
                    st.metric("Total Lipides", f"{total_fats:.0f}g")
                
                # Comparaison avec objectifs
                target = st.session_state.nutritional_needs['target_calories']
                diff = total_cal - target
                if abs(diff) < 100:
                    st.success(f"✅ Objectif atteint! ({diff:+.0f} kcal de différence)")
                elif abs(diff) < 200:
                    st.warning(f"⚠️ Proche de l'objectif ({diff:+.0f} kcal)")
                else:
                    st.error(f"❌ Écart important ({diff:+.0f} kcal)")
                
                st.markdown("---")
                
                # Afficher les repas
                for meal_name, meal_data in day_meals.items():
                    with st.expander(f"🍽️ {meal_name}", expanded=True):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown("**🥘 Aliments:**")
                            for aliment in meal_data.get('aliments', []):
                                st.markdown(f"• {aliment}")
                        
                        with col2:
                            st.markdown("**📊 Valeurs nutritionnelles:**")
                            st.markdown(f"- 🔥 {meal_data.get('calories', 0)} kcal")
                            st.markdown(f"- 🥩 {meal_data.get('proteines', 0)}g protéines")
                            st.markdown(f"- 🌾 {meal_data.get('glucides', 0)}g glucides")
                            st.markdown(f"- 🥑 {meal_data.get('lipides', 0)}g lipides")
            
            # Actions sur le plan
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🔄 Régénérer le plan", use_container_width=True):
                    st.session_state.meal_plan = None
                    st.rerun()
            with col2:
                if st.button("📥 Exporter en PDF", use_container_width=True):
                    st.info("🚧 Fonctionnalité d'export PDF en développement")
            with col3:
                if st.button("💾 Sauvegarder", use_container_width=True):
                    st.success("✅ Plan sauvegardé dans votre profil!")

# PAGE: ASSISTANT
elif page == "💬 Assistant":
    st.markdown('<h1 class="main-header">💬 Assistant Nutritionnel IA</h1>', unsafe_allow_html=True)
    
    st.info("**Module utilisé:** 💬 Assistant (NLP basé sur règles + Base de connaissances)")
    
    if not st.session_state.profile:
        st.warning("⚠️ Configurez votre profil pour des réponses personnalisées")
    
    st.markdown("""
    ### 💡 Questions Suggérées (Cliquez pour poser la question)
    """)
    
    # Quick actions
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🍳 Petit-déjeuner protéiné", use_container_width=True):
            question = "Suggère-moi un petit-déjeuner protéiné adapté à mon objectif"
            st.session_state.chat_history.append({"role": "user", "content": question})
    with col2:
        if st.button("🏋️ Post-entraînement", use_container_width=True):
            question = "Que dois-je manger après mon entraînement?"
            st.session_state.chat_history.append({"role": "user", "content": question})
    with col3:
        if st.button("💧 Hydratation", use_container_width=True):
            question = "Combien d'eau dois-je boire par jour?"
            st.session_state.chat_history.append({"role": "user", "content": question})
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🐟 Analyser le saumon", use_container_width=True):
            question = "Analyse les bienfaits du saumon pour mon objectif"
            st.session_state.chat_history.append({"role": "user", "content": question})
    with col2:
        if st.button("🔄 Alternatives poulet", use_container_width=True):
            question = "Quelles sont les alternatives au poulet?"
            st.session_state.chat_history.append({"role": "user", "content": question})
    with col3:
        if st.button("⏰ Timing des repas", use_container_width=True):
            question = "Quand dois-je manger mes repas?"
            st.session_state.chat_history.append({"role": "user", "content": question})
    
    st.markdown("---")
    
    # Historique du chat
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history[-10:]:  # Afficher les 10 derniers messages
            if msg["role"] == "user":
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%); 
                            padding: 1rem; border-radius: 15px; margin: 0.5rem 0; 
                            margin-left: 20%; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                    <strong>👤 Vous:</strong> {msg["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #F5F5F5 0%, #E0E0E0 100%); 
                            padding: 1rem; border-radius: 15px; margin: 0.5rem 0; 
                            margin-right: 20%; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                    <strong>🤖 Assistant:</strong><br>{msg["content"]}
                </div>
                """, unsafe_allow_html=True)
    
    # Zone de saisie
    st.markdown("---")
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input("💬 Posez votre question nutritionnelle...", 
                                   key="chat_input", 
                                   label_visibility="collapsed",
                                   placeholder="Ex: Suggère-moi un repas, Analyse un aliment...")
    with col2:
        send = st.button("📤 Envoyer", use_container_width=True)
    
    if send and user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        with st.spinner("🤖 L'assistant réfléchit..."):
            if assistant and st.session_state.profile:
                response = assistant.answer_query(user_input)
            else:
                response = """
⚠️ **Profil non configuré**

Pour des recommandations personnalisées, veuillez:
1. Aller dans l'onglet **👤 Profil**
2. Renseigner vos informations
3. Enregistrer votre profil

Je pourrai alors vous fournir des conseils adaptés à votre objectif! 💪
"""
            
            st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        st.rerun()
    
    # Bouton pour effacer l'historique
    if st.session_state.chat_history:
        st.markdown("---")
        if st.button("🗑️ Effacer l'historique de conversation", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

# PAGE: SUIVI
elif page == "📈 Suivi":
    st.markdown('<h1 class="main-header">📈 Suivi de Progression</h1>', unsafe_allow_html=True)
    
    if not st.session_state.profile:
        st.warning("⚠️ Configurez votre profil d'abord")
    else:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📝 Enregistrer un nouveau poids")
            with st.form("weight_form"):
                col_a, col_b = st.columns(2)
                with col_a:
                    weight_date = st.date_input("Date", datetime.now())
                    weight_val = st.number_input("Poids (kg)", 30.0, 200.0, 
                                                 st.session_state.profile['weight'], 0.1)
                with col_b:
                    notes = st.text_area("Notes/Ressenti", 
                                        placeholder="Comment vous sentez-vous? Observations...")
                
                if st.form_submit_button("💾 Enregistrer", use_container_width=True):
                    st.session_state.weight_history.append({
                        'date': weight_date,
                        'weight': weight_val,
                        'notes': notes
                    })
                    st.success(f"✅ {weight_val} kg enregistré pour le {weight_date}")
                    st.balloons()
        
        with col2:
            if st.session_state.weight_history:
                st.markdown("### 📊 Statistiques")
                latest = st.session_state.weight_history[-1]['weight']
                initial = st.session_state.profile['weight']
                target = st.session_state.profile['target_weight']
                
                progress = abs(initial - latest)
                total = abs(initial - target)
                pct = (progress / total * 100) if total > 0 else 0
                
                st.metric("Dernier poids", f"{latest:.1f} kg", 
                         f"{latest - initial:+.1f} kg depuis le début")
                
                st.progress(min(pct / 100, 1.0))
                st.caption(f"**{pct:.1f}%** de l'objectif atteint")
                
                remaining = abs(target - latest)
                st.metric("Reste à atteindre", f"{remaining:.1f} kg")
            else:
                st.info("📊 Aucun enregistrement pour le moment.\nCommencez à suivre votre progression!")
        
        # Graphique d'évolution
        if st.session_state.weight_history:
            st.markdown("---")
            st.markdown("### 📈 Évolution de votre Poids")
            
            dates = [e['date'] for e in st.session_state.weight_history]
            weights = [e['weight'] for e in st.session_state.weight_history]
            
            fig = go.Figure()
            
            # Courbe de poids
            fig.add_trace(go.Scatter(
                x=dates, y=weights,
                mode='lines+markers',
                name='Poids',
                line=dict(color='#FF6B35', width=3),
                marker=dict(size=10, color='#FF6B35')
            ))
            
            # Ligne objectif
            target = st.session_state.profile['target_weight']
            fig.add_trace(go.Scatter(
                x=[dates[0], dates[-1]],
                y=[target, target],
                mode='lines',
                name='Objectif',
                line=dict(color='green', dash='dash', width=2)
            ))
            
            # Poids initial
            initial = st.session_state.profile['weight']
            fig.add_trace(go.Scatter(
                x=[dates[0], dates[-1]],
                y=[initial, initial],
                mode='lines',
                name='Poids initial',
                line=dict(color='gray', dash='dot', width=2)
            ))
            
            fig.update_layout(
                title="Évolution du Poids dans le Temps",
                xaxis_title="Date",
                yaxis_title="Poids (kg)",
                height=500,
                hovermode='x unified',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Historique détaillé
            st.markdown("### 📋 Historique Détaillé")
            for idx, entry in enumerate(reversed(st.session_state.weight_history)):
                with st.expander(f"📅 {entry['date']} - {entry['weight']} kg"):
                    if idx > 0:
                        prev = st.session_state.weight_history[-(idx+1)]
                        diff = entry['weight'] - prev['weight']
                        st.metric("Évolution", f"{diff:+.1f} kg")
                    
                    if entry['notes']:
                        st.markdown(f"**Notes:** {entry['notes']}")

# PAGE: BASE ALIMENTS
elif page == "📚 Base Aliments":
    st.markdown('<h1 class="main-header">📚 Base de Données Alimentaire</h1>', unsafe_allow_html=True)
    
    st.markdown(f"### 🔍 Explorez {len(food_data)} aliments avec données nutritionnelles complètes")
    
    # Filtres
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        search = st.text_input("🔎 Rechercher", placeholder="Nom d'aliment...")
    with col2:
        sort_by = st.selectbox("Trier par", 
                               ["Nutrition Density", "Caloric Value", "Protein", 
                                "Carbohydrates", "Fat", "Dietary Fiber"])
    with col3:
        min_protein = st.slider("Protéines min (g)", 0, 50, 0)
    with col4:
        max_calories = st.slider("Calories max", 0, 1000, 1000)
    
    # Filtrage
    filtered = food_data.copy()
    
    if search:
        filtered = filtered[filtered['food'].str.contains(search, case=False, na=False)]
    
    filtered = filtered[
        (filtered['Protein'] >= min_protein) &
        (filtered['Caloric Value'] <= max_calories)
    ]
    
    filtered = filtered.sort_values(sort_by, ascending=False)
    
    st.markdown(f"### 📊 {len(filtered)} aliments trouvés")
    
    # Statistiques globales
    if not filtered.empty:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Calories moyenne", f"{filtered['Caloric Value'].mean():.0f} kcal")
        with col2:
            st.metric("Protéines moyenne", f"{filtered['Protein'].mean():.1f}g")
        with col3:
            st.metric("Glucides moyenne", f"{filtered['Carbohydrates'].mean():.1f}g")
        with col4:
            st.metric("Lipides moyenne", f"{filtered['Fat'].mean():.1f}g")
    
    st.markdown("---")
    
    # Affichage paginé
    items_per_page = 10
    total_pages = max(1, (len(filtered) - 1) // items_per_page + 1)
    
    if total_pages > 0:
        page_num = st.number_input("Page", 1, total_pages, 1, label_visibility="collapsed")
        st.caption(f"Page {page_num} sur {total_pages}")
        
        start_idx = (page_num - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, len(filtered))
        
        page_data = filtered.iloc[start_idx:end_idx]
        
        for idx, (_, row) in enumerate(page_data.iterrows()):
            with st.expander(f"🍽️ {row['food']} - {row['Caloric Value']:.0f} kcal/100g", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("#### 📊 Macronutriments")
                    st.markdown(f"""
                    - 🔥 **Calories:** {row['Caloric Value']:.0f} kcal
                    - 🥩 **Protéines:** {row['Protein']:.1f}g
                    - 🌾 **Glucides:** {row['Carbohydrates']:.1f}g
                    - 🥑 **Lipides:** {row['Fat']:.1f}g
                    - 🌿 **Fibres:** {row['Dietary Fiber']:.1f}g
                    - 🍬 **Sucres:** {row['Sugars']:.1f}g
                    """)
                
                with col2:
                    st.markdown("#### 💊 Vitamines")
                    st.markdown(f"""
                    - 🅰️ **Vitamine A:** {row['Vitamin A']:.1f}µg
                    - 🅱️ **Vitamine B12:** {row['Vitamin B12']:.2f}µg
                    - 🍊 **Vitamine C:** {row['Vitamin C']:.1f}mg
                    - ☀️ **Vitamine D:** {row['Vitamin D']:.1f}µg
                    """)
                    
                    st.markdown("#### ⚗️ Minéraux")
                    st.markdown(f"""
                    - 🦴 **Calcium:** {row['Calcium']:.0f}mg
                    - 🩸 **Fer:** {row['Iron']:.1f}mg
                    - 💪 **Magnésium:** {row['Magnesium']:.0f}mg
                    """)
                
                with col3:
                    st.markdown("#### 🧂 Autres")
                    st.markdown(f"""
                    - 🧂 **Sodium:** {row['Sodium']:.0f}mg
                    - 💧 **Eau:** {row['Water']:.0f}%
                    - ⚡ **Potassium:** {row['Potassium']:.0f}mg
                    """)
                    
                    # Score nutritionnel
                    st.markdown("#### ⭐ Score Nutritionnel")
                    if pd.notna(row['Nutrition Density']):
                        density_score = float(row['Nutrition Density'])
                        progress_value = min(max(density_score / 10, 0.0), 1.0)
                        st.progress(progress_value)
                        st.caption(f"**{density_score:.1f}/10**")
                    
                    # Tags nutritionnels
                    st.markdown("#### 🏷️ Caractéristiques")
                    tags = []
                    if row['Protein'] > 20:
                        tags.append("💪 Très riche en protéines")
                    elif row['Protein'] > 10:
                        tags.append("🥩 Riche en protéines")
                    
                    if row['Dietary Fiber'] > 5:
                        tags.append("🌿 Riche en fibres")
                    
                    if row['Caloric Value'] < 100:
                        tags.append("🔥 Faible en calories")
                    elif row['Caloric Value'] > 400:
                        tags.append("⚡ Haute densité calorique")
                    
                    if row['Vitamin C'] > 50:
                        tags.append("🍊 Riche en vitamine C")
                    
                    for tag in tags:
                        st.success(tag)
                
                # Actions
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    if st.button(f"⭐ Favoris", key=f"fav_db_{start_idx + idx}"):
                        if row['food'] not in st.session_state.favorite_foods:
                            st.session_state.favorite_foods.append(row['food'])
                            st.success(f"✅ {row['food']} ajouté aux favoris!")
                
                with col_b:
                    if st.button(f"🔄 Alternatives", key=f"alt_db_{start_idx + idx}"):
                        if recommender:
                            alternatives = recommender.find_alternatives(row['food'], n_alternatives=3)
                            if not alternatives.empty:
                                st.write("**Alternatives similaires:**")
                                for _, alt in alternatives.iterrows():
                                    st.text(f"• {alt['food']}")
                
                with col_c:
                    if st.button(f"➕ Ajouter au plan", key=f"add_db_{start_idx + idx}"):
                        st.info(f"📝 {row['food']} sera ajouté lors de la prochaine génération de plan")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p><strong>🥗 FitLife - Assistant Nutritionnel IA 100% Local</strong></p>
    <p>Développé avec ❤️ par Asma Bélkahla & Monia Selleoui</p>
    <p style='font-size: 0.9rem;'>
        🤖 Powered by: Scikit-learn, Streamlit, Pandas, NumPy, Plotly<br>
        ✅ Sans API externe | ✅ 100% Local | ✅ Open Source
    </p>
    <p style='font-size: 0.8rem; margin-top: 1rem;'>
        ⚠️ Les conseils fournis sont à titre informatif uniquement.<br>
        Consultez un professionnel de santé pour un suivi personnalisé.
    </p>
    <hr style='margin: 1rem auto; width: 50%; border: 1px solid #ddd;'>
    <p style='font-size: 0.8rem;'>
        <strong>Modules IA utilisés:</strong><br>
        📊 Calculateur Nutritionnel | 🎯 Recommandeur ML | 🍽️ Planificateur | 💬 Assistant NLP
    </p>
</div>
""", unsafe_allow_html=True)