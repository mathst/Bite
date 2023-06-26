# from django.conf.urls import url
from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('cardapio/', views.cardapio, name='cardapio'),
    path('carrinho/', views.carrinho, name='carrinho'),
    path('pedidos/', views.pedidos, name='pedidos'),
    path('estoque/', views.estoque, name='estoque'),
    path('', views.login, name='login'),
    path('finalizar_pagamento/', views.finalizar_pagamento, name='finalizar_pagamento'),
    path('cadastro/', views.cadastrar_usuario_cli, name='cadastrar_usuario_cli'),
    path('login_google/', views.login_google, name='login_google'),
    path('auth/', include('social_django.urls', namespace='social')),
    path('reset/', views.reset,name='reset'),
    path('logout/', views.logout, name='logout'),

]