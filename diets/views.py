from django.shortcuts import render, redirect
<<<<<<< HEAD
=======
from .models import Weight, Diet
>>>>>>> a2718985b2ce9faa27afda783f776e91372ef8bc
from .forms import WeightForm
import datetime
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .diets_services import *


<<<<<<< HEAD
# Create your views here.
=======
>>>>>>> a2718985b2ce9faa27afda783f776e91372ef8bc


@login_required()
def show_progress(request):
    
    '''That function show for every user their weight progress in profile like graph'''
    
    user = request.user
    my_weight = get_my_weight(user)
    # my_weight = Weight.objects.filter(user=user).order_by('created')
    firstt = None
    lastt = None
    res = None
    new_res = None
    dt = datetime.datetime.today()
    fd = None
    if my_weight:
        firstt = my_weight.reverse()[0]
        lastt = my_weight[0]
        res = float(firstt.weight) - float(lastt.weight)
        new_res = round(res, 2)
        fd = dt.day
        if request.method == 'POST':
            weight_form = WeightForm(request.POST)
            if firstt.created.day == dt.day:
                messages.warning(request, 'Today you already added your weight')
                return redirect('diets:weight')
            else:
                if weight_form.is_valid():
                    new_weight = weight_form.save(commit=False)
                    new_weight.user = request.user
                    new_weight.save()
        else:
            weight_form = WeightForm()
    else:
        if request.method == 'POST':
            weight_form = WeightForm(request.POST)
            if weight_form.is_valid():
                new_weight = weight_form.save(commit=False)
                new_weight.user = request.user
                new_weight.save()
            return redirect('diets:weight')
        else:
            weight_form = WeightForm()
    context = {
        'weight_form': weight_form,
        'weight': my_weight,
        'last': lastt,
        'first': firstt,
        'res': new_res,
        'day': dt,
        'fd': dt
    }
    return render(request, 'weight/weight_progress.html', context)


def delete_weight(request, id):
    
    '''Function for deleting weight from our weight history'''
    
    user = request.user
    item = get_weight_item(user, id)
    # item = Weight.objects.get(user=user, id=id)
    if request.method == 'POST':
        item.delete()
        return redirect('diets:weight')
    return render(request, 'weight/weight_delete.html', {'weight_for_delete': item})


def calculator(request):
    
    #bmr - is the total number of calories that your body needs to perform basic, life-sustaining functions.
    
    #tdee - is an estimation of how many calories you burn per day when exercise is taken into account.
    
    '''Function for calculating bmr and tdee'''
    
    if request.method == 'POST':
        activity = request.POST['drop']
        sex = request.POST['sex']
        height = request.POST['height']
        weight = request.POST['weight']
        age = request.POST['age']
        bmi = round(float(weight) / (float(height) ** 2) * 10000, 2)
        if sex == 'Woman':
            bmr = int(655 + (9.6 * float(weight)) + (1.8 * float(height)) - 4.7 * int(age))
            tdee = int(float(activity) * bmr)
            tdee_lose_weight = int(tdee - tdee * 0.15)
            tdee_gain_weight = int(tdee + tdee * 0.15)
        elif sex == 'Man':
            bmr = int(66 + (13.7 * float(weight)) + (5 * float(height)) - 6.8 * int(age))
            tdee = int(float(activity) * bmr)
            tdee_lose_weight = int(tdee - tdee * 0.15)
            tdee_gain_weight = int(tdee + tdee * 0.15)
        return render(request, 'res_for_calculator.html', {'activity': activity,
                                                           'tdee': tdee,
                                                           'tdee_plus': tdee + 100,
                                                           'sex': sex,
                                                           'bmr': bmr,
                                                           'a': activity,
                                                           'tdee_lose_weight': tdee_lose_weight,
                                                           'tdee_lose_weight_plus': tdee_lose_weight + 100,
                                                           'tdee_gain_weight': tdee_gain_weight,
                                                           'tdee_gain_weight_plus': tdee_gain_weight + 100,
                                                           'bmi': bmi
                                                           })
    return render(request, 'calculator.html')


<<<<<<< HEAD
'''Function for calculating gain weight program'''


