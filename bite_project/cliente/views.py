from rest_framework import viewsets
from .models import UsuarioCustomizado, Categoria, ItemCardapio, Pedido
from .serializers import UsuarioCustomizadoSerializer, CategoriaSerializer, ItemCardapioSerializer, PedidoSerializer

class UsuarioCustomizadoViewSet(viewsets.ModelViewSet):
    queryset = UsuarioCustomizado.objects.all()
    serializer_class = UsuarioCustomizadoSerializer

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

class ItemCardapioViewSet(viewsets.ModelViewSet):
    queryset = ItemCardapio.objects.all()
    serializer_class = ItemCardapioSerializer

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer
