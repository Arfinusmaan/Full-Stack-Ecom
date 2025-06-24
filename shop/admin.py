from django.contrib import admin
from .models import *

# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'image', 'description')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product)  # Register Product with the custom admin settings
admin.site.register(Cart)
admin.site.register(Favourite)
admin.site.register(Order)
admin.site.register(OrderItem)
