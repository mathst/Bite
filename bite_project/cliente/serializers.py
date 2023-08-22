from rest_framework import serializers
from .models import UsuarioCustomizado, Categoria, ItemCardapio, Pedido

class UsuarioCustomizadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsuarioCustomizado
        fields = '__all__'

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'

class ItemCardapioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCardapio
        fields = '__all__'

class PedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = '__all__'
