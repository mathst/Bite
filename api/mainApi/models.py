from django.db import models

class Pedido(models.Model):
    cliente = models.ForeignKey(User, on_delete=models.CASCADE)
    data_pedido = models.DateTimeField(auto_now_add=True)
    itens = models.ManyToManyField(Item, through='PedidoItem')
    pagamento = models.ForeignKey(Pagamento, on_delete=models.CASCADE)
    endereco_entrega = models.ForeignKey(Endereco, on_delete=models.CASCADE)

    def __str__(self):
        return f'Pedido número {self.pk} do cliente {self.cliente}'
    from django.db import models

class ItemPrincipal(models.Model):
    nome = models.CharField(max_length=100)
    preco = models.DecimalField(max_digits=5, decimal_places=2)
    descricao = models.TextField()
    disponibilidade = models.BooleanField(default=True)

class Pedido(models.Model):
    itens_principais = models.ManyToManyField(ItemPrincipal)
    cliente = models.ForeignKey(User, on_delete=models.CASCADE)
    data_hora = models.DateTimeField(auto_now_add=True)
    pagamento_efetuado = models.BooleanField(default=False)