def gain_weight_program(request, value):
    # calculate amount of calories for all day
    value += (value * 0.15)
    # we use functions from diets_services.py for calculating breakfast, lunch, dinner and snack calories
    breakfast_calories = calculate_breakfast_calories(value)
    lunch_calories = calculate_lunch_calories(value)
    dinner_calories = calculate_dinner_calories(value)
    lunch_calories2 = calculate_lunch_calories(value)
    snack_calories = calculate_snack_calories(value)
    snack_calories2 = calculate_snack_calories(value)
    # we calculate amount carbs, protein and  fat for all day
    amount_of_carbs = (value * 0.55) / 4
    amount_of_fat = (value * 0.2) / 9
    amount_of_protein = (value * 0.25) / 4

    # checking if there is a need to split lunch in 2 times
    if lunch_calories > 1000:
        lunch_calories /= 2

    # using functions from diets_service.py for calculate breakfast, lunch and dinner recipes
    breakfast_recipes = calculate_recipes_for_breakfast_for_gain_weight_program(amount_of_carbs, amount_of_fat,
                                                                                amount_of_protein,
                                                                                breakfast_calories)
    lunch_recipes = calculate_recipes_for_lunch_for_gain_weight_program(amount_of_carbs, amount_of_fat,
                                                                        amount_of_protein,
                                                                        lunch_calories)
    dinner_recipes = calculate_recipes_for_dinner_for_gain_weight_program(amount_of_carbs, amount_of_fat,
                                                                          amount_of_protein,
                                                                          dinner_calories)
    # checking user is subscribe or not
    is_subscribe = False
    gain_program = Diet.objects.filter(subscriber=request.user)
    if gain_program:
        is_subscribe = True

    # process of subscription on program
    if request.method == 'POST':
        breakfast_time = request.POST['breakfast_time']
        lunch_time = request.POST['lunch_time']
        dinner_time = request.POST['dinner_time']

        new_program = Diet.objects.create(title='GainWeight',
                                          slug='gainweightfor' + request.user.username,
                                          subscriber=request.user,
                                          description_of_diet='descriptionAnton',
                                          breakfast_time=breakfast_time,
                                          lunch_time=lunch_time,
                                          dinner_time=dinner_time)
        new_program.save()
        for i in dinner_recipes:
            new_program.dinner.add(i.id)
        for b in breakfast_recipes:
            new_program.breakfast.add(b.id)
        for lunch in lunch_recipes:
            new_program.lunch.add(lunch.id)
        # send sms with short info about program
        # send_confirm(new_program)
        return redirect('hairstyle:my_profile')
    context = {
        'breakfast_recipes': breakfast_recipes,
        'lunch_recipes': lunch_recipes,
        'dinner_recipes': dinner_recipes,
        'lunch_calories2': lunch_calories2,
        'lunch_calories': lunch_calories,
        'breakfast_calories': breakfast_calories,
        'dinner_calories': dinner_calories,
        'is_subscribe': is_subscribe,
        'amount_of_protein_for_breakfast': round(amount_of_protein * 0.3, 1),
        'amount_of_protein_for_lunch': round(amount_of_protein * 0.4, 1),
        'amount_of_protein_for_dinner': round(amount_of_protein * 0.3, 1),
        'amount_of_fat_for_breakfast': round(amount_of_fat * 0.4, 1),
        'amount_of_fat_for_lunch': round(amount_of_fat * 0.4, 1),
        'amount_of_fat_for_dinner': round(amount_of_fat * 0.2, 1),
        'amount_of_carbs_for_breakfast': round(amount_of_carbs * 0.4, 1),
        'amount_of_carbs_for_lunch': round(amount_of_carbs * 0.4, 1),
        'amount_of_carbs_for_dinner': round(amount_of_carbs * 0.2, 1),
        'snack_calories': snack_calories,
        'snack_calories2': snack_calories2,
        'value': value
    }
    return render(request, 'gain_program.html', context)


def stable_weight_program(request, value):
    amount_of_carbs = (value * 0.5) / 4
    amount_of_fat = (value * 0.2) / 9
    amount_of_protein = (value * 0.3) / 4
    breakfast_calories = calculate_breakfast_calories(value)
    lunch_calories = calculate_lunch_calories(value)
    lunch_calories2 = calculate_lunch_calories(value)
    dinner_calories = calculate_dinner_calories(value)
    snack_calories = calculate_snack_calories(value)
    snack2_calories = calculate_snack_calories(value)
    if lunch_calories > 900:
        lunch_calories /= 2
    # calculate recipes for user
    breakfast_recipes = calculate_recipes_for_breakfast_for_stable_weight_program(amount_of_carbs, amount_of_fat,
                                                                                  amount_of_protein,
                                                                                  breakfast_calories)

    lunch_recipes = calculate_recipes_for_breakfast_for_stable_weight_program(amount_of_carbs, amount_of_fat,
                                                                              amount_of_protein,
                                                                              lunch_calories)

    dinner_recipes = calculate_recipes_for_dinner_for_stable_weight_program(amount_of_carbs, amount_of_fat,
                                                                            amount_of_protein,
                                                                            dinner_calories)
