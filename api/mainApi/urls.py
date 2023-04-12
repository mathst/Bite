# from django.conf.urls import url
from django.urls import path, include
from . import views
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('comanda/', views.comanda, name='comanda'),
    path('estoque/', views.estoque, name='estoque'),
    path('financeiro/', views.finaceiro, name='financeiro'),
    path('', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='accounts/logout.html'), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('signup/cliente/', views.signup_cliente, name='cliente_signup'),
    path('signup/funcionario/', views.funcionario_signup, name='funcionario_signup'),
    path('signup/administrador/', views.administrador_signup, name='administrador_signup'),
    path('google-authenticate/', views.authenticate_with_google, name='google_authenticate'),
    path('auth/', include('social_django.urls', namespace='social')),
    # path('reset/', views.reset),

]