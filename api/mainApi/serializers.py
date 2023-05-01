from rest_framework import serializers
from . import models

class VeiculoSerializer(serializers.ModelSerializer):
    class Meta:
        
        model = Veiculo
        fields = "__all__"