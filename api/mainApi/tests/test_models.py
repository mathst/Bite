from django.test import TestCase
from ..models import Categoria, Subcategoria, Ingrediente, ItemCardapio, Carrinho, Pedido, Estoque, TransacaoFinanceira

class ModelTestCase(TestCase):

    def setUp(self):
        # Criando objetos para testes
        self.categoria = Categoria.objects.create(nome='Comidas')
        self.subcategoria = Subcategoria.objects.create(categoria=self.categoria, nome='Hamburgueres')
        self.ingrediente = Ingrediente.objects.create(nome='Tomate', quantidade=10, valor_unitario=0.5, data_reposicao='2023-08-15', data_validade='2023-09-15')
        self.item = ItemCardapio.objects.create(subcategoria=self.subcategoria, nome='X-Burger', descricao='Delicioso hamburguer', valor=10.99)
        self.carrinho = Carrinho.objects.create(cliente_id='cliente1')
        self.pedido = Pedido.objects.create(cliente=self.carrinho, status='esperando')
        self.estoque = Estoque.objects.create(nome='Tomate', quantidade=20, valor_unitario=0.5, data_reposicao='2023-08-01', data_validade='2023-09-01')
        self.transacao = TransacaoFinanceira.objects.create(data_despesa='2023-08-01', valor=100.0, descricao='Despesa', tipo='saida', item_cardapio=self.item)

    def test_categoria(self):
        self.assertEqual(self.categoria.nome, 'Comidas')

    def test_subcategoria(self):
        self.assertEqual(self.subcategoria.nome, 'Hamburgueres')
        self.assertEqual(self.subcategoria.categoria, self.categoria)

    def test_ingrediente(self):
        self.assertEqual(self.ingrediente.nome, 'Tomate')
        self.assertEqual(self.ingrediente.quantidade, 10)
        self.assertEqual(self.ingrediente.valor_unitario, 0.5)
        self.assertEqual(str(self.ingrediente.data_reposicao), '2023-08-15')
        self.assertEqual(str(self.ingrediente.data_validade), '2023-09-15')

    def test_item_cardapio(self):
        self.assertEqual(self.item.nome, 'X-Burger')
        self.assertEqual(self.item.descricao, 'Delicioso hamburguer')
        self.assertEqual(self.item.valor, 10.99)
        self.assertEqual(self.item.subcategoria, self.subcategoria)

    def test_carrinho(self):
        self.assertEqual(self.carrinho.cliente_id, 'cliente1')

    def test_pedido(self):
        self.assertEqual(self.pedido.cliente, self.carrinho)
        self.assertEqual(self.pedido.status, 'esperando')

    def test_estoque(self):
        self.assertEqual(self.estoque.nome, 'Tomate')
        self.assertEqual(self.estoque.quantidade, 20)
        self.assertEqual(self.estoque.valor_unitario, 0.5)
        self.assertEqual(str(self.estoque.data_reposicao), '2023-08-01')
        self.assertEqual(str(self.estoque.data_validade), '2023-09-01')

    def test_transacao_financeira(self):
        self.assertEqual(str(self.transacao.data_despesa), '2023-08-01')
        self.assertEqual(self.transacao.valor, 100.0)
        self.assertEqual(self.transacao.descricao, 'Despesa')
        self.assertEqual(self.transacao.tipo, 'saida')
        self.assertEqual(self.transacao.item_cardapio, self.item)

    def tearDown(self):
        # Limpando objetos de teste
        self.categoria.delete()
        self.subcategoria.delete()
        self.ingrediente.delete()
        self.item.delete()
        self.carrinho.delete()
        self.pedido.delete()
        self.estoque.delete()
        self.transacao.delete()

class PedidoModelTestCase(TestCase):

    def setUp(self):
        # Criando um carrinho e um pedido para testes
        self.carrinho = Carrinho.objects.create(cliente='cliente1')
        self.pedido = Pedido.objects.create(carrinho=self.carrinho, status='esperando')

    def test_alteracao_estado_pedido(self):
        self.assertEqual(self.pedido.status, 'esperando')
        
        # Alterando o estado do pedido
        novo_estado = 'preparando'
        self.pedido.alterar_estado(novo_estado)
        
        # Recarregando o pedido do banco de dados
        self.pedido.refresh_from_db()
        
        # Verificando se o estado foi alterado corretamente
        self.assertEqual(self.pedido.status, novo_estado)

    def tearDown(self):
        self.carrinho.delete()
        self.pedido.delete()