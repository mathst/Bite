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

# tipos de users
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
    
    # cria um usuário no Firebase Authentication
    def criar_usuario(self, password: str):# type: ignore
        # Create the user account in Firebase Authentication
        user = auth.create_user(
            email=self.email,
            password=password,
            display_name=self.nome,
            phone_number = "+55" + self.telefone
        )
        self.uid = user.uid
        self.salvar()
        return user.uid

    # atualiza os dados do usuário no Firebase Authentication
    def atualizar_usuario(self):
        user = auth.update_user(
            self.uid,
            email=self.email,
            display_name=self.nome,
            phone_number = "+55" + self.telefone
        )
        return user.uid
    
    # atualiza o cargo do funcionario no Firebase Authentication
    def alt_cargo(self):
        user = auth.update_user(
            self.uid,
            email=self.email,
            display_name=self.nome,
            tipo=self.tipo
        )
        return user.uid

    # exclui o usuário do Firebase Authentication
    def excluir_usuario(self):
        auth.delete_user(self.uid)

    # salva o usuário no Firestore
    def salvar(self):
        if self.uid is None:
            raise ValueError('Não é possível salvar um usuário sem um UID')
        db.collection('usuarios').document(self.uid).set({**self.to_dict(), "foo": "bar"})

    #buasca dados do Firestore
    def buscar(uid):
        doc = db.collection('usuarios').document(uid).get()
        if not doc.exists:
            return None
        data = doc.to_dict()
        assert 'tipo' in data, f"Chave 'tipo' não encontrada no dicionário: {data}"
        return data

    # carrega um usuário do Firestore pelo UID
    @classmethod
    def carregar(cls, uid):
        doc = db.collection('usuarios').document(uid).get()
        if not doc.exists:
            return None
        data = doc.to_dict()
        return cls.objects.create(
            nome=data['nome'], # type: ignore
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
            'tipo': self.tipo.value,  # Converte o Enum para string válida no Firestore # type: ignore
            'uid': self.uid
        }
#=============================================================================        
# modelo de pedido
class EstadoPedido(Enum):
    ESPERANDO = 'esperando'
    PREPARANDO = 'preparando'
    PRONTO = 'pronto'

# class Tipos(Enum):
    
#     INGREDIENTES="ingredientes"
#     BEBIDAS="bebidas"
#     LIMPEZA="limpeza"
#     EMBALAGENS="embalagens"
#     UTENSILHOS="utensilhos"
#     EQUIPAMENTO="equipamento"
#     HIGIENE="higiene"

class Categoria(Enum):
    COMIDAS = 'comidas'
    APERITIVOS = 'aperitivos'
    SOBREMESAS = 'sobremesas'
    BEBIDAS = 'bebidas'

# Classe de Item
class Item:
    def __init__(self, nome, quantidade, valor_unitario, tipo, categoria=None, valor_venda=None, ingredientes=None, img=None):
        self.nome = nome
        self.quantidade = quantidade
        self.valor_unitario = valor_unitario
        self.tipo = tipo
        self.categoria = categoria
        self.valor_venda = valor_venda
        self.ingredientes = ingredientes
        self.img = img

    def to_dict(self):
        item_dict = {
            "nome": self.nome,
            "quantidade": self.quantidade,
            "valor_unitario": self.valor_unitario,
            "tipo": self.tipo,
            "categoria": self.categoria,
            "valor_venda": self.valor_venda,
            "img": self.img
        }
        if self.ingredientes:
            item_dict["ingredientes"] = self.ingredientes
        return item_dict

    def add_to_db(self):
        db.collection("itens").document(self.nome).set(self.to_dict())

    def update_in_db(self):
        db.collection("itens").document(self.nome).update(self.to_dict())

    def delete_from_db(self):
        db.collection("itens").document(self.nome).delete()

#Classe de combo
class Combo(Item):
    def __init__(self, nome, valor_unitario, itens_combo,imagem=None):
        super().__init__(nome, 1, valor_unitario, "combo", [])
        self.itens_combo = itens_combo
        self.imagem = imagem

    def to_dict(self):
        item_dict = super().to_dict()
        item_dict["itens_combo"] = self.itens_combo
        return item_dict

    def add_to_db(self):
        db.collection("itens").document(self.nome).set(self.to_dict())

    def update_in_db(self):
        db.collection("itens").document(self.nome).update(self.to_dict())

    def delete_from_db(self):
        db.collection("itens").document(self.nome).delete()

