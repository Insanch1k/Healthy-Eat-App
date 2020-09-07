from django.contrib import admin
from .models import Weight, Diet


# Register your models here.


@admin.register(Weight)
class WeightAdmin(admin.ModelAdmin):
    list_display = ('user', 'weight', 'created')


@admin.register(Diet)
class LoseWeightAdmin(admin.ModelAdmin):
    list_display = ('title', )