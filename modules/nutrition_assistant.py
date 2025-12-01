"""
Module 4: Assistant Nutritionnel Conversationnel
Système basé sur des règles et templates (sans API externe)
Auteurs: Asma Bélkahla & Monia Selleoui
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import pandas as pd

@dataclass
class ConversationContext:
    """Contexte de conversation pour personnalisation"""
    user_profile: Optional[Dict] = None
    nutritional_needs: Optional[Dict] = None
    recent_queries: List[str] = None
    
    def __post_init__(self):
        if self.recent_queries is None:
            self.recent_queries = []

class NutritionAssistant:
    """
    Assistant conversationnel basé sur des règles et reconnaissance de patterns
    Alternative intelligente sans dépendance API externe
    
    Architecture:
    1. Détection intentions: regex patterns
    2. Extraction entités: noms d'aliments, quantités
    3. Génération réponses: templates contextuels
    4. Personnalisation: utilise profil utilisateur
    """
    
    # Patterns de questions (regex pour détection d'intentions)
    PATTERNS = {
        'petit_dejeuner': r'(petit[- ]d[eé]jeuner|breakfast|matin)',
        'post_entrainement': r'(post[- ]entra[îi]nement|apr[èe]s (sport|musculation|training|séance))',
        'calories': r'(calorie|kcal|[ée]nergie)',
        'proteines': r'(prot[ée]ine|protein)',
        'perte_poids': r'(perd(re|[- ]de[- ]poids)|maigrir|mincir)',
        'prise_masse': r'(pris(e[- ]de[- ]masse|[- ]masse)|muscle|hypertrophie)',
        'analyse_aliment': r'(analys|bienfait|b[ée]n[ée]fice|propri[ée]t[ée])',
        'alternatives': r'(alternat|remplac|substitu)',
        'hydratation': r'(eau|hydr|boire)',
        'vitamines': r'(vitamine|nutriment|min[ée]raux)',
        'recette': r'(recette|pr[ée]par|cuisin)',
        'portion': r'(portion|quantit[ée]|combien)',
        'timing': r'(quand|heure|moment|timing)'
    }
    
    # Templates de réponses personnalisées
    RESPONSE_TEMPLATES = {
        'petit_dejeuner': {
            'Perte de poids': """
🳳 **Petit-déjeuner pour perte de poids** (adapté à votre profil)

Objectif: {calories:.0f} kcal | {proteins:.0f}g protéines

**Suggestions:**
1. **Option protéinée classique:**
   - 3 blancs d'œufs + 1 œuf entier (scrambled)
   - 40g flocons d'avoine
   - 1 pomme
   - Café/thé sans sucre

2. **Option yaourt:**
   - 200g yaourt grec 0%
   - 30g granola maison
   - Fruits rouges (100g)
   - 10 amandes

3. **Option smoothie:**
   - 30g whey protéine
   - 1 banane
   - 100g épinards
   - 200ml lait d'amande
   - 1 c.à.s. beurre d'amande

**Principes clés:**
✅ Riche en protéines (satiété prolongée)
✅ Fibres (contrôle glycémie)
✅ Faible en sucres ajoutés
✅ Hydratation importante
""",
            'Prise de masse': """
💪 **Petit-déjeuner pour prise de masse** (adapté à votre profil)

Objectif: {calories:.0f} kcal | {proteins:.0f}g protéines

**Suggestions anaboliques:**
1. **Option complète:**
   - 4 œufs entiers
   - 80g flocons d'avoine + miel
   - 2 tranches pain complet + beurre d'arachide
   - 1 banane
   - Jus d'orange

2. **Option pancakes:**
   - 100g pancakes protéinés (avoine+œufs+whey)
   - Sirop d'érable
   - 30g amandes
   - 200ml lait entier

**Timing:** Dans l'heure suivant le réveil pour activer le métabolisme
""",
            'Maintien': """
⚖️ **Petit-déjeuner équilibré** (adapté à votre profil)

Objectif: {calories:.0f} kcal | {proteins:.0f}g protéines

**Option équilibrée:**
- 2 œufs + 50g jambon
- 2 tranches pain complet
- 1 portion fruits
- 1 laitage
- Boisson chaude
"""
        },
        
        'post_entrainement': """
🏋️ **Nutrition post-entraînement optimale**

