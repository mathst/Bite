
from django.urls import path, include
from mainApi import urls as main_urls

urlpatterns = [
    path('', include(main_urls)),
]