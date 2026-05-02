from django.contrib import admin

from .models import DietMeal, MealPlan, ProgramSubscription, SmsDeliveryLog, Weight

# Register your models here.


@admin.register(Weight)
class WeightAdmin(admin.ModelAdmin):
    list_display = ('user', 'weight', 'created')


@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'program_kind', 'target_calories', 'selection_algorithm')
    list_filter = ('program_kind', 'selection_algorithm')


@admin.register(DietMeal)
class DietMealAdmin(admin.ModelAdmin):
    list_display = ('meal_plan', 'meal_type', 'recipe', 'position', 'target_calories')
    list_filter = ('meal_type',)


@admin.register(ProgramSubscription)
class ProgramSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('subscriber', 'meal_plan', 'is_active', 'date_subscribe')
    list_filter = ('is_active', 'date_subscribe')


@admin.register(SmsDeliveryLog)
class SmsDeliveryLogAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'meal', 'sent_for_date', 'status', 'provider_sid', 'created')
    list_filter = ('meal', 'status', 'sent_for_date')
    search_fields = (
        'subscription__meal_plan__title',
        'subscription__subscriber__username',
        'provider_sid',
    )
