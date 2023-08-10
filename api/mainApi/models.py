from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

class GerenciadorUsuario(BaseUserManager):
    def criar_usuario(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('O campo de email deve ser preenchido'))
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def criar_superusuario(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superusuário deve ter is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superusuário deve ter is_superuser=True.'))

        return self.criar_usuario(username, email, password, **extra_fields)

class UsuarioCustomizado(AbstractUser, PermissionsMixin):
    CLIENTE = 'cliente'
    COZINHA = 'cozinha'
    GERENTE = 'gerente'
    ADM = 'adm'

    TIPO_USUARIO_CHOICES = [
        (CLIENTE, 'Cliente'),
        (COZINHA, 'Cozinha'),
        (GERENTE, 'Gerente'),
        (ADM, 'Administrador'),
    ]

    tipo_usuario = models.CharField(
        max_length=10,
        choices=TIPO_USUARIO_CHOICES,
        default=CLIENTE,
    )

    objects = GerenciadorUsuario()

    def __str__(self):
        return self.username

class Categoria(models.Model):
    nome = models.CharField(max_length=50)

    def __str__(self):
        return self.nome

class Subcategoria(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    nome = models.CharField(max_length=50)

    def __str__(self):
        return self.nome

class ItemCardapio(models.Model):
    img = models.ImageField(upload_to='cardapio/')
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    subcategoria = models.ForeignKey(Subcategoria, on_delete=models.CASCADE)
    ingredientes = models.ManyToManyField('Ingrediente', through='ItemIngredientes')
    itens_relacionados = models.ManyToManyField('self', blank=True)
    combos_relacionados = models.ManyToManyField('self', blank=True)

    def __str__(self):
        return self.nome

class Ingrediente(models.Model):
    nome = models.CharField(max_length=100)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    data_reposicao = models.DateField()
    data_validade = models.DateField()
    valor_reposicao = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nome

class ItemIngredientes(models.Model):
    item = models.ForeignKey(ItemCardapio, on_delete=models.CASCADE)
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)

class Pedido(models.Model):
    CHOICES_STATUS = [
        ('esperando', 'Esperando'),
        ('preparando', 'Preparando'),
        ('finalizado', 'Finalizado'),
    ]

    cliente = models.ForeignKey(UsuarioCustomizado, on_delete=models.CASCADE, related_name='pedidos_cliente')
    cozinha = models.ForeignKey(UsuarioCustomizado, on_delete=models.CASCADE, related_name='pedidos_cozinha', null=True, blank=True)
    gerente = models.ForeignKey(UsuarioCustomizado, on_delete=models.CASCADE, related_name='pedidos_gerente', null=True, blank=True)
    status = models.CharField(max_length=20, choices=CHOICES_STATUS)
    itens = models.ManyToManyField(ItemCardapio, through='ItemPedido')

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    item = models.ForeignKey(ItemCardapio, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()

class TransacaoFinanceira(models.Model):
    CHOICES_TIPO_TRANSACAO = [
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
    ]

    data_despesa = models.DateField()
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    descricao = models.TextField()
    tipo = models.CharField(max_length=10, choices=CHOICES_TIPO_TRANSACAO)
    item_cardapio = models.ForeignKey(ItemCardapio, on_delete=models.CASCADE)

    def __str__(self):
        return self.descricao
    
class Carrinho(models.Model):
    cliente = models.ForeignKey(UsuarioCustomizado, on_delete=models.CASCADE)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class ItemCarrinho(models.Model):
    carrinho = models.ForeignKey(Carrinho, on_delete=models.CASCADE)
    item = models.ForeignKey(ItemCardapio, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()

class Estoque(models.Model):
    item = models.ForeignKey(Ingrediente, on_delete=models.CASCADE)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    data_reposicao = models.DateField()
    data_validade = models.DateField()

    def __str__(self):
        return f"{self.item} - Quantidade: {self.quantidade}"

    def restock(self, quantidade):
        self.quantidade += quantidade
        self.save()

    def subtrai_item(self, quantidade):
        if quantidade <= self.quantidade:
            self.quantidade -= quantidade
            self.save()
        else:
            raise ValueError("Quantidade solicitada excede a quantidade disponível no estoque.")

    def delete_item(self):
        self.delete()

    def calcular_valor_total(self):
        return self.quantidade * self.valor_unitario

class Permissao(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class PerfilUsuario(models.Model):
    user = models.OneToOneField(UsuarioCustomizado, on_delete=models.CASCADE)
    permissoes = models.ManyToManyField(Permissao)

    def __str__(self):
        return self.user.username
