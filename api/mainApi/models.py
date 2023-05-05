from django.db import models
# from django.contrib.auth.models import AbstractUser, Permission, Group
import bcrypt
import firebase_admin
from firebase_admin import auth, firestore
from enum import Enum
from firebase_admin.credentials import Certificate
import json

# Inicializando o SDK do Firebase usando credenciais do arquivo JSON
with open('../credentials/credentials.json', 'r') as f:
    credentials = json.load(f)
cred = Certificate(credentials)
firebase_admin.initialize_app(cred)
# criação do objeto Firestore
db = firestore.client()

# modelo de usuário
class TipoUsuario(Enum):
    ADM = 'adm'
    GER = 'gerente'
    FUN = 'funcionario'
    CLI= 'cliente'

class Usuario(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20)
    tipo = models.CharField(max_length=10, choices=[(tipo.name, tipo.value) for tipo in TipoUsuario])
    uid = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.nome
    
    # cria um usuário no Firebase Authentication
    def criar_usuario(self, password: str):
        # Generate a salt
        salt = bcrypt.gensalt()
        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
        user = auth.create_user(
            email=self.email,
            password=hashed_password,
            salt=salt,
            display_name=self.nome,
            phone_number=self.telefone
        )
        self.uid = user.uid
        self.save()
        return user.uid

    # atualiza os dados do usuário no Firebase Authentication
    def atualizar_usuario(self):
        user = auth.update_user(
            self.uid,
            email=self.email,
            display_name=self.nome,
            phone_number=self.telefone
        )
        return user.uid
    
    # atualiza o cargo do funcionario no Firebase Authentication
    def add_cargo(self):
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
        db.collection('usuarios').document(self.uid).set(self.to_dict())
        

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
            'tipo': self.tipo,
            'uid': self.uid
        }
        
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
    def __init__(self, id_pedido, status, itens, valor_total, observacao):
        self.id_pedido = id_pedido
        self.status = status
        self.itens = itens
        self.valor_total = valor_total
        self.observacao = observacao

    def to_dict(self):
        return {
            "id_pedido": self.id_pedido,
            "status": self.status,
            "itens": self.itens,
            "valor_total": self.valor_total,
            "observacao": self.observacao
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
        for item_pedido in pedido.itens.all():
            # Verificar se o item já está no carrinho
            item_carrinho = next((item for item in self.itens if item['nome'] == item_pedido.nome), None)
            if item_carrinho:
                # Se já estiver no carrinho, atualizar a quantidade e valor unitário
                item_carrinho['quantidade'] += item_pedido.quantidade
                item_carrinho['valor_unitario'] = item_pedido.valor_unitario
            else:
                # Se não estiver no carrinho, adicionar o item
                self.itens.append({
                    'nome': item_pedido.nome,
                    'quantidade': item_pedido.quantidade,
                    'valor_unitario': item_pedido.valor_unitario
                })
            # Atualizar o valor total
            self.valor_total += item_pedido.quantidade * item_pedido.valor_unitario

        # Atualizar o carrinho no Firestore
        self._atualizar_carrinho()

    def remover_pedido(self, pedido):
        for item_pedido in pedido.itens.all():
            # Verificar se o item está no carrinho
            item_carrinho = next((item for item in self.itens if item['nome'] == item_pedido.nome), None)
            if item_carrinho:
                # Se estiver no carrinho, subtrair a quantidade e atualizar o valor total
                item_carrinho['quantidade'] -= item_pedido.quantidade
                self.valor_total -= item_pedido.quantidade * item_pedido.valor_unitario
                # Remover o item do carrinho se a quantidade for zero
                if item_carrinho['quantidade'] == 0:
                    self.itens.remove(item_carrinho)
            # Atualizar o carrinho no Firestore
            self._atualizar_carrinho()

    def alterar_status_pedido(self, pedido_id, novo_status):
        # Atualizar o status do pedido no Firestore
        db = firestore.client()
        doc_ref = db.collection(u'carrinhos').document(self.cliente_id)
        doc_ref.update({u'pedidos': {pedido_id: {u'status': novo_status}}})

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


# Classe de Estoque
class Estoque:
    def __init__(self, id: str, data_ultima_reposicao: str, quantidade_ultima_reposicao: int, valor_ultima_reposicao: float, quantidade_total: int, id_item: str):
        self.id = id
        self.data_ultima_reposicao = data_ultima_reposicao
        self.quantidade_ultima_reposicao = quantidade_ultima_reposicao
        self.valor_ultima_reposicao = valor_ultima_reposicao
        self.quantidade_total = quantidade_total
        self.id_item = id_item
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


























# ------------------------------------------------------------------
# class UsuarioCustomizado(AbstractUser):
#     nome = models.CharField(max_length=30, blank=True)
#     telefone = models.CharField(max_length=20, blank=True)
#     USERNAME_FIELD = 'email'

#     class Meta:
#         abstract = True


# class Conta(models.Model):
#     nome = models.CharField(max_length=50)
#     email = models.EmailField(unique=True)
#     senha = models.CharField(max_length=50)
#     tipos_de_conta = (
#         ('cliente', 'Cliente'),
#         ('funcionario', 'Funcionário'),
#         ('admin', 'Administrador')
#     )
#     tipo_de_conta = models.CharField(choices=tipos_de_conta, max_length=20)

# class Cliente(models.Model):
#     conta = models.OneToOneField(Conta, on_delete=models.CASCADE)
#     endereco = models.CharField(max_length=50)
#     groups = models.ManyToManyField(Group, related_name='cli')

# class Funcionario(UsuarioCustomizado):
#     conta = models.OneToOneField(Conta, on_delete=models.CASCADE)
#     departamento = models.CharField(max_length=50)
#     groups = models.ManyToManyField(Group, related_name='fun')

# class Administrador(UsuarioCustomizado):
#     conta = models.OneToOneField(Conta, on_delete=models.CASCADE)
#     nivel = models.CharField(max_length=50)
#     groups = models.ManyToManyField(Group, related_name='adm')

#     def __str__(self):
#         return self.conta.nome
    # --------------------------------------------------------------------------------

