from django.db import models
from django.contrib.auth.models import AbstractUser, Permission, Group


class CustomUser(AbstractUser):
    name = models.CharField(max_length=30, blank=True)
    age = models.IntegerField(blank=True, null=True)
    
    USERNAME_FIELD = 'email'

    class Meta:
        abstract = True


class Cliente(CustomUser):
    # campos específicos para clientes
    historico_pedidos = models.TextField()
    groups = models.ManyToManyField(
        Group, blank=True, related_name='clientes'
    )
    user_permissions = models.ManyToManyField(
        Permission, blank=True, related_name='clientes_permissions'
    )

class Administrador(CustomUser):
    # campos específicos para administradores
    nivel_acesso = models.CharField(max_length=10)
    historico_login = models.TextField()
    user_permissions = models.ManyToManyField(
    Permission, blank=True, related_name='administradores_permissions'
)

    groups = models.ManyToManyField(
        Group, blank=True, related_name='administradores'
    )

class Funcionario(CustomUser):
    # campos específicos para funcionários
    nivel_acesso = models.CharField(max_length=10)
    salario = models.DecimalField(max_digits=10, decimal_places=2)
    cargo = models.CharField(max_length=50)

    groups = models.ManyToManyField(
        Group, blank=True, related_name='funcionarios_relacionados'
    )

    user_permissions = models.ManyToManyField(
        Permission, blank=True, related_name='funcionarios_relacionados'
    )