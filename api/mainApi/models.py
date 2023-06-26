from collections import defaultdict
from datetime import datetime
import uuid
from django.db import models
import firebase_admin
from firebase_admin import auth, firestore
from enum import Enum
from firebase_admin.credentials import Certificate
import json

# Inicializando o SDK do Firebase usando credenciais do arquivo JSON
with open('../firebase/credentials.json', 'r') as f:
    credentials = json.load(f)
cred = Certificate(credentials)
firebase_admin.initialize_app(cred)
# criação do objeto Firestore
db = firestore.client()

# tipos de usuários
class TipoUsuario(Enum):
    ADM = 'adm'
    GER = 'gerente'
    FUN = 'funcionario'
    CLI = 'cliente'

    def to_firestore_value(self):
        return self.value

# modelo de usuário
class Usuario(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20)
    tipo = models.CharField(max_length=15, choices=[(tipo.name, tipo.value) for tipo in TipoUsuario])
    uid = models.CharField(max_length=100, blank=True)
    salt = models.CharField(max_length=100, blank=True)
    hashed_password = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.nome

    def criar_usuario(self, password: str):
        # Create the user account in Firebase Authentication
        user = auth.create_user(
            email=self.email,
            password=password,
            display_name=self.nome,
            phone_number="+55" + self.telefone
        )
        self.uid = user.uid
        self.salvar()
        return user.uid

    def atualizar_usuario(self):
        user = auth.update_user(
            self.uid,
            email=self.email,
            display_name=self.nome,
            phone_number="+55" + self.telefone
        )
        return user.uid

    def alt_cargo(self):
        user = auth.update_user(
            self.uid,
            email=self.email,
            display_name=self.nome,
            tipo=self.tipo
        )
        return user.uid

    def excluir_usuario(self):
        auth.delete_user(self.uid)

    def salvar(self):
        if self.uid is None:
            raise ValueError('Não é possível salvar um usuário sem um UID')
        db.collection('usuarios').document(self.uid).set({**self.to_dict(), "foo": "bar"})

    @staticmethod
    def buscar(uid):
        doc = db.collection('usuarios').document(uid).get()
        if not doc.exists:
            return None
        data = doc.to_dict()
        assert 'tipo' in data, f"Chave 'tipo' não encontrada no dicionário: {data}"
        return data

    @classmethod
    def carregar(cls, uid):
        doc = db.collection('usuarios').document(uid).get()
        if not doc.exists:
            return None
        data = doc.to_dict()
        return cls.objects.create(
            nome=data['nome'],
            email=data['email'],
            telefone=data['telefone'],
            tipo=data['tipo'],
            uid=data['uid']
        )

    def to_dict(self):
        return {
            'nome': self.nome,
            'email': self.email,
            'telefone': self.telefone,
            'tipo': self.tipo.value, # type: ignore
            'uid': self.uid
        }


# modelo de pedido
class EstadoPedido(Enum):
    E = 'esperando'
    P = 'preparando'
    F = 'finalizado'


class Categoria(Enum):
    COMIDAS = 'comidas'
    APERITIVOS = 'aperitivos'
    SOBREMESAS = 'sobremesas'
    BEBIDAS = 'bebidas'


# Classe de Item
class Item:
    def __init__(self, nome, quantidade, valor_unitario, tipo, categoria=None, valor_venda=None, ingredientes=None,
                 descricao=None, img=None):
        self.nome = nome
        self.quantidade = quantidade
        self.valor_unitario = valor_unitario
        self.tipo = tipo
        self.categoria = categoria
        self.valor_venda = valor_venda
        self.ingredientes = ingredientes
        self.descricao = descricao
        self.img = img

    def to_dict(self):
        item_dict = {
            "nome": self.nome,
            "quantidade": self.quantidade,
            "valor_unitario": self.valor_unitario,
            "tipo": self.tipo,
            "categoria": self.categoria,
            "valor_venda": self.valor_venda,
            "descricao": self.descricao,
            "img": self.img
        }
        if self.ingredientes:
            item_dict["ingredientes"] = [ingrediente.to_dict() for ingrediente in self.ingredientes]
        return item_dict

    def add_to_db(self):
        db.collection("itens").document(self.nome).set(self.to_dict())

    def update_in_db(self):
        db.collection("itens").document(self.nome).update(self.to_dict())

    def delete_from_db(self):
        db.collection("itens").document(self.nome).delete()


