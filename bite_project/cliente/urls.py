from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UsuarioCustomizadoViewSet, CategoriaViewSet, ItemCardapioViewSet, PedidoViewSet

router = DefaultRouter()
router.register(r'usuarios', UsuarioCustomizadoViewSet)
router.register(r'categorias', CategoriaViewSet)
router.register(r'itens-cardapio', ItemCardapioViewSet)
router.register(r'pedidos', PedidoViewSet)

urlpatterns = [
    path('api/', include(router.urls)),  # Use uma URL base adequada para a sua API
]