**Fenêtre anabolique (0-30 min):**
Si entraînement intense > 60 min:
- 20-40g protéines rapides (whey, blanc poulet)
- 0.5-1g/kg glucides selon objectif
  * Perte: 0.5g/kg (ex: {weight}kg = {carbs_loss:.0f}g)
  * Masse: 1g/kg (ex: {weight}kg = {carbs_gain:.0f}g)

**Exemples pratiques:**

🥤 **Option shake rapide:**
- 30g whey protéine
- 1-2 bananes
- 300ml eau/lait
- Optionnel: créatine 5g

🍗 **Option repas solide (30-60 min):**
- 150g poulet/poisson
- 100-200g riz/patate douce
- Légumes à volonté

**Hydratation:**
- Minimum 500ml eau + électrolytes
- Continuer à boire régulièrement (30ml/kg/jour)

**Pourquoi c'est important:**
✅ Restauration glycogène musculaire
✅ Synthèse protéique maximale
✅ Réduction catabolisme
✅ Récupération accélérée
""",
        
        'analyse_aliment': """
🔍 **Analyse nutritionnelle de {food_name}**

**Composition pour 100g:**
- Calories: {calories:.0f} kcal
- Protéines: {proteins:.1f}g {protein_rating}
- Glucides: {carbs:.1f}g
- Lipides: {fats:.1f}g
- Fibres: {fiber:.1f}g {fiber_rating}

**Intérêt pour votre objectif ({goal}):**
{goal_analysis}

**Quand le consommer:**
{timing_advice}

**Alternatives similaires:**
{alternatives}
""",
        
        'hydratation': """
💧 **Hydratation optimale pour votre profil**

**Besoin quotidien estimé:** {water:.1f} litres/jour
(Basé sur: {weight}kg + activité {activity})

**Répartition recommandée:**
- Au réveil: 300-500ml (réhydratation nocturne)
- Avant repas: 200ml (aide digestion)
- Pendant entraînement: 150-200ml/15min
- Post-entraînement: 150% pertes sudation
- Entre les repas: régulièrement

**Signes de déshydratation:**
⚠️ Urine foncée
⚠️ Fatigue
⚠️ Maux de tête
⚠️ Baisse performance

**Astuces:**
✅ Bouteille toujours à portée
✅ Application rappel
✅ Eau aromatisée (citron, concombre)
✅ Thé/tisane comptent aussi

