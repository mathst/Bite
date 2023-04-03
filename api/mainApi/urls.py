# from django.conf.urls import url
from django.urls import path, include
from .views import *
from . import views

urlpatterns = [
    # path('comanda/', views.comanda, name='comanda'),
    # path('estoque/', views.estoque, name='estoque'),
    # path('financeiro/', views.finaceiro, name='financeiro'),
    path('', views.signin),
    path('postsignIn/', views.postsignin),
    path('signUp/', views.signup, name="signup"),
    path('logout/', views.logout, name="log"),
    path('postsignUp/', views.postsignup),
    path('reset/', views.reset),
    path('postReset/', views.postReset),

]