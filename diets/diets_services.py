from .models import Diet
from hairstyle.models import Recipe


'''Functions below for calculate amount of calories for each eating'''


def calculate_recipes_for_breakfast_for_lose_weight_program(amount_of_carbs, amount_of_fat, amount_of_protein,
                                                            breakfast_calories):
    breakfast_recipes = Recipe.objects.filter(
        calories__range=(breakfast_calories - 20, breakfast_calories + 20)).filter(
        protein__range=(((amount_of_protein * 0.3) - 5), ((amount_of_protein * 0.3) + 5))).filter(
        carbohydrates__range=(((amount_of_carbs * 0.4) - 5), ((amount_of_carbs * 0.4) + 5))).filter(
        fat__range=((amount_of_fat * 0.4) - 5, (amount_of_fat * 0.4) + 5))

    return breakfast_recipes


def calculate_recipes_for_lunch_for_lose_program(amount_of_carbs, amount_of_fat, amount_of_protein,
                                                 lunch_calories):
    lunch_recipes = Recipe.objects.filter(calories__range=(lunch_calories - 20, lunch_calories + 20)).filter(
        protein__range=((amount_of_protein * 0.4) - 5, ((amount_of_protein * 0.4) + 5))).filter(
        carbohydrates__range=((amount_of_carbs * 0.4) - 5, (amount_of_carbs * 0.4) + 5)).filter(
        fat__range=((amount_of_fat * 0.4) - 5, (amount_of_fat * 0.4) + 5))
    return lunch_recipes


def calculate_recipes_for_dinner_for_lose_program(amount_of_carbs, amount_of_fat, amount_of_protein,
                                                  dinner_calories):
    dinner_recipes = Recipe.objects.filter(
        protein__range=((amount_of_protein * 0.3) - 5, ((amount_of_protein * 0.3) + 5))).filter(
        calories__range=(dinner_calories - 20, dinner_calories + 20)).filter(
        carbohydrates__range=((amount_of_carbs * 0.2) - 5, (amount_of_carbs * 0.2) + 5)).filter(
        fat__range=((amount_of_fat * 0.2) - 5, (amount_of_fat * 0.4) + 5))
    return dinner_recipes