**Attention:** Augmenter si:
- Chaleur/été
- Entraînement intense
- Sudation importante
"""
    }
    
    def __init__(self, food_df: pd.DataFrame, recommender):
        self.food_df = food_df
        self.recommender = recommender
        self.context = ConversationContext()
    
    def set_context(self, profile: Dict, needs: Dict):
        """Configure le contexte utilisateur pour personnalisation"""
        self.context.user_profile = profile
        self.context.nutritional_needs = needs
    
    def _detect_intent(self, query: str) -> Tuple[str, float]:
        """
        Détecte l'intention de l'utilisateur via patterns
        
        Args:
            query: Question de l'utilisateur
            
        Returns:
            Tuple (intent, confidence_score)
        """
        query_lower = query.lower()
        
        # Chercher patterns
        for intent, pattern in self.PATTERNS.items():
            if re.search(pattern, query_lower):
                return intent, 0.9
        
        # Intent par défaut
        return 'general', 0.5
    
    def _extract_food_name(self, query: str) -> Optional[str]:
        """
        Extrait un nom d'aliment de la requête
        
        Args:
            query: Question de l'utilisateur
            
        Returns:
            Nom de l'aliment trouvé ou None
        """
        query_lower = query.lower()
        
        # Chercher dans la base
        for food in self.food_df['food'].values:
            if food.lower() in query_lower:
                return food
        
        # Mots clés communs
        keywords = ['poulet', 'saumon', 'riz', 'avoine', 'œuf', 'banane', 
                   'brocoli', 'quinoa', 'amande', 'yaourt', 'thon', 'tofu',
                   'lentille', 'épinard', 'avocat', 'patate']
        
        for keyword in keywords:
            if keyword in query_lower:
                # Chercher correspondance partielle
                matches = self.food_df[
                    self.food_df['food'].str.contains(keyword, case=False, na=False)
                ]
                if not matches.empty:
                    return matches.iloc[0]['food']
        
        return None
    
    def _rate_nutrient(self, value: float, nutrient_type: str) -> str:
        """
        Évalue un nutriment avec emoji
        
        Args:
            value: Valeur du nutriment
            nutrient_type: Type ('protein' ou 'fiber')
            
        Returns:
            Label d'évaluation
        """
        ratings = {
            'protein': {
                'high': (20, '💪 Excellent source'),
                'medium': (10, '✅ Bonne source'),
                'low': (0, 'ℹ️ Source modérée')
            },
            'fiber': {
                'high': (5, '🌾 Riche en fibres'),
                'medium': (2, '✅ Contient des fibres'),
                'low': (0, 'ℹ️ Faible en fibres')
            }
        }
        
        thresholds = ratings.get(nutrient_type, {})
        
        for level in ['high', 'medium', 'low']:
            threshold, label = thresholds.get(level, (0, ''))
            if value >= threshold:
                return label
        
        return ''
    
    def _analyze_food_for_goal(self, food_data: pd.Series, goal: str) -> str:
        """
        Analyse un aliment selon l'objectif utilisateur
        
        Args:
            food_data: Données de l'aliment
            goal: Objectif utilisateur
            
        Returns:
            Analyse textuelle personnalisée
        """
        analyses = {
            'Perte de poids': lambda f: f"""
{'✅ EXCELLENT' if f['Caloric Value'] < 150 else '⚠️ MODÉRÉ' if f['Caloric Value'] < 300 else '❌ LIMITER'} pour la perte de poids
- Densité calorique: {'faible' if f['Caloric Value'] < 150 else 'modérée' if f['Caloric Value'] < 300 else 'élevée'}
- Satiété: {'élevée' if f['Protein'] > 15 or f['Dietary Fiber'] > 5 else 'moyenne'}
- Recommandation: {'Consommer régulièrement' if f['Caloric Value'] < 150 else 'Portions contrôlées'}
""",
            'Prise de masse': lambda f: f"""
{'✅ EXCELLENT' if f['Caloric Value'] > 200 and f['Protein'] > 15 else '✅ BON' if f['Caloric Value'] > 100 else '⚠️ COMPLÉTER'} pour la prise de masse
- Densité calorique: {'élevée (parfait)' if f['Caloric Value'] > 200 else 'modérée (ok)'}
- Protéines: {'élevées (anabolique)' if f['Protein'] > 20 else 'modérées'}
- Recommandation: {'Base de votre alimentation' if f['Protein'] > 20 else 'Combiner avec protéines'}
""",
            'Maintien': lambda f: f"""
✅ Compatible avec le maintien
- Équilibre nutritionnel: {'excellent' if f.get('Nutrition Density', 5) > 7 else 'bon'}
- Recommandation: Intégrer dans une alimentation variée
"""
        }
        
        return analyses.get(goal, analyses['Maintien'])(food_data)
    
    def answer_query(self, query: str) -> str:
        """
        Répond à une question utilisateur
        Point d'entrée principal
        
        Args:
            query: Question de l'utilisateur
            
        Returns:
            Réponse personnalisée
        """
        # Détection intention
        intent, confidence = self._detect_intent(query)
        
        # Pas de contexte
        if not self.context.user_profile:
            return """
⚠️ **Profil non configuré**

Pour des recommandations personnalisées, merci de configurer votre profil avec:
- Poids, taille, âge
- Objectif (perte/maintien/prise de masse)
- Niveau d'activité

Je pourrai ensuite vous fournir des conseils adaptés! 💪
"""
        
        profile = self.context.user_profile
        needs = self.context.nutritional_needs
        
        # Génération réponse selon intent
        if intent == 'petit_dejeuner':
            goal = profile.get('goal', 'Maintien')
            template = self.RESPONSE_TEMPLATES['petit_dejeuner'].get(goal, '')
            
            meal_ratio = 0.25
            return template.format(
                calories=needs['target_calories'] * meal_ratio,
                proteins=needs['macros']['proteins'] * meal_ratio
            )
        
        elif intent == 'post_entrainement':
            weight = profile['weight']
            return self.RESPONSE_TEMPLATES['post_entrainement'].format(
                weight=weight,
                carbs_loss=weight * 0.5,
                carbs_gain=weight * 1.0
            )
        
        elif intent == 'analyse_aliment':
            food_name = self._extract_food_name(query)
            
            if not food_name:
                return """
❓ **Aliment non trouvé**

Je n'ai pas identifié l'aliment dans votre question.

