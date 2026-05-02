from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.http import require_POST

from recipes import selectors


def home(request):
    return render(request, 'health/home.html')


def recipe_list(request):
    recipe_queryset = selectors.recipes()
    paginator = Paginator(recipe_queryset, 6)
    page = request.GET.get('page')
    try:
        recipe_page = paginator.page(page)
    except PageNotAnInteger:
        recipe_page = paginator.page(1)
    except EmptyPage:
        recipe_page = paginator.page(paginator.num_pages)
    return render(
        request,
        'recipes/recipes_list.html',
        {
            'categories': selectors.categories(),
            'recipes': recipe_queryset,
            'recipe_list': recipe_page,
        },
    )


def recipe_detail(request, id, slug):
    recipe = selectors.get_recipe(recipe_id=id, slug=slug)
    is_favorite = (
        request.user.is_authenticated
        and recipe.favorite.filter(id=request.user.id).exists()
    )
    return render(request, 'recipes/detail.html', {'recipe': recipe, 'is_favorite': is_favorite})


@login_required
@require_POST
def favorite(request, id, slug):
    recipe = selectors.get_recipe(recipe_id=id, slug=slug)
    if recipe.favorite.filter(id=request.user.id).exists():
        recipe.favorite.remove(request.user)
    else:
        recipe.favorite.add(request.user)
    return HttpResponseRedirect(recipe.get_absolute_url())


def search(request):
    query = request.GET.get('q', '').strip()
    result = selectors.search_recipes(query=query)
    context = {
        'categories': selectors.categories(),
        'query': query,
        'result': result,
        'count': result.count(),
    }
    return render(request, 'recipes/recipes_list.html', context)


def recipes_by_category(request, category_slug):
    category, recipe_queryset = selectors.recipes_for_category_slug(category_slug=category_slug)
    context = {
        'by_category': category,
        'recipes': recipe_queryset,
        'result': recipe_queryset,
    }
    return render(request, 'recipes/recipes_by_category.html', context)


def search_calories(request, category_slug):
    category, category_recipes = selectors.recipes_for_category_slug(category_slug=category_slug)
    query_calories = request.GET.get('calories', '').strip()
    result = category_recipes
    if query_calories:
        try:
            calories = int(query_calories)
        except ValueError:
            messages.error(request, 'Calories must be a number.')
        else:
            _, result = selectors.recipes_for_category_calories(
                category_slug=category_slug,
                calories=calories,
            )
    context = {
        'by_category': category,
        'recipes': category_recipes if not query_calories else None,
        'query': query_calories,
        'result': result,
        'count': result.count(),
    }
    return render(request, 'recipes/recipes_by_category.html', context)
