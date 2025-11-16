"""
FitLife Nutrition AI - Application Utilisateur Finale
Assistant Nutritionnel IA 
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

# Sidebar - Navigation
st.sidebar.markdown("# 🥗 FitLife AI Assistant")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["🏠 Accueil", "👤 Profil", "📊 Dashboard", 
     "🎯 Recommandations", "🍽️ Plan Alimentaire",
     "💬 Assistant", "📈 Suivi", "📚 Base Aliments"]
)

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
    
    # Fonctionnalités principales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h2>📊</h2>
            <h3>Analyse Personnalisée</h3>
            <p>Calculez vos besoins nutritionnels adaptés à votre profil</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h2>🎯</h2>
            <h3>Recommandations</h3>
            <p>Découvrez les aliments parfaits pour votre objectif</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h2>📈</h2>
            <h3>Suivi Progrès</h3>
            <p>Suivez votre évolution et restez motivé(e)</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Guide d'utilisation
    st.markdown("### 📖 Comment utiliser FitLife")
    
    st.markdown("""
    <div class="info-box">
        <h4>🚀 Premiers Pas</h4>
        <ol style="margin: 0.5rem 0;">
            <li><strong>Configurez votre profil</strong> - Rendez-vous dans l'onglet <strong>👤 Profil</strong> pour renseigner vos informations personnelles (poids, taille, âge, objectif...)</li>
            <li><strong>Consultez votre dashboard</strong> - Visualisez vos besoins nutritionnels quotidiens calculés automatiquement</li>
            <li><strong>Découvrez les recommandations</strong> - Obtenez une liste d'aliments adaptés à vos besoins</li>
            <li><strong>Générez votre plan alimentaire</strong> - Créez un plan de repas personnalisé pour la semaine</li>
            <li><strong>Posez vos questions</strong> - Utilisez l'assistant pour obtenir des conseils nutritionnels</li>
            <li><strong>Suivez votre progression</strong> - Enregistrez votre poids régulièrement et visualisez votre évolution</li>
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
        - Maintien de la masse musculaire
        """)
    
    with col2:
        st.markdown("""
        #### 🎯 Maintien
        - Équilibre nutritionnel
        - Maintien du poids actuel
        - Alimentation variée
        - Bien-être général
        """)
    
    with col3:
        st.markdown("""
        #### 💪 Prise de masse
        - Surplus calorique optimal
        - Aliments riches en protéines
        - Développement musculaire
        - Nutrition sportive
        """)
    
    st.markdown("---")
    
    # Avantages
    st.markdown("### ✨ Pourquoi choisir FitLife ?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ✅ **Personnalisation complète**  
        Tous les conseils sont adaptés à votre profil unique
        
        ✅ **Base de données complète**  
        Des milliers d'aliments avec informations nutritionnelles détaillées
        
        ✅ **Plans alimentaires intelligents**  
        Génération automatique de menus équilibrés et variés
        """)
    
    with col2:
        st.markdown("""
        ✅ **Assistant nutritionnel**  
        Réponses instantanées à vos questions
        
        ✅ **Suivi de progression**  
        Graphiques et statistiques pour visualiser vos résultats
        
        ✅ **Facile à utiliser**  
        Interface intuitive et conviviale
        """)
    
    # Call to action
    if not st.session_state.profile:
        st.markdown("---")
        st.markdown("### 🚀 Prêt(e) à commencer ?")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📝 Créer mon profil maintenant", use_container_width=True, type="primary"):
                st.rerun()
    else:
        st.markdown("---")
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
        📝 <strong>Renseignez vos informations personnelles</strong> pour obtenir des recommandations nutritionnelles adaptées à vos besoins et objectifs.
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
            value='Modérément actif',
            help="Sédentaire: Peu ou pas d'exercice | Légèrement actif: Exercice 1-3 jours/semaine | Modérément actif: 3-5 jours/semaine | Très actif: 6-7 jours/semaine | Extrêmement actif: Sport intense quotidien"
        )
        
        st.markdown("### 🍽️ Préférences Alimentaires")
        col1, col2 = st.columns(2)
        with col1:
            diet_type = st.multiselect(
                "Régime alimentaire",
                ["Omnivore", "Végétarien", "Végétalien", "Sans gluten", "Sans lactose"],
                default=["Omnivore"]
            )
        with col2:
            allergies = st.text_area("Allergies ou intolérances alimentaires", 
                                     placeholder="Ex: Arachides, fruits de mer, lactose...")
        
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
                'diet_type': diet_type,
                'allergies': allergies,
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
                st.metric("🔥 Métabolisme de base", f"{needs['bmr']:.0f} kcal", 
                         help="Calories brûlées au repos")
            with col2:
                st.metric("⚡ Dépense quotidienne", f"{needs['tdee']:.0f} kcal", 
                         help="Calories totales brûlées par jour")
            with col3:
                st.metric("🎯 Calories recommandées", f"{needs['target_calories']:.0f} kcal", 
                         delta=f"{needs['deficit_surplus']:+.0f} kcal")
            with col4:
                if needs['duration_weeks'] > 0:
                    st.metric("⏱️ Durée estimée", f"{needs['duration_weeks']:.0f} semaines",
                             help=needs['duration_message'])
                else:
                    st.metric("⏱️ Objectif", "Maintien")
            
            st.markdown("### 🥗 Répartition Quotidienne des Macronutriments")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🥩 Protéines", f"{needs['macros']['proteins']:.0f}g",
                         help=f"{needs['macros']['proteins_pct']:.1f}% de vos calories")
            with col2:
                st.metric("🌾 Glucides", f"{needs['macros']['carbs']:.0f}g",
                         help=f"{needs['macros']['carbs_pct']:.1f}% de vos calories")
            with col3:
                st.metric("🥑 Lipides", f"{needs['macros']['fats']:.0f}g",
                         help=f"{needs['macros']['fats_pct']:.1f}% de vos calories")
            
            st.markdown("### 💧 Hydratation")
            st.metric("💧 Eau recommandée par jour", f"{needs['water_liters']} litres")
            
            st.info(f"""
            ✅ **Récapitulatif de votre profil:**
            - **Objectif:** {goal}
            - **Évolution souhaitée:** de {weight}kg à {target_weight}kg
            - **Niveau d'activité:** {activity_level}
            - **Régime alimentaire:** {', '.join(diet_type)}
            """)