=======
def stable_weight_program(request, value, amount_of_breakfast, amount_of_lunch):
    
    '''Function for showing program "stable weight" for every users  for their tdee and bmr'''
    
    dinner_recipes = None
    breakfast_recipes = None
    lunch_recipes = None
    breakfast_calories = None
    lunch_calories = None
    dinner_calories = None
    if amount_of_lunch == 1:
        breakfast_calories = value / 4
        lunch_calories = (value - breakfast_calories) / 2
        dinner_calories = (value - breakfast_calories) / 2
        dinner_recipes = Recipe.objects.filter(category__name='Dinner',
                                               calories__range=(dinner_calories - 20, dinner_calories + 25))
        lunch_recipes = Recipe.objects.filter(category__name='Vegan',
                                              calories__range=(lunch_calories - 20, lunch_calories + 25))
        breakfast_recipes = Recipe.objects.filter(category__name='Breakfast',
                                                  calories__range=(breakfast_calories - 20, breakfast_calories + 20))
    if amount_of_lunch == 2:
        breakfast_calories = value / 4
        lunch_calories = (value - breakfast_calories) / 4
        dinner_calories = (value - breakfast_calories) / 2
        dinner_recipes = Recipe.objects.filter(category__name='Dinner',
                                               calories__range=(dinner_calories - 20, dinner_calories + 25))
        lunch_recipes = Recipe.objects.filter(category__name='Vegan',
                                              calories__range=(lunch_calories - 20, lunch_calories + 25))
        breakfast_recipes = Recipe.objects.filter(category__name='Breakfast',
                                                  calories__range=(breakfast_calories - 20, breakfast_calories + 20))
>>>>>>> a2718985b2ce9faa27afda783f776e91372ef8bc

    is_subscribe = False
    stable_program = Diet.objects.filter(subscriber=request.user)
    if stable_program:
        is_subscribe = True
    if request.method == 'POST':
<<<<<<< HEAD
        breakfast_time = request.POST['breakfast_time']
        lunch_time = request.POST['lunch_time']
        dinner_time = request.POST['dinner_time']

        new_program = Diet.objects.create(title='StableWeight',
                                          slug='stableweightfor' + request.user.username,
                                          subscriber=request.user,
                                          description_of_diet='descriptionAnton',
                                          breakfast_time=breakfast_time,
                                          lunch_time=lunch_time,
                                          dinner_time=dinner_time)
        new_program.save()
        for i in dinner_recipes:
            new_program.dinner.add(i.id)
        for b in breakfast_recipes:
            new_program.breakfast.add(b.id)
        for lunch in lunch_recipes:
            new_program.lunch.add(lunch.id)
        # send_confirm(new_program)
        # create new record in database with recipes for every user
=======
        if is_subscribe:
            return HttpResponse(
                '<h1>You already have this program</h1>')
        else:
            new_program = Diet.objects.create(title='StableWeight',
                                              slug='stableweightfor' + request.user.username,
                                              subscriber=request.user,
                                              description_of_diet='descriptionAnton',
                                              breakfast_time='10:00:00',
                                              lunch_time='15:00:00',
                                              dinner_time='20:00:00')
            new_program.save()
            for i in dinner_recipes:
                new_program.dinner.add(i.id)
            for b in breakfast_recipes:
                new_program.breakfast.add(b.id)
            for lunch in lunch_recipes:
                new_program.lunch.add(lunch.id)
            # create new record in database with recipes for every user
>>>>>>> a2718985b2ce9faa27afda783f776e91372ef8bc
        return redirect('hairstyle:my_profile')
    context = {
        'value': value,
        'is_subscribe': is_subscribe,
        'breakfast_calories': breakfast_calories,
        'lunch_calories': lunch_calories,
        'dinner_calories': dinner_calories,
        'amount_of_protein_for_breakfast': round(amount_of_protein * 0.3, 1),
        'amount_of_protein_for_lunch': round(amount_of_protein * 0.4, 1),
        'amount_of_protein_for_dinner': round(amount_of_protein * 0.3, 1),
        'amount_of_fat_for_breakfast': round(amount_of_fat * 0.4, 1),
        'amount_of_fat_for_lunch': round(amount_of_fat * 0.4, 1),
        'amount_of_fat_for_dinner': round(amount_of_fat * 0.2, 1),
        'breakfast_recipes': breakfast_recipes,
        'amount_of_carbs_for_breakfast': round(amount_of_carbs * 0.4, 1),
        'amount_of_carbs_for_lunch': round(amount_of_carbs * 0.4, 1),
        'amount_of_carbs_for_dinner': round(amount_of_carbs * 0.2, 1),
        'dinner_recipes': dinner_recipes,
        'lunch_recipes': lunch_recipes,
        'snack_calories': snack_calories,
        'snack2_calories': snack2_calories,
        'lunch_calories2': lunch_calories2,
    }
    return render(request, 'stable_program.html', context)


