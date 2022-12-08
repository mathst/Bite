# from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # path('veiculos/', views.VeiculoDetailView.as_view(), name='vieculo_view'),
    # path('veiculos/<int:id>',views.VeiculoDetailView.as_view(), name='view_items'),
]