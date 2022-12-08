# from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('comanda/', views.comanda, name='comanda'),
    path('estoque/', views.estoque, name='estoque'),
    path('financeiro/', views.finaceiro, name='financeiro'),
    # path('veiculos/', views.VeiculoDetailView.as_view(), name='vieculo_view'),
    # path('veiculos/<int:id>',views.VeiculoDetailView.as_view(), name='view_items'),
]