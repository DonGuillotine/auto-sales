from django.contrib import admin
from .models import Category

# Register your models here.


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'url': ('category_name',)}
    list_display = ('category_name', 'url')


admin.site.register(Category, CategoryAdmin)
