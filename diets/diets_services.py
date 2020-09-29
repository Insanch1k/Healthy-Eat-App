from .models import Diet, Weight
from hairstyle.models import Recipe
from django.core.mail import send_mail
from twilio.rest import Client
import datetime


def get_weight_item(user, id):
    item = Weight.objects.get(user=user, id=id)
    return item


def get_my_weight(user):
    weight = Weight.objects.filter(user=user).order_by('created')
    return weight


def calculate_recipes_for_dinner_for_gain_weight_program(amount_of_carbs, amount_of_fat, amount_of_protein,
                                                         dinner_calories):
    dinner_recipes = Recipe.objects.filter(category__name='Dinner',
                                           calories__range=(dinner_calories - 50, dinner_calories + 100))
    return dinner_recipes


def calculate_recipes_for_lunch_for_gain_weight_program(amount_of_carbs, amount_of_fat, amount_of_protein,
                                                        lunch_calories):
    lunch_recipes = Recipe.objects.filter(category__name='Lunch',
                                          calories__range=(lunch_calories - 50, lunch_calories + 100))
    return lunch_recipes


def calculate_recipes_for_breakfast_for_gain_weight_program(amount_of_carbs, amount_of_fat, amount_of_protein,
                                                            breakfast_calories):
    breakfast_recipes = Recipe.objects.filter(category__name='Breakfast',
                                              calories__range=(breakfast_calories - 50, breakfast_calories + 100))

    return breakfast_recipes


def calculate_recipes_for_dinner_for_stable_weight_program(amount_of_carbs, amount_of_fat, amount_of_protein,
                                                           dinner_calories):
    dinner_recipes = Recipe.objects.filter(category__name='Dinner',
                                           calories__range=(dinner_calories - 70, dinner_calories + 70))
    return dinner_recipes


def calculate_recipes_for_breakfast_for_stable_weight_program(amount_of_carbs, amount_of_fat, amount_of_protein,
                                                              breakfast_calories):
    breakfast_recipes = Recipe.objects.filter(category__name='Breakfast', calories__range=(
        breakfast_calories - 60, breakfast_calories + 60))
    return breakfast_recipes


def calculate_recipes_for_lunch_for_stable_weight_program(amount_of_carbs, amount_of_fat, amount_of_protein,
                                                          lunch_calories):
    lunch_recipes = Recipe.objects.filter(category__name='Dinner',
                                          calories__range=(lunch_calories - 70, lunch_calories + 70))


def calculate_recipes_for_breakfast_for_lose_weight_program(amount_of_carbs, amount_of_fat, amount_of_protein,
                                                            breakfast_calories):
    breakfast_recipes = Recipe.objects.filter(category__name='Breakfast',
                                              calories__range=(breakfast_calories - 50, breakfast_calories + 50))

    return breakfast_recipes


def calculate_recipes_for_lunch_for_lose_program(amount_of_carbs, amount_of_fat, amount_of_protein,
                                                 lunch_calories):
    lunch_recipes = Recipe.objects.filter(calories__range=(lunch_calories - 50, lunch_calories + 50))
    return lunch_recipes


def calculate_recipes_for_dinner_for_lose_program(amount_of_carbs, amount_of_fat, amount_of_protein,
                                                  dinner_calories):
    dinner_recipes = Recipe.objects.filter(category__name='Dinner',
                                           calories__range=(dinner_calories - 50, dinner_calories + 50))

    return dinner_recipes


def calculate_breakfast_calories(value):
    breakfast_calories = round(value * 0.25, 1)
    return breakfast_calories


def calculate_lunch_calories(value):
    lunch_calories = round(value * 0.45, 1)
    return lunch_calories


def calculate_dinner_calories(value):
    dinner_calories = round(value * 0.2, 1)
    return dinner_calories


def calculate_snack_calories(value):
    snack_calories = round(value * 0.05, 1)
    return snack_calories


def send_confirm(new_program):
    message_to_broadcast = (f'Hello {new_program.subscriber.username}! You just subscribed on {new_program.title}.\n'
                            f'Breakfast at {new_program.breakfast_time}\n'
                            f'Lunch at {new_program.lunch_time}\n'
                            f'Dinner at {new_program.dinner_time}\n')
    account_sid = 'AC43ea34bd786650eb056e24cc007fd8a6'
    auth_token = '992283c8ea1deed10c5f47c61bf69e83'
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=message_to_broadcast,
        from_='+12526240484',
        to=new_program.subscriber.profile.phone
    )
    print(message.sid)
