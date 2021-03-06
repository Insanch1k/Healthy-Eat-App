from .models import Diet, Weight
from recipes.models import Recipe
from django.core.mail import send_mail
from twilio.rest import Client
import datetime
from . import pswd


def get_weight_item(user, id):
    item = Weight.objects.get(user=user, id=id)
    return item


def get_my_weight(user):
    weight = Weight.objects.filter(user=user).order_by('created')
    return weight


def calculate_recipes_for_dinner_for_gain_weight_program(amount_of_carbs, amount_of_fat, amount_of_protein,
                                                         dinner_calories):
    dinner_recipes = Recipe.objects.filter(category__name='Dinner',
                                           calories__range=(dinner_calories - 100, dinner_calories + 50))
    return dinner_recipes


def calculate_recipes_for_lunch_for_gain_weight_program(amount_of_carbs, amount_of_fat, amount_of_protein,
                                                        lunch_calories):
    lunch_recipes = Recipe.objects.filter(category__name='Lunch',
                                          calories__range=(lunch_calories - 100, lunch_calories + 50))
    return lunch_recipes


def calculate_recipes_for_breakfast_for_gain_weight_program(amount_of_carbs, amount_of_fat, amount_of_protein,
                                                            breakfast_calories):
    breakfast_recipes = Recipe.objects.filter(category__name='Breakfast',
                                              calories__range=(breakfast_calories - 100, breakfast_calories + 50))

    return breakfast_recipes


def calculate_recipes_for_dinner_for_stable_weight_program(amount_of_carbs, amount_of_fat, amount_of_protein,
                                                           dinner_calories):
    dinner_recipes = Recipe.objects.filter(category__name='Dinner',
                                           calories__range=(dinner_calories - 50, dinner_calories + 100))
    return dinner_recipes


def calculate_recipes_for_breakfast_for_stable_weight_program(amount_of_carbs, amount_of_fat, amount_of_protein,
                                                              breakfast_calories):
    breakfast_recipes = Recipe.objects.filter(category__name='Breakfast',
                                              calories__range=(breakfast_calories - 100, breakfast_calories + 50))
    return breakfast_recipes


def calculate_recipes_for_lunch_for_stable_weight_program(amount_of_carbs, amount_of_fat, amount_of_protein,
                                                          lunch_calories):
    lunch_recipes = Recipe.objects.filter(category__name='Lunch',
                                          calories__range=(lunch_calories - 100, lunch_calories + 50))
    return lunch_recipes


'''Functions below for calculate amount of calories for each eating'''

def calculate_recipes_for_breakfast_for_lose_weight_program(amount_of_carbs, amount_of_fat, amount_of_protein,
                                                            breakfast_calories):
    breakfast_recipes = Recipe.objects.filter(category__name='Breakfast',
                                              calories__range=(breakfast_calories - 100, breakfast_calories + 50))

    return breakfast_recipes


def calculate_recipes_for_lunch_for_lose_program(amount_of_carbs, amount_of_fat, amount_of_protein,
                                                 lunch_calories):
    lunch_recipes = Recipe.objects.filter(category__name='Lunch',
                                          calories__range=(lunch_calories - 100, lunch_calories + 50))
    return lunch_recipes


def calculate_recipes_for_dinner_for_lose_program(amount_of_carbs, amount_of_fat, amount_of_protein,
                                                  dinner_calories):
    dinner_recipes = Recipe.objects.filter(category__name='Dinner',
                                           calories__range=(dinner_calories - 100, dinner_calories + 50))

    return dinner_recipes


# funkcja która liczy liczbę kalorii na śniadanie, jako argument przyjmuje wartość TDEE
def calculate_breakfast_calories(value):
    breakfast_calories = round(value * 0.25, 1)
    return breakfast_calories


# funkcja która liczy liczbę kalorii na obiad, jako argument przyjmuje wartość TDEE
def calculate_lunch_calories(value):
    lunch_calories = round(value * 0.45, 1)
    return lunch_calories


# funkcja która liczy liczbę kalorii na kolację, jako argument przyjmuje wartość TDEE
def calculate_dinner_calories(value):
    dinner_calories = round(value * 0.2, 1)
    return dinner_calories


# funkcja która liczy liczbę kalorii przekąsek, jako argument przyjmuje wartość TDEE
def calculate_snack_calories(value):
    snack_calories = round(value * 0.05, 1)
    return snack_calories


def send_confirm(new_program):
    message_to_broadcast = (f'Hello {new_program.subscriber.username}! You just subscribed on {new_program.title}.\n'
                            f'Breakfast at {new_program.breakfast_time}\n'
                            f'Lunch at {new_program.lunch_time}\n'
                            f'Dinner at {new_program.dinner_time}\n')
    account_sid = pswd.account_sid
    auth_token = pswd.auth_token
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=message_to_broadcast,
        from_='+12526240484',
        to=new_program.subscriber.profile.phone
    )
    print(message.sid)
