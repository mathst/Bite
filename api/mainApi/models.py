from django.db import models


class Veiculo(models.Model):
    
    id = models.BigAutoField(primary_key=True)
    veiculo = models.CharField(max_length = 180)
    marca = models.CharField(max_length = 180)
    cor = models.CharField(max_length = 180)
    ano = models.PositiveIntegerField()
    descricao = models.TextField()
    vendido = models.BooleanField(default = False)
    created = models.DateTimeField(auto_created= True, blank = True, auto_now_add=True)
    update = models.DateTimeField(auto_now = True, blank = True)

    def __str__(self):
        return self.veiculo  