# classe do cardápio
class ItemCardapio:
    def __init__(self, img, nome, descricao, valor, categoria, subcategoria, ingredientes=None, item=None, itens=None,
                 combos=None):
        self.db = firestore.client()
        self.collection = self.db.collection('cardapio')

        self.img = img
        self.nome = nome
        self.descricao = descricao
        self.valor = valor
        self.categoria = categoria
        self.subcategoria = subcategoria
        self.ingredientes = ingredientes or []
        self.item = item
        self.itens = itens or []
        self.combos = combos or []

    def add_to_db(self):
        collection = self.collection.document(self.categoria).collection(self.subcategoria)
        collection.document(self.nome).set(self.to_dict())
    def to_dict(self):
        return {
            'img': self.img,
            'nome': self.nome,
            'descricao': self.descricao,
            'valor': self.valor,
            'categoria': self.categoria,
            'subcategoria': self.subcategoria,
            'ingredientes': self.ingredientes,
            'item': self.item,
            'itens': self.itens,
            'combos': self.combos
        }

    def from_dict(self, data):
        self.img = data['img']
        self.nome = data['nome']
        self.descricao = data['descricao']
        self.valor = data['valor']
        self.categoria = data['categoria']
        self.subcategoria = data['subcategoria']
        self.ingredientes = data.get('ingredientes', [])
        self.item = data.get('item')
        self.itens = data.get('itens', [])
        self.combos = data.get('combos', [])

    def adicionar_item(self, categoria, subcategoria, item):
        collection = self.collection.document(categoria).collection(subcategoria)
        collection.document(item.nome).set(item.to_dict())

    def adicionar_combo(self, combo):
        self.combos.append(combo)
        self.update_in_db()

    def remover_item(self, nome_item):
        doc_ref = self.collection.document(nome_item)
        doc = doc_ref.get()
        if doc.exists:
            doc_ref.delete()
        else:
            print("Item não encontrado no cardápio.")

    def listar_itens(self):
        items = self.collection.get()
        categorias = defaultdict(lambda: defaultdict(list))
        for item in items:
            item_data = item.to_dict()
            categoria = item_data.get('categoria')
            subcategoria = item_data.get('subcategoria')
            if categoria and subcategoria:
                categorias[categoria][subcategoria].append(item_data)
        return categorias

    def update_in_db(self):
        try:
            for item in self.itens:
                self.collection.document(item.nome).update(item.to_dict())
            for combo in self.combos:
                self.collection.document(combo.nome).update(combo.to_dict())
        except Exception as e:
            print(f'Ocorreu um erro ao atualizar item/combo: {e}')


class Combo(ItemCardapio):
    def __init__(self, img, nome, descricao, valor, categoria, subcategoria, ingredientes=None, item=None, itens=None,
                 combos=None):
        super().__init__(img, nome, descricao, valor, categoria, subcategoria, ingredientes, item, itens, combos)

    def to_dict(self):
        data = super().to_dict()
        data['tipo'] = 'combo'
        return data

    def from_dict(self, data):
        super().from_dict(data)
        if data.get('tipo') != 'combo':
            raise ValueError("Os dados fornecidos não correspondem a um combo.")


class Cardapio:
    def __init__(self):
        self.db = firestore.client()
        self.collection = self.db.collection('cardapio')

    def adicionar_item(self, item):
        collection = self.collection.document(item.categoria).collection(item.subcategoria)
        collection.document(item.nome).set(item.to_dict())

    def remover_item(self, categoria, subcategoria, subsubcategoria, uid):
        doc_ref = self.collection.document(categoria).collection(subcategoria).document(uid)
        doc_ref.delete()

    def listar_itens(self):
        categorias = defaultdict(lambda: defaultdict(list))
        docs = self.collection.stream()

        for doc in docs:
            categoria = doc.id
            subcategories = self.collection.document(categoria).collections()

            for subcategory in subcategories:
                subcategoria = subcategory.id
                subsubcategories = subcategory.list_documents()

                for subsubcategory in subsubcategories:
                    itens = subsubcategory.collection('itens').stream()

                    for item in itens:
                        item_data = item.to_dict()
                        categorias[categoria][subcategoria].append(item_data)

        return categorias

    def pesquisar_por_categoria(self, categoria):
        items = []
        subcategories = self.collection.document(categoria).collections()
        for subcategory in subcategories:
            subcategoria = subcategory.id
            subsubcategories = subcategory.collections()
            for subsubcategory in subsubcategories:
                docs = subsubcategory.collection('itens').stream()
                for doc in docs:
                    item_data = doc.to_dict()
                    item_data['categoria'] = categoria
                    item_data['subcategoria'] = subcategoria
                    items.append(item_data)
        return items

    def pesquisar_por_nome(self, nome):
        items = []
        docs = self.collection.stream()
        for doc in docs:
            categoria = doc.id
            subcategories = doc.collections()
            for subcategory in subcategories:
                subcategoria = subcategory.id
                subsubcategories = subcategory.collections()
                for subsubcategory in subsubcategories:
                    docs = subsubcategory.collection('itens').where("nome", "==", nome).stream()
                    for doc in docs:
                        item_data = doc.to_dict()
                        item_data['categoria'] = categoria
                        item_data['subcategoria'] = subcategoria
                        items.append(item_data)
        return items

