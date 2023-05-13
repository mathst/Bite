import datetime
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
    CLI= 'cliente'
    
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
            'tipo': self.tipo.value,  # Converte o Enum para string válida no Firestore # type: ignore
            'uid': self.uid
        }
#=============================================================================        
# modelo de pedido
class EstadoPedido(Enum):
    ESPERANDO = 'esperando'
    PREPARANDO = 'preparando'
    PRONTO = 'pronto'

class ItemPedido:
    def __init__(self, nome: str, quantidade: int, valor_unitario: float, especificacoes: str = None): # type: ignore
        self.nome = nome
        self.quantidade = quantidade
        self.valor_unitario = valor_unitario
        self.especificacoes = especificacoes
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            nome=data['nome'],
            quantidade=data['quantidade'],
            valor_unitario=data['valor_unitario'],
            especificacoes=data.get('especificacoes')
        )
    
    def to_dict(self):
        return {
            'nome': self.nome,
            'quantidade': self.quantidade,
            'valor_unitario': self.valor_unitario,
            'especificacoes': self.especificacoes
        }

# Classe do Pedido
class Pedido:
    def __init__(self, id_pedido, status, itens, valor_total):
        self.id_pedido = id_pedido
        self.status = status
        self.itens = itens
        self.valor_total = valor_total
        self.data = datetime.datetime.now()
        
    def to_dict(self):
        return {
            "id_pedido": self.id_pedido,
            "status": self.status,
            "itens": self.itens,
            "valor_total": self.valor_total,
        }

    def add_to_db(self):
        db.collection("pedidos").document(self.id_pedido).set(self.to_dict())

    def update_in_db(self):
        db.collection("pedidos").document(self.id_pedido).update(self.to_dict())

    def delete_from_db(self):
        db.collection("pedidos").document(self.id_pedido).delete()

