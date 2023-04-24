# from django.conf.urls import url
from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('comanda/', views.comanda, name='comanda'),
    path('estoque/', views.estoque, name='estoque'),
    path('financeiro/', views.finaceiro, name='financeiro'),
    path('', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='accounts/logout.html'), name='logout'),
    path('signup/', views.signup_cliente, name='signup_cliente'),
    path('signup/funcionario/', views.signup_funcionario, name='signup_funcionario'),
    path('signup/administrador/', views.signup_administrador, name='signup_administrador'),
    path('google-authenticate/', views.authenticate_with_google, name='google_authenticate'),
    path('auth/', include('social_django.urls', namespace='social')),
    path('index/', views.index, name='index')
    # path('reset/', views.reset),
    # path('', views.login, name='login'),
    # path('logout/', views.logout, name='logout'),

]