"""
Tests unitaires pour le Module 1: Calculateur Nutritionnel
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from modules.nutrition_calculator import NutritionalCalculator, UserProfile

def test_bmr_calculation():
    """Test du calcul du BMR"""
    print("Test 1: Calcul BMR")
    
    # Homme 30 ans, 85kg, 175cm
    bmr_homme = NutritionalCalculator.calculate_bmr(85, 175, 30, 'Homme')
    expected_homme = (10 * 85) + (6.25 * 175) - (5 * 30) + 5
    assert abs(bmr_homme - expected_homme) < 0.1, f"BMR homme incorrect: {bmr_homme} vs {expected_homme}"
    print(f"  ✅ BMR Homme: {bmr_homme} kcal")
    
    # Femme 25 ans, 60kg, 165cm
    bmr_femme = NutritionalCalculator.calculate_bmr(60, 165, 25, 'Femme')
    expected_femme = (10 * 60) + (6.25 * 165) - (5 * 25) - 161
    assert abs(bmr_femme - expected_femme) < 0.1, f"BMR femme incorrect: {bmr_femme} vs {expected_femme}"
    print(f"  ✅ BMR Femme: {bmr_femme} kcal")
    
    print()

def test_tdee_calculation():
    """Test du calcul du TDEE"""
    print("Test 2: Calcul TDEE")
    
    bmr = 1800
    
    # Sédentaire
    tdee_sed = NutritionalCalculator.calculate_tdee(bmr, 'Sédentaire')
    assert tdee_sed == bmr * 1.2, "TDEE sédentaire incorrect"
    print(f"  ✅ TDEE Sédentaire: {tdee_sed} kcal")
    
    # Modérément actif
    tdee_mod = NutritionalCalculator.calculate_tdee(bmr, 'Modérément actif')
    assert tdee_mod == bmr * 1.55, "TDEE modéré incorrect"
    print(f"  ✅ TDEE Modéré: {tdee_mod} kcal")
    
    # Très actif
    tdee_actif = NutritionalCalculator.calculate_tdee(bmr, 'Très actif')
    assert tdee_actif == bmr * 1.725, "TDEE actif incorrect"
    print(f"  ✅ TDEE Actif: {tdee_actif} kcal")
    
    print()

def test_target_calories():
    """Test du calcul des calories cibles"""
    print("Test 3: Calories cibles selon objectif")
    
    tdee = 2500
    
    # Perte de poids
    cal_perte = NutritionalCalculator.calculate_target_calories(tdee, 'Perte de poids')
    expected_perte = tdee * 0.85
    assert abs(cal_perte - expected_perte) < 0.1, "Calories perte incorrectes"
    print(f"  ✅ Perte: {cal_perte} kcal (-15%)")
    
    # Maintien
    cal_maint = NutritionalCalculator.calculate_target_calories(tdee, 'Maintien')
    assert cal_maint == tdee, "Calories maintien incorrectes"
    print(f"  ✅ Maintien: {cal_maint} kcal")
    
    # Prise de masse
    cal_masse = NutritionalCalculator.calculate_target_calories(tdee, 'Prise de masse')
    expected_masse = tdee * 1.15
    assert abs(cal_masse - expected_masse) < 0.1, "Calories prise incorrectes"
    print(f"  ✅ Prise: {cal_masse} kcal (+15%)")
    
    print()

def test_macros_calculation():
    """Test du calcul des macronutriments"""
    print("Test 4: Calcul des macros")
    
    calories = 2000
    weight = 75
    
    # Perte de poids
    macros_perte = NutritionalCalculator.calculate_macros(calories, weight, 'Perte de poids')
    
    # Vérifier que les protéines sont calculées
    assert macros_perte['proteins'] > 0, "Protéines non calculées"
    print(f"  ✅ Protéines: {macros_perte['proteins']}g")
    
    # Vérifier que les glucides sont calculés
    assert macros_perte['carbs'] > 0, "Glucides non calculés"
    print(f"  ✅ Glucides: {macros_perte['carbs']}g")
    
    # Vérifier que les lipides sont calculés
    assert macros_perte['fats'] > 0, "Lipides non calculés"
    print(f"  ✅ Lipides: {macros_perte['fats']}g")
    
    # Vérifier la somme des calories
    total_cal = (macros_perte['proteins'] * 4 + 
                 macros_perte['carbs'] * 4 + 
                 macros_perte['fats'] * 9)
    assert abs(total_cal - calories) < 50, f"Total calories incorrect: {total_cal} vs {calories}"
    print(f"  ✅ Total calories: {total_cal:.0f} kcal (cible: {calories})")
    
    # Vérifier les pourcentages
    assert 'proteins_pct' in macros_perte, "Pourcentages manquants"
    assert 'carbs_pct' in macros_perte, "Pourcentages manquants"
    assert 'fats_pct' in macros_perte, "Pourcentages manquants"
    
    total_pct = (macros_perte['proteins_pct'] + 
                 macros_perte['carbs_pct'] + 
                 macros_perte['fats_pct'])
    assert abs(total_pct - 100) < 1, f"Total pourcentages incorrect: {total_pct}%"
    print(f"  ✅ Répartition: P{macros_perte['proteins_pct']:.0f}% G{macros_perte['carbs_pct']:.0f}% L{macros_perte['fats_pct']:.0f}%")
    
    print()

def test_duration_estimation():
    """Test de l'estimation de durée"""
    print("Test 5: Estimation durée objectif")
    
    # Perte de poids: 85kg -> 75kg
    weeks_perte, msg_perte = NutritionalCalculator.estimate_duration(85, 75, 'Perte de poids')
    expected_weeks_perte = 10 / 0.75  # 10kg à 0.75kg/semaine
    assert abs(weeks_perte - expected_weeks_perte) < 1, "Durée perte incorrecte"
    print(f"  ✅ Perte 10kg: {weeks_perte:.1f} semaines")
    print(f"     {msg_perte}")
    
    # Prise de masse: 70kg -> 75kg
    weeks_masse, msg_masse = NutritionalCalculator.estimate_duration(70, 75, 'Prise de masse')
    expected_weeks_masse = 5 / 0.375  # 5kg à 0.375kg/semaine
    assert abs(weeks_masse - expected_weeks_masse) < 1, "Durée prise incorrecte"
    print(f"  ✅ Prise 5kg: {weeks_masse:.1f} semaines")
    print(f"     {msg_masse}")
    
    # Poids atteint
    weeks_ok, msg_ok = NutritionalCalculator.estimate_duration(75, 75.3, 'Perte de poids')
    assert weeks_ok == 0, "Devrait retourner 0 si objectif atteint"
    print(f"  ✅ Objectif atteint: {msg_ok}")
    
    print()