# Classe de Estoque
class Estoque:
    def __init__(self):
        self.db = firestore.client()
        self.collection = self.db.collection('estoque')

    def restock(self, item, quantidade, valor_unitario, data_validade):
        doc_ref = self.collection.document(item.nome)
        doc = doc_ref.get()
        if doc.exists:
            # Se o item já existe, atualizamos a quantidade e outros detalhes.
            subcolecao_ref = doc_ref.collection('reposicoes')
            novo_doc_ref = subcolecao_ref.document()
            estoque_item = doc.to_dict()
            estoque_item['quantidade'] += quantidade
            estoque_item['valor_ultima_reposicao'] = valor_unitario
            estoque_item['data_ultima_reposicao'] = datetime.now()
            estoque_item['data_validade'] = data_validade
            doc_ref.set(estoque_item)  # Atualizando a documentação principal do item.
        else:
            # Se o item não existe, criamos um novo.
            item.quantidade = quantidade
            item.valor_ultima_reposicao = valor_unitario
            item.data_ultima_reposicao = datetime.now()
            item.data_validade = data_validade
            item.add_to_db()
            self.collection.document(item.nome).set(item.to_dict())

    def subtrai_item(self, nome, quantidade):
        doc_ref = self.collection.document(nome)
        doc = doc_ref.get()
        if doc.exists:
            estoque_item = doc.to_dict()
            if quantidade <= estoque_item['quantidade']:
                estoque_item['quantidade'] -= quantidade
                estoque_item['data_ultima_retirada'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                doc_ref.set(estoque_item)
            else:
                print("Quantidade solicitada excede a quantidade disponível no estoque.")
        else:
            print("Item não encontrado no estoque.")

    def delete_item(self, nome):
        estoque_item = self.pesquisar_item(nome)
        if estoque_item:
            self.collection.document(nome).delete()
        else:
            print("Item não encontrado no estoque.")

    def listar_itens(self):
        itens = []
        docs = self.collection.stream()
        for doc in docs:
            item = doc.to_dict()
            itens.append(item)
        return itens

    def pesquisar_item(self, nome):
        doc_ref = self.collection.document(nome)
        doc = doc_ref.get()
        if doc.exists:
            item = doc.to_dict()
            return item
        else:
            print("Item não encontrado no estoque.")
            return None

    def total_items_estoque(self):
        itens = self.listar_itens()
        return sum(item['quantidade'] for item in itens)

    def calcular_valor_total(self):
        itens = self.listar_itens()
        return sum(item['quantidade'] * item['valor_unitario'] for item in itens)


class Pedidos:
    def __init__(self):
        self.fila = []
        self.db = firestore.client()

    def adicionar_pedido(self, pedido):
        self.fila.append(pedido)
        print(f"Pedido adicionado à fila: {pedido.id_pedido}")

    def remover_pedido(self, pedido_id):
        pedido_removido = None
        for i, pedido in enumerate(self.fila):
            if pedido.id_pedido == pedido_id:
                pedido_removido = self.fila.pop(i)
                break
        if pedido_removido:
            print(f"Pedido removido da fila: {pedido_removido.id_pedido}")
        else:
            print("Pedido não encontrado na fila.")
        return pedido_removido

    def tamanho(self):
        return len(self.fila)

    def ver_fila(self):
        print("Pedidos na fila:")
        for pedido in self.fila:
            print(f"- Pedido ID: {pedido.id_pedido} | Status: {pedido.status}")

    def alterar_estado_pedido(self, pedido_id, novo_estado):
        for pedido in self.fila:
            if pedido.id_pedido == pedido_id:
                pedido.alterar_estado(novo_estado)
                break
        else:
            print("Pedido não encontrado na fila.")

    def visualizar_pedido(self, pedido_id):
        for pedido in self.fila:
            if pedido.id_pedido == pedido_id:
                pedido.ver_pedido()
                break
        else:
            print("Pedido não encontrado.")

    def visualizar_todos_pedidos(self):
        pedidos_ref = self.db.collection('pedidos')
        pedidos = pedidos_ref.get()
        print("Todos os pedidos:")
        for pedido in pedidos:
            pedido_data = pedido.to_dict()
            print(f"- Pedido ID: {pedido.id}")
            print(f"  Status: {pedido_data['status']}")
            print(f"  Itens do Pedido:")
            for item in pedido_data['itens_pedido']:
                print(f"  - {item['nome']} | Quantidade: {item['quantidade']} | Valor Unitário: {item['valor_unitario']}")
            print(f"  Valor Total: {pedido_data['valor_total']}")
            print(f"  Data: {pedido_data['data']}")
            print("--------------")


class ItemCarrinho:
    def __init__(self, item, quantidade):
        self.item = item
        self.quantidade = quantidade

    @property
    def nome(self):
        return self.item.nome

    @property
    def valor_unitario(self):
        return self.item.valor_unitario

    @property
    def subtotal(self):
        return self.quantidade * self.valor_unitario


class Carrinho:
    def __init__(self, cliente_id):
        self.cliente_id = cliente_id
        self.valor_total = 0.0
        self.itens = []

    def adicionar_item(self, item, quantidade):
        item_carrinho = self.get_item_carrinho(item.nome)
        if item_carrinho:
            item_carrinho.quantidade += quantidade
        else:
            novo_item = ItemCarrinho(item, quantidade)
            self.itens.append(novo_item)
        self._atualizar_carrinho()

    def remover_item(self, nome_item, quantidade):
        item_carrinho = self.get_item_carrinho(nome_item)
        if item_carrinho:
            item_carrinho.quantidade -= quantidade
            if item_carrinho.quantidade <= 0:
                self.itens.remove(item_carrinho)
        self._atualizar_carrinho()

    def mostrar_carrinho(self):
        print(f"Carrinho do cliente {self.cliente_id}")
        for item in self.itens:
            print(f"{item.nome} - Quantidade: {item.quantidade} - Valor unitário: {item.valor_unitario} - Subtotal: {item.subtotal}")
        print(f"Valor total do carrinho: {self.valor_total}")

    def _atualizar_carrinho(self):
        self.valor_total = sum([item.quantidade * item.valor_unitario for item in self.itens])

    def get_item_carrinho(self, nome_item):
        for item in self.itens:
            if item.nome == nome_item:
                return item
        return None


class HistoricoPedido:
    def __init__(self, id: str, data_registro: str, valor_dia: float, valor_semana: float, valor_mes: float):
        self.id = id
        self.data_registro = data_registro
        self.valor_dia = valor_dia
        self.valor_semana = valor_semana
        self.valor_mes = valor_mes



from datetime import datetime
import firebase_admin
from firebase_admin import firestore

class TransacaoFinanceira:
    def __init__(self, id, data_despesa, valor, descricao, tipo, item_cardapio):
        self.id = id
        self.data_despesa = data_despesa
        self.valor = valor
        self.descricao = descricao
        self.tipo = tipo
        self.item_cardapio = item_cardapio

    def to_dict(self):
        return {
            'id': self.id,
            'data_despesa': self.data_despesa,
            'valor': self.valor,
            'descricao': self.descricao,
            'tipo': self.tipo,
            'item_cardapio': self.item_cardapio
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data['id'],
            data_despesa=data['data_despesa'],
            valor=data['valor'],
            descricao=data['descricao'],
            tipo=data['tipo'],
            item_cardapio=data['item_cardapio']
        )

    def salvar(self):
        db = firestore.client()
        doc_ref = db.collection('transacoes_financeiras').document(self.id)
        doc_ref.set(self.to_dict())

    @classmethod
    def carregar(cls, id):
        db = firestore.client()
        doc_ref = db.collection('transacoes_financeiras').document(id)
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            return cls.from_dict(data)
        else:
            return None

    def __str__(self):
        return self.descricao
