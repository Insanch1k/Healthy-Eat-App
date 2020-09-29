from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from .forms import UserRegistrationForm, EditUser, EditProfile
from .models import Category, Recipe, Profile
from diets.models import Diet
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, 'barbershop/home.html')


def example(request):
    return render(request, 'barbershop/example.html')


def new_template(request):
    return render(request, 'barbershop/home.html')


class StartView(TemplateView):
    template_name = 'barbershop/start_page.html'


class AboutView(TemplateView):
    template_name = 'barbershop/about.html'


@login_required
def edit(request):  # funkcja realizujaca edycje profilu
    if request.method == 'POST':
        user_form = EditUser(instance=request.user, data=request.POST)  # wyswietlenie danych uzytkownika
        profile_form = EditProfile(instance=request.user.profile, data=request.POST, files=request.FILES)

        if user_form.is_valid() and profile_form.is_valid():  # jesli dane sa validowane
            profile_form.save()
            user_form.save()  # zmieniamy na nowe
            messages.success(request, "Successfully")  # wiadomosc ze dane zostaly zmienione
        else:
            messages.error(request, "Fail")  # wiadomosc ze nie zostaly
    else:
        user_form = EditUser(instance=request.user)  # wyswieltenie pustej formy
        profile_form = EditProfile(instance=request.user.profile)
    return render(request, 'profile/edit.html', {'user_form': user_form,
                                                 'profile_form': profile_form})  # przekazyjemy dane w HTML


@login_required
def my_profile(request):
    program = None
    try:
        program = Diet.objects.filter(subscriber=request.user)
    except NotImplemented:
        HttpResponse("Error")
    finally:
        user = request.user
        favorite_recipe = user.favorite.all()
        my_programs = Diet.objects.filter(subscriber=request.user)
        sweet = favorite_recipe.filter(category__name='Sweet')
        dinner = favorite_recipe.filter(category__name='Dinner')
        breakfast = favorite_recipe.filter(category__name='Breakfast')
        vegan = favorite_recipe.filter(category__name='Vegan')
        number = request.user.profile.phone

        return render(request, 'profile/my_profile.html', {'favorite_recipe': favorite_recipe,
                                                           'Sweet': sweet,
                                                           'dinner': dinner,
                                                           'breakfast': breakfast,
                                                           'vegan': vegan,
                                                           'my_programs': my_programs,
                                                           'number': number,
                                                           'program': program
                                                           })


def register(request):  # funkcja rejestracji
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)  # wyswietlamy forme do rejestracji
        profile_form = EditProfile(request.POST)
        if user_form.is_valid() and profile_form.is_valid():  # jesli forma validowana
            new_user = user_form.save(commit=False)  # bierzemy dane nowego uzytkownika ale nie zachowujemy w bazie
            new_user.set_password(user_form.cleaned_data['password'])  # haslo dla uzytkownika
            new_user.save()  # zachowujemy  w bazie
            # profile = profile_form.save(commit=False)
            # profile_form.user = new_user
            # profile.save()
            profile = profile_form.save(commit=False)
            profile.user = new_user
            profile.save()
            # profile_form.user = new_user
            # profile_form.save()
            login(request, new_user,
                  backend='django.contrib.auth.backends.ModelBackend')  # logujemy automatycznie uzytkownika na stronie

            return render(request, 'barbershop/about.html',
                          {'new_user': new_user})  # przekazyjemy dane w HTML
    else:
        user_form = UserRegistrationForm()  # pusta forma
        profile_form = EditProfile()
    return render(request, 'registration/register.html', {'user_form': user_form,
                                                          'profile_form': profile_form
                                                          })  # przekazyjemy dane w HTML



def recipe_list(request):
    categories = Category.objects.all()
    recipes = Recipe.objects.all()
    r = recipes.count()
    paginator = Paginator(recipes, 3)
    page = request.GET.get('page')
    recipe_list = None
    try:
        recipe_list = paginator.page(page)
    except PageNotAnInteger:
        recipe_list = paginator.page(1)
    except EmptyPage:
        recipe_list = paginator.page(paginator.num_pages)
    return render(request, 'recipes/recipes_list.html', {'categories': categories,
                                                         'recipes': recipes,
                                                         'recipe_list': recipe_list
                                                         })


def recipe_detail(request, id, slug):
    recipe = get_object_or_404(Recipe, id=id, slug=slug)
    is_favorite = False
    if recipe.favorite.filter(id=request.user.id).exists():
        is_favorite = True
    return render(request, 'recipes/detail.html', {'recipe': recipe,
                                                   'is_favorite': is_favorite})


def favorite(request, id, slug):
    recipe = get_object_or_404(Recipe, id=id, slug=slug)
    if recipe.favorite.filter(id=request.user.id).exists():
        recipe.favorite.remove(request.user)
    else:
        recipe.favorite.add(request.user)
    return HttpResponseRedirect(recipe.get_absolute_url())


def search(request):
    query = request.GET.get('q', '')

    if query:
        result = Recipe.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))

    else:
        result = Recipe.objects.all()
    count_of_result = len(result)
    context = {
        'query': query,
        'result': result,
        'count': count_of_result
    }
    return render(request, 'recipes/recipes_list.html', context)


def recipes_by_category(request, category_slug):
    by_category = get_object_or_404(Category, slug=category_slug)
    recipes = Recipe.objects.filter(category=by_category)
    query_calories = request.GET.get('calories')

    if query_calories:
        result = recipes.filter(Q(title__icontains=query_calories))
    else:
        result = recipes.all()
    count_of_result = len(result)
    context = {
        'by_category': by_category,
        'recipes': recipes,
        'result': result,
    }
    return render(request, 'recipes/recipes_by_category.html', context)


def search_calories(request, category_slug):
    by_category = get_object_or_404(Category, slug=category_slug)
    recipes = Recipe.objects.filter(category=by_category)
    query_calories = request.GET.get('calories', '')
    q = int(query_calories)
    if query_calories:
        result = recipes.filter(calories__range=(q - 50, q + 50))
    else:
        result = recipes.all()
    count_of_result = len(result)
    context = {
        'by_category': by_category,
        'query': query_calories,
        'result': result,
        'count': count_of_result
    }
    return render(request, 'recipes/recipes_by_category.html', context)