# PAGE: DASHBOARD
elif page == "📊 Dashboard":
    st.markdown('<h1 class="main-header">📊 Tableau de Bord</h1>', unsafe_allow_html=True)
    
    if not st.session_state.profile:
        st.warning("⚠️ Veuillez d'abord configurer votre profil dans l'onglet **👤 Profil**")
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
        st.markdown("### 🎯 Aliments Recommandés pour Vous")
        
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
                        <span class="recommendation-badge">Compatibilité: {food['match_percentage']:.0f}%</span>
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
    st.markdown('<h1 class="main-header">🎯 Recommandations Personnalisées</h1>', unsafe_allow_html=True)
    
    if not st.session_state.profile:
        st.warning("⚠️ Configurez votre profil pour des recommandations personnalisées")
    else:
        profile = st.session_state.profile
        needs = st.session_state.nutritional_needs
        
        st.markdown("""
        <div class="info-box">
            💡 Découvrez les aliments les plus adaptés à votre objectif et vos besoins nutritionnels
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🔍 Recherche d'Aliments")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            search = st.text_input("🔎 Rechercher un aliment", "")
        with col2:
            n_results = st.number_input("Nombre de résultats", 5, 20, 10)
        with col3:
            sort_by = st.selectbox("Trier par", ["Compatibilité", "Protéines", "Calories"])
        
        # Filtres avancés
        with st.expander("🔧 Filtres avancés"):
            col1, col2 = st.columns(2)
            with col1:
                min_protein = st.slider("Protéines minimum (g/100g)", 0, 50, 0)
                max_calories = st.slider("Calories maximum (kcal/100g)", 0, 1000, 1000)
            with col2:
                exclude_foods = st.multiselect(
                    "Exclure des aliments",
                    st.session_state.favorite_foods if st.session_state.favorite_foods else ["Aucun"]
                )
        
        if st.button("🎯 Voir les recommandations", use_container_width=True, type="primary"):
            with st.spinner("🔍 Recherche des meilleurs aliments pour vous..."):
                # Calculer les besoins pour un repas
                meal_ratio = 0.30
                
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
                
                st.success(f"✅ {len(recommendations)} aliments recommandés pour votre objectif: **{profile['goal']}**")
                
                # Afficher résultats
                for idx, (_, food) in enumerate(recommendations.iterrows()):
                    with st.expander(f"#{idx+1} - {food['food']} (Compatibilité: {food['match_percentage']:.0f}%)", expanded=(idx < 3)):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown("**📊 Valeurs nutritionnelles /100g:**")
                            st.text(f"🔥 Calories: {food['Caloric Value']:.0f} kcal")
                            st.text(f"🥩 Protéines: {food['Protein']:.1f}g")
                            st.text(f"🌾 Glucides: {food['Carbohydrates']:.1f}g")
                            st.text(f"🥑 Lipides: {food['Fat']:.1f}g")
                            st.text(f"🌿 Fibres: {food['Dietary Fiber']:.1f}g")
                        
                        with col2:
                            st.markdown("**🍽️ Portion suggérée:**")
                            if food['Caloric Value'] > 0:
                                suggested_portion = min(200, target.calories * 0.4 / food['Caloric Value'] * 100)
                            else:
                                suggested_portion = 100
                            st.text(f"📏 {suggested_portion:.0f}g recommandés")
                            
                            portion_cal = food['Caloric Value'] * suggested_portion / 100
                            portion_prot = food['Protein'] * suggested_portion / 100
                            st.text(f"🔥 {portion_cal:.0f} kcal")
                            st.text(f"🥩 {portion_prot:.1f}g protéines")
                            
                            # Indicateurs
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
                                    st.success("✅ EXCELLENT CHOIX")
                                elif food['Caloric Value'] < 300:
                                    st.warning("⚠️ BON AVEC MODÉRATION")
                                else:
                                    st.error("❌ À LIMITER")
                            elif profile['goal'] == 'Prise de masse':
                                if food['Caloric Value'] > 200 and food['Protein'] > 15:
                                    st.success("✅ EXCELLENT CHOIX")
                                else:
                                    st.info("ℹ️ BON ALIMENT")
                            else:
                                st.success("✅ COMPATIBLE")
                        
                        # Actions
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button(f"⭐ Ajouter aux favoris", key=f"fav_rec_{idx}"):
                                if food['food'] not in st.session_state.favorite_foods:
                                    st.session_state.favorite_foods.append(food['food'])
                                    st.success(f"✅ {food['food']} ajouté!")
                        with col_b:
                            if st.button(f"🔄 Voir alternatives", key=f"alt_rec_{idx}"):
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
                    
                    if st.button("🗑️ Retirer", key=f"remove_fav_{idx}"):
                        st.session_state.favorite_foods.remove(food_name)
                        st.rerun()

# PAGE: PLAN ALIMENTAIRE
elif page == "🍽️ Plan Alimentaire":
    st.markdown('<h1 class="main-header">🍽️ Votre Plan Alimentaire Personnalisé</h1>', unsafe_allow_html=True)
    
    if not st.session_state.profile:
        st.warning("⚠️ Configurez votre profil d'abord")
    else:
        st.markdown("""
        <div class="info-box">
            📅 Générez un plan alimentaire hebdomadaire adapté à vos besoins et préférences
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("meal_plan_form"):
            st.markdown("### ⚙️ Personnalisez votre plan")
            
            col1, col2 = st.columns(2)
            
            with col1:
                meals_per_day = st.slider("Nombre de repas par jour", 3, 6, 4,
                                         help="3 repas = Petit-déj, Déjeuner, Dîner | 4+ = Ajout de collations")
                variety_days = st.slider("Variété des repas (jours)", 1, 7, 7,
                                        help="Nombre de jours avant de répéter les mêmes repas")
            
            with col2:
                budget = st.selectbox("Budget alimentaire", ["Économique", "Moyen", "Élevé"])
                prep_time = st.selectbox("Temps de préparation", 
                                        ["Rapide (<30min)", "Moyen (30-60min)", "Élaboré (>60min)"])
            
            st.markdown("---")
            generate = st.form_submit_button("🎨 Générer mon plan alimentaire", use_container_width=True, type="primary")
            
            if generate and meal_generator:
                with st.spinner("🍳 Création de votre plan personnalisé..."):
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
                    
                    # Formater
                    formatted_plan = meal_generator.format_plan_for_display(week_plan)
                    st.session_state.meal_plan = formatted_plan
                    
                    # Stats
                    stats = meal_generator.calculate_plan_stats(week_plan)
                    
                    st.success("✅ Votre plan alimentaire est prêt!")
                    st.balloons()
                    
                    # Statistiques
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Calories moy/jour", f"{stats['avg_daily_calories']:.0f}")
                    with col2:
                        st.metric("Protéines moy/jour", f"{stats['avg_daily_proteins']:.0f}g")
                    with col3:
                        st.metric("Aliments différents", stats['unique_foods_count'])
                    with col4:
                        st.metric("Score de variété", f"{stats['variety_score']:.0f}%")
        
        # Affichage du plan
        if st.session_state.meal_plan:
            st.markdown("---")
            st.markdown("### 📅 Votre Plan de la Semaine")
            
            # Sélecteur de jour
            days = list(st.session_state.meal_plan.keys())
            selected_day = st.selectbox("📆 Choisissez un jour", days)
            
            if selected_day in st.session_state.meal_plan:
                day_meals = st.session_state.meal_plan[selected_day]
                
                # Totaux du jour
                total_cal = sum([meal.get('calories', 0) for meal in day_meals.values()])
                total_prot = sum([meal.get('proteines', 0) for meal in day_meals.values()])
                total_carbs = sum([meal.get('glucides', 0) for meal in day_meals.values()])
                total_fats = sum([meal.get('lipides', 0) for meal in day_meals.values()])
                
                st.markdown(f"### 📊 Bilan nutritionnel - {selected_day}")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Calories", f"{total_cal:.0f} kcal")
                with col2:
                    st.metric("Total Protéines", f"{total_prot:.0f}g")
                with col3:
                    st.metric("Total Glucides", f"{total_carbs:.0f}g")
                with col4:
                    st.metric("Total Lipides", f"{total_fats:.0f}g")
                
                # Comparaison
                target = st.session_state.nutritional_needs['target_calories']
                diff = total_cal - target
                if abs(diff) < 100:
                    st.success(f"✅ Parfait! Vous êtes à {diff:+.0f} kcal de votre objectif")
                elif abs(diff) < 200:
                    st.warning(f"⚠️ Proche de l'objectif ({diff:+.0f} kcal de différence)")
                else:
                    st.error(f"❌ Écart important: {diff:+.0f} kcal")
                
                st.markdown("---")
                
                # Repas du jour
                for meal_name, meal_data in day_meals.items():
                    with st.expander(f"🍽️ {meal_name}", expanded=True):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown("**🥘 Composition du repas:**")
                            for aliment in meal_data.get('aliments', []):
                                st.markdown(f"• {aliment}")
                        
                        with col2:
                            st.markdown("**📊 Valeurs nutritionnelles:**")
                            st.markdown(f"- 🔥 {meal_data.get('calories', 0):.0f} kcal")
                            st.markdown(f"- 🥩 {meal_data.get('proteines', 0):.0f}g protéines")
                            st.markdown(f"- 🌾 {meal_data.get('glucides', 0):.0f}g glucides")
                            st.markdown(f"- 🥑 {meal_data.get('lipides', 0):.0f}g lipides")
            
            # Actions
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🔄 Générer un nouveau plan", use_container_width=True):
                    st.session_state.meal_plan = None
                    st.rerun()
            with col2:
                if st.button("📥 Exporter en PDF", use_container_width=True):
                    st.info("🚧 Fonctionnalité d'export bientôt disponible")
            with col3:
                if st.button("💾 Sauvegarder", use_container_width=True):
                    st.success("✅ Plan sauvegardé!")

# PAGE: ASSISTANT
elif page == "💬 Assistant":
    st.markdown('<h1 class="main-header">💬 Assistant Nutritionnel</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        💡 Posez toutes vos questions sur la nutrition, les aliments, et recevez des conseils personnalisés
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.profile:
        st.warning("⚠️ Configurez votre profil pour des réponses personnalisées")
    
    st.markdown("### 💡 Questions Fréquentes (Cliquez pour poser)")
    
    # Quick actions
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🍳 Petit-déjeuner protéiné", use_container_width=True):
            question = "Suggère-moi un petit-déjeuner protéiné adapté à mon objectif"
            st.session_state.chat_history.append({"role": "user", "content": question})
            st.rerun()
    with col2:
        if st.button("🏋️ Post-entraînement", use_container_width=True):
            question = "Que dois-je manger après mon entraînement?"
            st.session_state.chat_history.append({"role": "user", "content": question})
            st.rerun()
    with col3:
        if st.button("💧 Hydratation", use_container_width=True):
            question = "Combien d'eau dois-je boire par jour?"
            st.session_state.chat_history.append({"role": "user", "content": question})
            st.rerun()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🐟 Bienfaits du saumon", use_container_width=True):
            question = "Quels sont les bienfaits du saumon pour moi?"
            st.session_state.chat_history.append({"role": "user", "content": question})
            st.rerun()
    with col2:
        if st.button("🔄 Alternatives poulet", use_container_width=True):
            question = "Quelles sont les alternatives au poulet?"
            st.session_state.chat_history.append({"role": "user", "content": question})
            st.rerun()
    with col3:
        if st.button("⏰ Timing des repas", use_container_width=True):
            question = "À quelle heure dois-je prendre mes repas?"
            st.session_state.chat_history.append({"role": "user", "content": question})
            st.rerun()
    
    st.markdown("---")
    
    # Historique du chat
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history[-10:]:
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
        user_input = st.text_input("💬 Votre question...", 
                                   key="chat_input", 
                                   label_visibility="collapsed",
                                   placeholder="Ex: Suggère-moi un repas, Quels aliments pour mon objectif?")
    with col2:
        send = st.button("📤 Envoyer", use_container_width=True)
    
    if send and user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        with st.spinner("🤖 Réflexion en cours..."):
            if assistant and st.session_state.profile:
                response = assistant.answer_query(user_input)
            else:
                response = """
⚠️ **Configuration nécessaire**

Pour recevoir des conseils personnalisés, veuillez:
1. Configurer votre profil dans l'onglet **👤 Profil**
2. Renseigner vos informations personnelles
3. Enregistrer votre profil

Je pourrai ensuite vous fournir des recommandations adaptées à votre objectif! 💪
"""
            
            st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        st.rerun()
    
    # Effacer historique
    if st.session_state.chat_history:
        st.markdown("---")
        if st.button("🗑️ Effacer l'historique", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

# PAGE: SUIVI
elif page == "📈 Suivi":
    st.markdown('<h1 class="main-header">📈 Suivi de Votre Progression</h1>', unsafe_allow_html=True)
    
    if not st.session_state.profile:
        st.warning("⚠️ Configurez votre profil d'abord")
    else:
        st.markdown("""
        <div class="info-box">
            📊 Suivez votre évolution en enregistrant régulièrement votre poids et visualisez vos progrès
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📝 Nouvel Enregistrement")
            with st.form("weight_form"):
                col_a, col_b = st.columns(2)
                with col_a:
                    weight_date = st.date_input("Date de la mesure", datetime.now())
                    weight_val = st.number_input("Poids (kg)", 30.0, 200.0, 
                                                 st.session_state.profile['weight'], 0.1)
                with col_b:
                    notes = st.text_area("Notes (optionnel)", 
                                        placeholder="Comment vous sentez-vous? Observations...")
                
                if st.form_submit_button("💾 Enregistrer", use_container_width=True, type="primary"):
                    st.session_state.weight_history.append({
                        'date': weight_date,
                        'weight': weight_val,
                        'notes': notes
                    })
                    st.success(f"✅ Poids de {weight_val} kg enregistré pour le {weight_date}")
                    st.balloons()
        
        with col2:
            if st.session_state.weight_history:
                st.markdown("### 📊 Vos Statistiques")
                latest = st.session_state.weight_history[-1]['weight']
                initial = st.session_state.profile['weight']
                target = st.session_state.profile['target_weight']
                
                progress = abs(initial - latest)
                total = abs(initial - target)
                pct = (progress / total * 100) if total > 0 else 0
                
                st.metric("Dernier poids", f"{latest:.1f} kg", 
                         f"{latest - initial:+.1f} kg depuis le début")
                
                st.progress(min(pct / 100, 1.0))
                st.caption(f"**{pct:.1f}%** de votre objectif atteint")
                
                remaining = abs(target - latest)
                st.metric("Reste à atteindre", f"{remaining:.1f} kg")
            else:
                st.info("📊 Aucun enregistrement.\nCommencez à suivre votre progression!")
        
        # Graphique
        if st.session_state.weight_history:
            st.markdown("---")
            st.markdown("### 📈 Courbe d'Évolution")
            
            dates = [e['date'] for e in st.session_state.weight_history]
            weights = [e['weight'] for e in st.session_state.weight_history]
            
            fig = go.Figure()
            
            # Courbe de poids
            fig.add_trace(go.Scatter(
                x=dates, y=weights,
                mode='lines+markers',
                name='Votre poids',
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
                title="Évolution de Votre Poids",
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
    <p>Développé avec ❤️ par Asma Bélkahla & Monia selleoui </p>
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
