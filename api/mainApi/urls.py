# from django.conf.urls import url
from django.urls import path, include
from .views import *
from . import views

urlpatterns = [
    # path('comanda/', views.comanda, name='comanda'),
    # path('estoque/', views.estoque, name='estoque'),
    # path('financeiro/', views.finaceiro, name='financeiro'),
    path('', views.signIn),
    path('postsignIn/', views.postsignIn),
    path('signUp/', views.signUp, name="signup"),
    path('logout/', views.logout, name="log"),
    path('postsignUp/', views.postsignUp),
    # path('reset/', views.reset),
    # path('postReset/', views.postReset),

]