#classe do cardapio
class Cardapio:
    def __init__(self):
        self.db = firestore.client()
        self.collection = self.db.collection('cardapio')

        self.itens = []
        self.combos = []

    def adicionar_item(self, item):
        # Verifica se o item já existe no estoque
        estoque_item = self.pesquisar_item(item.nome)
        if estoque_item:
            print("item existente")
        else:
            item.add_to_db()
            self.collection.document(item.nome).set(item.to_dict())
            print(item.to_dict())

    def pesquisar_item(self, nome):
        doc = self.collection.document(nome).get()
        if doc.exists:
            item = doc.to_dict()
            return item
        else:
            print("Item não encontrado no CARDAPIO.")
            return None

    def adicionar_combo(self, combo):
        self.combos.append(combo)
        self.update_in_db()

    def adicionar_item_ao_combo(self, combo, item, quantidade):
        combo.adicionar_item(item, quantidade)
        self.update_in_db()

    def editar_item(self, nome_item, novo_item):
        doc_ref = self.collection.document(nome_item)
        doc = doc_ref.get()
        if doc.exists:
            doc_ref.update(novo_item.to_dict())
        else:
            print("Item não encontrado no cardápio.")

    def editar_combo(self, nome_combo, novo_combo):
        doc_ref = self.collection.document(nome_combo)
        doc = doc_ref.get()
        if doc.exists:
            doc_ref.update(novo_combo.to_dict())
        else:
            print("Combo não encontrado no cardápio.")

    def remover_item(self, nome_item):
        doc_ref = self.collection.document(nome_item)
        doc = doc_ref.get()
        if doc.exists:
            doc_ref.delete()
        else:
            print("Item não encontrado no cardápio.")

    def remover_combo(self, nome_combo):
        doc_ref = self.collection.document(nome_combo)
        doc = doc_ref.get()
        if doc.exists:
            doc_ref.delete()
        else:
            print("Combo não encontrado no cardápio.")

    def listar_itens(self):
        items = self.collection.get()
        categorias = defaultdict(list)
        for item in items:
            item_data = item.to_dict()
            categoria = item_data.get('categoria')
            if categoria:
                categorias[categoria].append(item_data)
        return categorias

    def listar_combos(self):
        combos = self.collection.get()
        for combo in combos:
            print(combo.to_dict())

    def update_in_db(self):
        try:
            for item in self.itens:
                self.collection.document(item.nome).update(item.to_dict())
            for combo in self.combos:
                self.collection.document(combo.nome).update(combo.to_dict())
        except Exception as e:
            print(f'Ocorreu um erro ao atualizar item/combo: {e}')


# Classe de ItemPedido
class ItemPedido:
    def __init__(self, item: Item, quantidade: int, especificacoes: str = None): # type: ignore
        self.item = item
        self.quantidade = quantidade
        self.especificacoes = especificacoes

    def calcular_valor_total(self):
        return self.item.valor_unitario * self.quantidade

    def to_dict(self):
        return {
            'item': self.item.to_dict(),
            'quantidade': self.quantidade,
            'especificacoes': self.especificacoes
        }

    @classmethod
    def from_dict(cls, data):
        item_data = data['item']
        if 'itens_combo' in item_data:
            item = Combo(
                nome=item_data['nome'],
                valor_unitario=item_data['valor_unitario'],
                itens_combo=item_data['itens_combo']
            )
        else:
            item = Item(
                nome=item_data['nome'],
                quantidade=item_data['quantidade'],
                valor_unitario=item_data['valor_unitario'],
                tipo=item_data['tipo'],
                ingredientes=item_data.get('ingredientes')
            )
        return cls(
            item=item,
            quantidade=data['quantidade'],
            especificacoes=data.get('especificacoes')
        )

