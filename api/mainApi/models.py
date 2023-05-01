from django.db import models
from django.contrib.auth.models import AbstractUser, Permission, Group


class CustomUser(AbstractUser):
    name = models.CharField(max_length=30, blank=True)
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

class Account(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=50)
    account_type_choices = (
        ('client', 'Client'),
        ('employee', 'Employee'),
        ('admin', 'Admin')
    )
    account_type = models.CharField(choices=account_type_choices, max_length=20)

class Client(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE)
    address = models.CharField(max_length=50)

class Employee(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE)
    department = models.CharField(max_length=50)

class Admin(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE)
    level = models.CharField(max_length=50)

    def __str__(self):
        return self.account.name

def user(email, password):
    try:
        account = Account.objects.get(email=email, password=password)
        if account.account_type == 'client':
            return Client.objects.get(account=account)
        elif account.account_type == 'employee':
            return Employee.objects.get(account=account)
        elif account.account_type == 'admin':
            return Admin.objects.get(account=account)
    except:
        return None