Essayez: "Analyse les bienfaits du poulet pour mon objectif"

💡 Aliments disponibles: poulet, saumon, riz, avoine, œufs, etc.
"""
            
            food_data = self.food_df[self.food_df['food'] == food_name].iloc[0]
            
            # Trouver alternatives
            alternatives = self.recommender.find_alternatives(food_name, n_alternatives=3)
            alt_list = ', '.join(alternatives['food'].tolist()) if not alternatives.empty else 'N/A'
            
            return self.RESPONSE_TEMPLATES['analyse_aliment'].format(
                food_name=food_name,
                calories=food_data['Caloric Value'],
                proteins=food_data['Protein'],
                protein_rating=self._rate_nutrient(food_data['Protein'], 'protein'),
                carbs=food_data['Carbohydrates'],
                fats=food_data['Fat'],
                fiber=food_data['Dietary Fiber'],
                fiber_rating=self._rate_nutrient(food_data['Dietary Fiber'], 'fiber'),
                goal=profile['goal'],
                goal_analysis=self._analyze_food_for_goal(food_data, profile['goal']),
                timing_advice="Idéal post-entraînement" if food_data['Protein'] > 20 else "Tout moment de la journée",
                alternatives=alt_list
            )
        
        elif intent == 'hydratation':
            from nutrition_calculator import NutritionalCalculator
            water = NutritionalCalculator.calculate_water_needs(
                profile['weight'],
                profile['activity_level']
            )
            
            return self.RESPONSE_TEMPLATES['hydratation'].format(
                water=water,
                weight=profile['weight'],
                activity=profile['activity_level']
            )
        
        # Réponse générale
        return f"""
💬 **Question notée**

Je comprends votre question sur: **{query}**

🤖 **Conseils généraux pour votre objectif ({profile['goal']}):**

{'- Privilégier déficit calorique modéré (15%)' if profile['goal'] == 'Perte de poids' else ''}
{'- Surplus calorique contrôlé (+15%)' if profile['goal'] == 'Prise de masse' else ''}
- Protéines: {needs['macros']['proteins']:.0f}g/jour minimum
- Hydratation: {profile['weight'] * 0.033:.1f}L/jour
- Sommeil: 7-9h/nuit crucial

💡 **Questions suggérées:**
- "Suggère-moi un petit-déjeuner"
- "Que manger après l'entraînement?"
- "Analyse le saumon pour mon objectif"
"""


# ===== TESTS =====
def test_assistant():
    """Tests de l'assistant"""
    print("=== TESTS DE L'ASSISTANT NUTRITIONNEL ===\n")
    
    # Dataset test
    test_data = pd.DataFrame({
        'food': ['Poulet grillé', 'Saumon', 'Riz complet', 'Brocoli'],
        'Caloric Value': [165, 208, 370, 34],
        'Protein': [31, 20, 7.9, 2.8],
        'Carbohydrates': [0, 0, 77, 6.6],
        'Fat': [3.6, 13, 2.9, 0.4],
        'Dietary Fiber': [0, 0, 3.5, 2.6],
        'Saturated Fats': [1, 3, 0.6, 0.1],
        'Sugars': [0, 0, 0.8, 1.7],
        'Sodium': [74, 59, 7, 33]
    })
    
    from food_recommender import FoodRecommendationEngine
    recommender = FoodRecommendationEngine(test_data)
    
    assistant = NutritionAssistant(test_data, recommender)
    
    # Configurer contexte
    profile = {
        'weight': 80,
        'height': 175,
        'age': 30,
        'goal': 'Perte de poids',
        'activity_level': 'Modérément actif'
    }
    
    needs = {
        'target_calories': 2100,
        'macros': {'proteins': 144, 'carbs': 210, 'fats': 60}
    }
    
    assistant.set_context(profile, needs)
    
    # Test questions
    queries = [
        "Suggère-moi un petit-déjeuner protéiné",
        "Que dois-je manger après mon entraînement?",
        "Analyse le poulet pour mon objectif",
        "Combien d'eau dois-je boire?"
    ]
    
    for query in queries:
        print(f"\n{'='*60}")
        print(f"Q: {query}")
        print(f"{'='*60}")
        response = assistant.answer_query(query)
        print(response)
        print()
    
    print("✅ Tests complétés!\n")


if __name__ == "__main__":
    test_assistant()