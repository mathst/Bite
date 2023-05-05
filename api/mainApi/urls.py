# from django.conf.urls import url
from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('comanda/', views.comanda, name='comanda'),
    path('estoque/', views.estoque, name='estoque'),
    path('financeiro/', views.finaceiro, name='financeiro'),
    path('cardapio/', views.cardapio, name='cardapio'),
    path('', views.login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='accounts/logout.html'), name='logout'),
    # path('google-authenticate/', views.authenticate_with_google, name='google_authenticate'),
    path('auth/', include('social_django.urls', namespace='social')),
    # path('reset/', views.reset),
    # path('', views.login, name='login'),
    # path('logout/', views.logout, name='logout'),

]