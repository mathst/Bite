# from django.conf.urls import url
from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('cardapio/', views.cardapio, name='cardapio'),
    path('carrinho/', views.carrinho, name='carrinho'),
    path('pedidos/', views.pedidos, name='pedidos'),
    path('estoque/', views.estoque, name='estoque'),
    path('', views.login_view, name='login'),
    path('finalizar_pagamento/', views.finalizar_pagamento, name='finalizar_pagamento'),
    path('cadastro/', views.signup_view, name='signup'),
    # path('login_google/', views.login_google, name='login_google'),
    path('auth/', include('social_django.urls', namespace='social')),
    path('reset-password/', views.client_reset_password_request_view, name='client_reset_password_request'),
    path('reset-password/<uidb64>/<token>/', views.client_reset_password_view, name='client_reset_password'),
    path('logout/', views.logout, name='logout'),

]