from django.contrib import admin
from .models import AllData, FinancialData, InformativeData, InvestorInfo, MainData, CurrencyPrice, Area, CadastralPhoto, Category, Currency, ObjectPhoto, ProductPhoto

admin.site.register(FinancialData)
admin.site.register(InformativeData)
admin.site.register(InvestorInfo)
admin.site.register(MainData)
admin.site.register(AllData)
admin.site.register(CurrencyPrice)
admin.site.register(Currency)
admin.site.register(Area)
admin.site.register(CadastralPhoto)
admin.site.register(Category)
admin.site.register(ObjectPhoto)
admin.site.register(ProductPhoto)

