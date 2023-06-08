from django.contrib import admin
from django.urls import path
from DApp.views import *
#from rest_framework import routers

# router = routers.DefaultRouter()
# router.register(r'products', ProductViewSet)

urlpatterns = [
   # path('products/get/', getProduct),
    path('products/create/',upload_product ),
    path('transactions/check/<transaction_hash>/',check_transaction),
    path('products/category/<subcatId>',get_products)
]