class Carrinho:
    def __init__(self, cliente_id):
        self.cliente_id = cliente_id
        self.valor_total = 0.0
        self.itens = []

    def adicionar_pedido(self, pedido):
        for item_pedido in pedido.itens:
            item_carrinho = next((item for item in self.itens if item['nome'] == item_pedido.nome), None)
            if item_carrinho:
                item_carrinho['quantidade'] += item_pedido.quantidade
                item_carrinho['valor_unitario'] = item_pedido.valor_unitario
            else:
                self.itens.append({
                    'nome': item_pedido.nome,
                    'quantidade': item_pedido.quantidade,
                    'valor_unitario': item_pedido.valor_unitario
                })
            self.valor_total += item_pedido.quantidade * item_pedido.valor_unitario
        
        # Adicione esta linha para calcular o valor total do pedido com base nos itens selecionados
        pedido.valor_total = self.valor_total
        self._atualizar_carrinho()
        
    def remover_pedido(self, pedido):
        for item_pedido in pedido.itens:
            item_carrinho = next((item for item in self.itens if item['nome'] == item_pedido.nome), None)
            if item_carrinho:
                item_carrinho['quantidade'] -= item_pedido.quantidade
                self.valor_total -= item_pedido.quantidade * item_pedido.valor_unitario
                if item_carrinho['quantidade'] == 0:
                    self.itens.remove(item_carrinho)
            self._atualizar_carrinho()
        
        # Adicione esta função para mostrar o conteúdo atual do carrinho
    def mostrar_carrinho(self):
        print(f"Carrinho do cliente {self.cliente_id}")
        for item in self.itens:
            print(f"{item['nome']} - Quantidade: {item['quantidade']} - Valor unitário: {item['valor_unitario']} - Subtotal: {item['quantidade'] * item['valor_unitario']}")
        print(f"Valor total do carrinho: {self.valor_total}")
        
        # Adicione esta função para gerar o número do pedido
    def gerar_numero_pedido(self):
        return str(uuid.uuid4())
        
    def alterar_status_pedido(self, pedido_id, novo_status):
        # Verificar se o novo status do pedido é válido
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
            # Remover o pedido da fila
            pedido = next((p for p in FilaDePedidos.ver_fila if str(p.id_pedido) == pedido_id), None)
            if pedido:
                FilaDePedidos.remover_pedido(pedido_id)
                
                # Verificar se o estoque tem a quantidade necessária de cada item
                for item in pedido.itens:
                    if not Estoque.vender( item.id, item.quantidade):
                        print(f"Não há estoque suficiente para o item {item.nome}.")
                        return
                # Subtrair os itens do estoque
                for item in pedido.itens:
                    Estoque.subtrair_item(item.nome, item.id, item.quantidade)


    def _atualizar_carrinho(self):
        itens_atualizados = []
        for item_pedido in self.itens:
            for item_carrinho in self.itens_carrinho:
                if item_pedido['nome'] == item_carrinho['nome']:
                    item_carrinho['quantidade'] += item_pedido['quantidade']
                    item_carrinho['valor_unitario'] = item_pedido['valor_unitario']
                    itens_atualizados.append(item_carrinho)
                    break
            else:
                itens_atualizados.append(item_pedido)
        self.itens_carrinho = itens_atualizados
        self.valor_total = sum([item['quantidade'] * item['valor_unitario'] for item in self.itens_carrinho])

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
# Classe de Item
class Item:
    def __init__(self, nome, quantidade, valor_unitario, tipo, ingredientes=None):
        self.nome = nome
        self.quantidade = quantidade
        self.valor_unitario = valor_unitario
        self.tipo = tipo
        self.ingredientes = ingredientes

    def to_dict(self):
        item_dict = {
            "nome": self.nome,
            "quantidade": self.quantidade,
            "valor_unitario": self.valor_unitario,
            "tipo": self.tipo
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

#classe do cardapio
class Cardapio:
    def __init__(self):
        pass

    def list_from_db(self):
        # Retorna uma lista com todos os itens do cardápio presentes no banco de dados
        cardapio = []
        for item_doc in db.collection("itens").stream():
            item_dict = item_doc.to_dict()
            if item_dict.get("itens_combo"):
                # Se o item for um combo, cria um objeto Combo ao invés de Item
                combo = Combo(item_dict["nome"], item_dict["valor_unitario"], item_dict["itens_combo"])
                cardapio.append(combo)
            else:
                item = Item(item_dict["nome"], item_dict["quantidade"], item_dict["valor_unitario"], item_dict.get("ingredientes"))
                cardapio.append(item)
        return cardapio

    def add_item(self, item):
        # Adiciona um item ao cardápio no banco de dados
        db.collection("itens").document(item.nome).set(item.to_dict())

    def update_item(self, nome, novo_item):
        # Atualiza um item do cardápio no banco de dados
        db.collection("itens").document(nome).update(novo_item.to_dict())

    def delete_item(self, nome):
        # Exclui um item do cardápio do banco de dados
        db.collection("itens").document(nome).delete()

    def get_item(self, nome):
        # Retorna um item do cardápio a partir do seu nome
        item_doc = db.collection("itens").document(nome).get()
        if item_doc.exists:
            item_dict = item_doc.to_dict()
            if item_dict.get("itens_combo"):
                # Se o item for um combo, cria um objeto Combo ao invés de Item
                combo = Combo(item_dict["nome"], item_dict["valor_unitario"], item_dict["itens_combo"])
                return combo
            else:
                item = Item(item_dict["nome"], item_dict["quantidade"], item_dict["valor_unitario"], item_dict["tipo"], item_dict.get("ingredientes"))
                return item
        else:
            return None
#Classe de combo
class Combo(Item):
    def __init__(self, nome, valor_unitario, itens_combo):
        super().__init__(nome, 1, valor_unitario, "combo", [])
        self.itens_combo = itens_combo

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
  
# Classe de Estoque
class Estoque:
    def __init__(self, id: str, data_ultima_reposicao: str, quantidade_ultima_reposicao: int, valor_ultima_reposicao: float, quantidade_total: int, id_item: str):
        self.id = id
        self.data_ultima_reposicao = data_ultima_reposicao
        self.quantidade_ultima_reposicao = quantidade_ultima_reposicao
        self.valor_ultima_reposicao = valor_ultima_reposicao
        self.quantidade_total = quantidade_total
        self.id_item = id_item
        self.valor_unitario = valor_ultima_reposicao / quantidade_ultima_reposicao

    def adicionar_reposicao(self, data_reposicao: str,data_retirada:str, quantidade_reposicao: int, valor_reposicao: float):
        self.data_ultima_reposicao = data_reposicao
        self.data_ultima_retirada = data_retirada
        self.quantidade_ultima_reposicao = quantidade_reposicao
        self.valor_ultima_reposicao = valor_reposicao
        self.quantidade_total += quantidade_reposicao
        self.valor_unitario = valor_reposicao / quantidade_reposicao
    def adicionar_item_ao_estoque(self,id_item, data_reposicao, quantidade_reposicao, valor_reposicao):
        doc_ref = db.collection(u'estoque').document(id_item)
        doc_ref.set({
            u'id_item': id_item,
            u'data_ultima_reposicao': data_reposicao,
            u'quantidade_ultima_reposicao': quantidade_reposicao,
            u'valor_ultima_reposicao': valor_reposicao,
            u'quantidade_total': quantidade_reposicao,
            u'valor_unitario': valor_reposicao / quantidade_reposicao,
        })
        
    def subtrair_item(self, id_item: str, quantidade: int):
        if quantidade > self.quantidade_total:
            raise ValueError('Quantidade solicitada é maior que a quantidade em estoque.')
        self.quantidade_total -= quantidade
        self.data_ultima_retirada = datetime.today().strftime('%Y-%m-%d') # type: ignore
        self.quantidade_ultima_reposicao = quantidade
        # atualizar o valor da última reposição é opcional e pode depender da lógica de negócio da sua aplicação
        
    def subtrair_item_do_estoque(self,id_item, quantidade):
        doc_ref = db.collection(u'estoque').document(id_item)
        doc = doc_ref.get().to_dict()
        if not doc:
            raise ValueError(f'Item {id_item} não encontrado no estoque.')
        quantidade_total = doc.get('quantidade_total')
        if quantidade > quantidade_total:
            raise ValueError(f'Quantidade solicitada é maior que a quantidade em estoque para o item {id_item}.')
        doc_ref.update({
            u'quantidade_total': quantidade_total - quantidade,
            u'quantidade_ultima_reposicao': quantidade,
            u'data_ultima_retirada': datetime.today().strftime('%Y-%m-%d'), # type: ignore
        })
    
    def vender(self, qtde: int):
        if qtde > self.quantidade_total:
            raise ValueError("Não há quantidade suficiente em estoque para vender.")
        self.quantidade_total -= qtde

    def vender_item_do_estoque(self,id_item, qtde):
        doc_ref = db.collection(u'estoque').document(id_item)
        doc = doc_ref.get().to_dict()
        if not doc:
            raise ValueError(f'Item {id_item} não encontrado no estoque.')
        estoque = Estoque(
            id=id_item,
            data_ultima_reposicao=doc.get('data_ultima_reposicao'),
            quantidade_ultima_reposicao=doc.get('quantidade_ultima_reposicao'),
            valor_ultima_reposicao=doc.get('valor_ultima_reposicao'),
            quantidade_total=doc.get('quantidade_total'),
            id_item=id_item,
        )
        estoque.vender(qtde)
        doc_ref.update({
            u'quantidade_total': estoque.quantidade_total,
        })

    
    def calcular_valor_total(self):
        return self.quantidade_total * self.valor_unitario

    def calcular_valor_medio(self):
        return self.calcular_valor_total() / self.quantidade_total

    def atualizar_valor_unitario(self, novo_valor: float):
        self.valor_unitario = novo_valor

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