<<<<<<< HEAD
def lose_weight(request, value):
=======
def lose_weight(request, value, amount_of_lunch, amount_of_breakfast):
    
    '''Function for showing program "lose weight" for every users  for their tdee and bmr'''
    
>>>>>>> a2718985b2ce9faa27afda783f776e91372ef8bc
    value -= (value * 0.15)
    amount_of_carbs = (value * 0.45) / 4
    amount_of_fat = (value * 0.2) / 9
    amount_of_protein = (value * 0.35) / 4
    breakfast_calories = calculate_dinner_calories(value)
    lunch_calories = calculate_lunch_calories(value)
    lunch_calories2 = calculate_lunch_calories(value)
    dinner_calories = calculate_dinner_calories(value)
    snack_calories = calculate_snack_calories(value)
    snack2_calories = calculate_snack_calories(value)
    breakfast_time = None
    if lunch_calories > 900:
        lunch_calories /= 2
    breakfast_recipes = calculate_recipes_for_breakfast_for_lose_weight_program(
        amount_of_carbs,
        amount_of_fat,
        amount_of_protein,
        breakfast_calories)
    lunch_recipes = calculate_recipes_for_lunch_for_lose_program(amount_of_carbs,
                                                                 amount_of_fat,
                                                                 amount_of_protein,
                                                                 lunch_calories)
    dinner_recipes = calculate_recipes_for_dinner_for_lose_program(amount_of_carbs,
                                                                   amount_of_fat,
                                                                   amount_of_protein,
                                                                   dinner_calories)
    is_subscribe = False
    lose_program = Diet.objects.filter(subscriber=request.user)
    if lose_program:
        is_subscribe = True
    if request.method == 'POST':
        breakfast_time = request.POST['breakfast_time']
        lunch_time = request.POST['lunch_time']
        dinner_time = request.POST['dinner_time']
        print(dinner_time)
        new_program = Diet.objects.create(title='LoseWeight',
                                          slug='loseweightfor' + request.user.username,
                                          subscriber=request.user,
                                          description_of_diet='descriptionAnton',
                                          breakfast_time=breakfast_time,
                                          lunch_time=lunch_time,
                                          dinner_time=dinner_time)
        new_program.save()
        for i in dinner_recipes:
            new_program.dinner.add(i.id)
        for b in breakfast_recipes:
            new_program.breakfast.add(b.id)
        for lunch in lunch_recipes:
            new_program.lunch.add(lunch.id)
        # send_confirm(new_program)
        # create new record in database with recipes for every user
        return redirect('hairstyle:my_profile')

    context = {
        'value': value,
        'is_subscribe': is_subscribe,
        'breakfast_calories': breakfast_calories,
        'lunch_calories': lunch_calories,
        'dinner_calories': dinner_calories,
        'amount_of_protein_for_breakfast': round(amount_of_protein * 0.3, 1),
        'amount_of_protein_for_lunch': round(amount_of_protein * 0.4, 1),
        'amount_of_protein_for_dinner': round(amount_of_protein * 0.3, 1),
        'amount_of_fat_for_breakfast': round(amount_of_fat * 0.4, 1),
        'amount_of_fat_for_lunch': round(amount_of_fat * 0.4, 1),
        'amount_of_fat_for_dinner': round(amount_of_fat * 0.2, 1),
        'breakfast_recipes': breakfast_recipes,
        'amount_of_carbs_for_breakfast': round(amount_of_carbs * 0.4, 1),
        'amount_of_carbs_for_lunch': round(amount_of_carbs * 0.4, 1),
        'amount_of_carbs_for_dinner': round(amount_of_carbs * 0.2, 1),
        'dinner_recipes': dinner_recipes,
        'lunch_recipes': lunch_recipes,
        'snack_calories': snack_calories,
        'snack2_calories': snack2_calories,
        'lunch_calories2': lunch_calories2,
    }
    return render(request, 'lose_program.html', context)


def my_program(request):
    
    '''Function for showing persona program for user in profile'''
    
    my_diet = Diet.objects.get(subscriber=request.user, is_active=True)
    times = [my_diet.breakfast_time, my_diet.lunch_time, my_diet.dinner_time]
    time_now = datetime.datetime.today().time()

    if request.method == 'POST':
        my_diet.delete()
        return redirect('hairstyle:my_profile')

    context = {
        'my_diet': my_diet,
        'time': time_now,
        'time1': times[0],

    }

    return render(request, 'my_program.html', context)


def settings_for_myprogram(request):
    
    '''Settings of personal program for user, opportunity unsub from program'''
    
    program = Diet.objects.get(subscriber=request.user)
    if request.method == 'POST':
        program.delete()  # delete diet for user
        return redirect('hairstyle:my_profile')

    context = {
        'program': program,
    }
    return render(request, 'settings_for_my_program.html', context)