def test_water_needs():
    """Test du calcul des besoins en eau"""
    print("Test 6: Besoins en eau")
    
    # Personne sédentaire 70kg
    water_sed = NutritionalCalculator.calculate_water_needs(70, 'Sédentaire')
    expected_sed = 70 * 0.033
    assert abs(water_sed - expected_sed) < 0.1, "Eau sédentaire incorrecte"
    print(f"  ✅ Sédentaire 70kg: {water_sed} L/jour")
    
    # Personne active 80kg
    water_actif = NutritionalCalculator.calculate_water_needs(80, 'Très actif')
    base = 80 * 0.033 * 1.3  # Facteur 1.3 pour très actif
    assert water_actif >= base * 0.9, "Eau actif incorrecte"
    print(f"  ✅ Très actif 80kg: {water_actif} L/jour")
    
    print()

def test_complete_needs():
    """Test du calcul complet des besoins"""
    print("Test 7: Calcul complet des besoins")
    
    profile = UserProfile(
        weight=80,
        height=175,
        age=30,
        sex='Homme',
        activity_level='Modérément actif',
        goal='Perte de poids',
        target_weight=72
    )
    
    needs = NutritionalCalculator.calculate_complete_needs(profile)
    
    # Vérifier que tous les champs sont présents
    required_fields = ['bmr', 'tdee', 'target_calories', 'macros', 
                       'duration_weeks', 'duration_message', 'water_liters', 'deficit_surplus']
    for field in required_fields:
        assert field in needs, f"Champ manquant: {field}"
    
    print(f"  ✅ BMR: {needs['bmr']} kcal")
    print(f"  ✅ TDEE: {needs['tdee']} kcal")
    print(f"  ✅ Calories cible: {needs['target_calories']} kcal")
    print(f"  ✅ Protéines: {needs['macros']['proteins']}g")
    print(f"  ✅ Glucides: {needs['macros']['carbs']}g")
    print(f"  ✅ Lipides: {needs['macros']['fats']}g")
    print(f"  ✅ Durée: {needs['duration_weeks']} semaines")
    print(f"  ✅ Eau: {needs['water_liters']} L/jour")
    print(f"  ✅ Déficit: {needs['deficit_surplus']} kcal")
    
    # Vérifier la cohérence
    assert needs['bmr'] < needs['tdee'], "BMR devrait être < TDEE"
    assert needs['target_calories'] < needs['tdee'], "Déficit pour perte"
    assert needs['deficit_surplus'] < 0, "Devrait être négatif pour perte"
    assert needs['duration_weeks'] > 0, "Durée devrait être positive"
    
    print()

def test_edge_cases():
    """Test des cas limites"""
    print("Test 8: Cas limites")
    
    # Très jeune
    bmr_young = NutritionalCalculator.calculate_bmr(60, 170, 18, 'Homme')
    assert bmr_young > 0, "BMR devrait être positif"
    print(f"  ✅ BMR jeune (18 ans): {bmr_young} kcal")
    
    # Âgé
    bmr_old = NutritionalCalculator.calculate_bmr(70, 170, 70, 'Homme')
    assert bmr_old > 0, "BMR devrait être positif"
    assert bmr_old < bmr_young, "BMR devrait diminuer avec l'âge"
    print(f"  ✅ BMR âgé (70 ans): {bmr_old} kcal")
    
    # Très léger
    bmr_light = NutritionalCalculator.calculate_bmr(45, 160, 25, 'Femme')
    assert bmr_light > 0, "BMR devrait être positif"
    print(f"  ✅ BMR léger (45kg): {bmr_light} kcal")
    
    # Très lourd
    bmr_heavy = NutritionalCalculator.calculate_bmr(120, 185, 35, 'Homme')
    assert bmr_heavy > 0, "BMR devrait être positif"
    assert bmr_heavy > bmr_light, "BMR devrait augmenter avec le poids"
    print(f"  ✅ BMR lourd (120kg): {bmr_heavy} kcal")
    
    print()

def run_all_tests():
    """Exécute tous les tests"""
    print("=" * 60)
    print("TESTS UNITAIRES - MODULE 1: CALCULATEUR NUTRITIONNEL")
    print("=" * 60)
    print()
    
    try:
        test_bmr_calculation()
        test_tdee_calculation()
        test_target_calories()
        test_macros_calculation()
        test_duration_estimation()
        test_water_needs()
        test_complete_needs()
        test_edge_cases()
        
        print("=" * 60)
        print("✅ TOUS LES TESTS SONT PASSÉS!")
        print("=" * 60)
        return True
        
    except AssertionError as e:
        print()
        print("=" * 60)
        print(f"❌ ÉCHEC DU TEST: {str(e)}")
        print("=" * 60)
        return False
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ ERREUR: {str(e)}")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)