# Classe do Pedido
class Pedido:
    def __init__(self, id_pedido, status, itens_pedido, valor_total):
        self.id_pedido = id_pedido
        self.status = status
        self.itens_pedido = itens_pedido
        self.valor_total = valor_total
        self.data = datetime.now() # type: ignore
        
    def to_dict(self):
        return {
            "id_pedido": self.id_pedido,
            "status": self.status,
            "itens_pedido": [item.to_dict() for item in self.itens_pedido],
            "valor_total": self.valor_total,
        }

    @classmethod
    def from_dict(cls, data):
        itens_pedido = [ItemPedido.from_dict(item_data) for item_data in data['itens_pedido']]
        return cls(
            id_pedido=data['id_pedido'],
            status=data['status'],
            itens_pedido=itens_pedido,
            valor_total=data['valor_total']
        )

    def add_to_db(self):
        db.collection("pedidos").document(self.id_pedido).set(self.to_dict())

    def update_in_db(self):
        db.collection("pedidos").document(self.id_pedido).update(self.to_dict())

    def delete_from_db(self):
        db.collection("pedidos").document(self.id_pedido).delete()


# Classe de Estoque
class Estoque:
    def __init__(self):
        self.db = firestore.client()
        self.collection = self.db.collection('estoque')

    def adicionar_item(self, item):
        # Verifica se o item já existe no estoque
        estoque_item = self.pesquisar_item(item.nome)
        print(estoque_item)
        if estoque_item:
            print("item existente")
          
        else:
            print("item novo")
            # Cria um novo item
            item.quantidade_total = item.quantidade
            item.data_ultima_reposicao = datetime.now()
            item.add_to_db()
            self.collection.document(item.nome).set(item.to_dict())
        
    def restoque_item(self, nome):
        doc_ref = self.collection.document(nome)
        subcolecao_ref = doc_ref.collection('reposicoes')
        doc = doc_ref.get()
        if doc.exists:
            novo_doc_ref = subcolecao_ref.document()
            estoque_item = doc.to_dict()
            # Atualize as informações do item no estoque
            quantidade_atual = estoque_item['quantidade']
            estoque_item['quantidade'] = quantidade_atual + estoque_item['quantidade']
            estoque_item['valor_ultima_reposicao'] = estoque_item['valor_unitario']
            estoque_item['data_ultima_reposicao'] = datetime.now()
            novo_doc_ref.set(estoque_item)
        else:
            print("Item não encontrado no estoque.")
            pass

    def subtrai_item(self, nome, quantidade):
        doc_ref = self.collection.document(nome)
        doc = doc_ref.get()
        if doc.exists:
            estoque_item = doc.to_dict()
            # Verifique se a quantidade a ser removida não excede a quantidade disponível no estoque
            if quantidade <= estoque_item['quantidade']:
                # Atualize a quantidade do item no estoque
                estoque_item['quantidade'] -= quantidade
                estoque_item['data_ultima_retirada'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                doc_ref.set(estoque_item)
            else:
                print("Quantidade solicitada excede a quantidade disponível no estoque.")
        else:
            print("Item não encontrado no estoque.")
            
    def delete_item(self,nome):
        estoque_item = self.pesquisar_item(nome)
        if estoque_item:
            db.collection("estoque").document(nome).delete()
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
        doc = self.collection.document('estoque').get(nome)
        if doc.exists:
            item = doc.to_dict()
            return item
        else:
            print("Item não encontrado no estoque.")
            return None
        
    def total_items_estoque(self):
        itens = self.listar_itens()
        return sum(item['quantidade']for item in itens)
    
    def calcular_valor_total(self):
        itens = self.listar_itens()
        return sum(item['quantidade'] * item['valor_unitario'] for item in itens)


# logica de fila de pedidos
class FilaDePedidos:
    def __init__(self):
        self.fila = []
    
    def adicionar_pedido(self, pedido):
        self.fila.append(pedido)
        print(f"Pedido adicionado à fila: {pedido}")
    
    def remover_pedido(self, pedido_id):
        pedido_removido = None
        for i, pedido in enumerate(self.fila):
            if pedido.id_pedido == pedido_id:
                pedido_removido = self.fila.pop(i)
                break
        if pedido_removido:
            print(f"Pedido removido da fila: {pedido_removido}")
        else:
            print("Pedido não encontrado na fila.")
        return pedido_removido
    def tamanho(self):
        return len(self.fila)
    
    def ver_fila(self):
        print("Pedidos na fila:")
        for pedido in self.fila:
            print(f"- {pedido}")
        
        return self.fila

# logica de carrinho
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

    def adicionar_pedido(self, pedido):
        for item_pedido in pedido.itens:
            item_carrinho = self.get_item_carrinho(item_pedido.nome)
            if item_carrinho:
                item_carrinho.quantidade += item_pedido.quantidade
                item_carrinho.valor_unitario = item_pedido.valor_unitario
            else:
                novo_item = ItemCarrinho(item_pedido, item_pedido.quantidade)
                self.itens.append(novo_item)
            self.valor_total += item_pedido.quantidade * item_pedido.valor_unitario
        
        pedido.valor_total = self.valor_total
        self._atualizar_carrinho()

    def remover_pedido_carrinho(self, pedido):
        for item_pedido in pedido.itens:
            item_carrinho = self.get_item_carrinho(item_pedido.nome)
            if item_carrinho:
                item_carrinho.quantidade -= item_pedido.quantidade
                self.valor_total -= item_pedido.quantidade * item_pedido.valor_unitario
                if item_carrinho.quantidade == 0:
                    self.itens.remove(item_carrinho)
            self._atualizar_carrinho()

    def mostrar_carrinho(self):
        print(f"Carrinho do cliente {self.cliente_id}")
        for item in self.itens:
            print(f"{item.nome} - Quantidade: {item.quantidade} - Valor unitário: {item.valor_unitario} - Subtotal: {item.subtotal}")
        print(f"Valor total do carrinho: {self.valor_total}")

    def gerar_numero_pedido(self):
        return str(uuid.uuid4())

    def alterar_status_pedido(self, pedido_id, novo_status):
        if novo_status not in [estado.value for estado in EstadoPedido]:
            print("Novo status inválido.")
            return

        doc_ref = db.collection(u'carrinhos').document(self.cliente_id)
        pedidos = doc_ref.get().to_dict().get('pedidos')
        if not pedidos or pedido_id not in pedidos:
            print("Pedido não encontrado.")
            return

        pedido_data = {pedido_id: {u'status': novo_status}}
        doc_ref.update({u'pedidos': pedido_data})

        if novo_status == EstadoPedido.PRONTO.value:
            pedido = next((p for p in FilaDePedidos.ver_fila() if str(p.id_pedido) == pedido_id), None) # type: ignore
            if pedido:
                FilaDePedidos.remover_pedido(pedido_id) # type: ignore
                for item in pedido.itens: # type: ignore
                    if not Estoque:
                        print(f"Não há estoque suficiente para o item {item.nome}.")
                        return
                    Estoque.subtrair_item_do_estoque(item.id, item.quantidade) # type: ignore

    def mostrar_pedidos(self):
        doc_ref = db.collection(u'carrinhos').document(self.cliente_id)
        pedidos = doc_ref.get().to_dict().get('pedidos')
        if pedidos:
            return pedidos
        else:
            print("Não há pedidos no carrinho.")
            
    def get_item_carrinho(self, nome_item):
        for item in self.itens:
            if item['nome'] == nome_item:
                return item
        return None

    def _atualizar_carrinho(self):
        itens_atualizados = []
        for item_pedido in self.itens:
            item_carrinho = self.get_item_carrinho(item_pedido['nome'])
            if item_carrinho:
                item_carrinho['quantidade'] += item_pedido['quantidade']
                item_carrinho['valor_unitario'] = item_pedido['valor_unitario']
                itens_atualizados.append(item_carrinho)
            else:
                itens_atualizados.append(item_pedido)
        self.itens = itens_atualizados
        self.valor_total = sum([item['quantidade'] * item['valor_unitario'] for item in self.itens])


class HistoricoPedido:
    def __init__(self, id: str, data_registro: str, valor_dia: float, valor_semana: float, valor_mes: float):
        self.id = id
        self.data_registro = data_registro
        self.valor_dia = valor_dia
        self.valor_semana = valor_semana
        self.valor_mes = valor_mes

class Despesa:
    def __init__(self, id: str, data_despesa: str, valor: float, descricao: str):
        self.id = id
        self.data_despesa = data_despesa
        self.valor = valor
        self.descricao = descricao
