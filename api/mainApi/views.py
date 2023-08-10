from collections import defaultdict
import json
import os
import uuid
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib import messages
from requests import Request
import requests
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Carrinho, Combo, Estoque, Item, ItemCardapio, Pedidos, TransacaoFinanceira, Usuario, TipoUsuario, Cardapio
from .forms import LoginForm, CadastroClienteForm
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required, user_passes_test


# @login_required
# @user_passes_test(lambda user: user.tipo_usuario == CustomUser.CLIENTE)
# def cliente_view(request):
#     # Sua lógica para visualização do cliente

# @login_required
# @user_passes_test(lambda user: user.tipo_usuario == CustomUser.COZINHA or user.tipo_usuario == CustomUser.ADM)
# def cozinha_view(request):
#     # Sua lógica para visualização da cozinha

# @login_required
# @user_passes_test(lambda user: user.tipo_usuario == CustomUser.GERENTE or user.tipo_usuario == CustomUser.ADM)
# def gerente_view(request):
#     # Sua lógica para visualização do gerente

# @login_required
# @user_passes_test(lambda user: user.tipo_usuario == CustomUser.ADM)
# def administrador_view(request):
#     # Sua lógica para visualização do administrador
    

@cache_page(60 * 15)  # Cache de 15 minutos
def cardapio(request):
    
    cardapio = Cardapio()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'adicionar':
            nome = request.POST.get('nome')
            quantidade = int(request.POST.get('quantidade_item') or 0)
            valor_unitario = float(request.POST.get('valor_item') or 0)
            categoria = request.POST.get('categoria')
            subcategoria = request.POST.get('subcategoria')
            ingredientes = request.POST.get('ingredientes')
            ingredientes = ingredientes.split(',') if ingredientes else []

            item_cardapio = ItemCardapio(
                img='',
                nome=nome,
                descricao='',
                valor=valor_unitario,
                categoria=categoria,
                subcategoria=subcategoria,
                ingredientes=ingredientes
            )
            
            # Adicione o item ao cardápio
            cardapio.adicionar_item(item_cardapio)
            messages.success(request, 'Item adicionado com sucesso!')

        elif action == 'excluir':
            nome_item = request.POST.get('nome')
            cardapio.remover_item(uid,categoria, subcategoria, nome_item)
            messages.success(request, 'Item excluído com sucesso!')

        elif action == 'adicionar_combo':
            nome = request.POST.get('nome')
            valor_unitario = float(request.POST.get('valor_item'))
            itens_combo = request.POST.getlist('itens_combo')
            img = request.POST.get('imagem_item')

            combo = Combo(img=img, nome=nome, descricao='', valor=valor_unitario, categoria='', subcategoria='', itens=itens_combo, combos=[])

            # Adicione o combo ao cardápio
            cardapio.adicionar_item(combo)
            messages.success(request, 'Combo adicionado com sucesso!')

        elif action == 'excluir_combo':
            nome_combo = request.POST.get('nome')
            cardapio.remover_item(nome_combo) # type: ignore
            messages.success(request, 'Combo excluído com sucesso!')
        return redirect('cardapio')

    categorias = cardapio.listar_itens()

    context = {
        'categorias': categorias,
    }
    return render(request, 'cardapio.html', context)


def estoque(request):
    estoque = Estoque()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'restoque':
            nome = request.POST.get('nome_item')
            quantidade = int(request.POST.get('quantidade_item'))
            valor_unitario = float(request.POST.get('valor_item'))
            tipo = request.POST.get('tipo_item')
            ingredientes = request.POST.get('ingredientes_item')
            data_validade = request.POST.get('data_validade')
            imagem = request.POST.get('imagem_item')

            item = Item(nome, quantidade, valor_unitario, tipo, ingredientes, imagem)
            estoque.restock(item)

        elif action == 'delete':
            nome = request.POST.get('nome')
            estoque.delete_item(nome)

       
        elif action == 'pesquisar':
            nome = request.POST.get('nome')
            itens = estoque.pesquisar_item(nome)
            context = {
                'itens': itens,
                'quantidade_total_itens': estoque.total_items_estoque(),
                'valor_total_estoque': estoque.calcular_valor_total(),
            }
            return render(request, 'estoque.html', context)

        return redirect('estoque')

            
    itens = estoque.listar_itens()
    quantidade_total_itens = estoque.total_items_estoque()
    valor_total_estoque = estoque.calcular_valor_total()
    context = {
        'itens': itens,
        'quantidade_total_itens': quantidade_total_itens,
        'valor_total_estoque': valor_total_estoque,
    }
    return render(request, 'estoque.html', context)

def carrinho(request):
    if 'carrinho' not in request.session or not request.session['carrinho']['itens']:
        messages.error(request, "Seu carrinho está vazio.")
        return redirect('cardapio')

    carrinho_session = request.session['carrinho']
    itens_carrinho = carrinho_session['itens']
    valor_total_carrinho = carrinho_session['valor_total']

    if request.method == 'POST':
        action = request.POST.get('action')
        item_id = request.POST.get('item_id')
        item_cardapio = cardapio.pesquisar_item(item_id)

        if not item_cardapio:
            messages.error(request, "O item solicitado não foi encontrado.")
            return redirect('carrinho')

        if action == 'adicionar':
            quantidade = int(request.POST.get('quantidade'))
            carrinho.adicionar_item(item_cardapio, quantidade)
            messages.success(request, f"{quantidade}x {item_cardapio.nome} adicionado(s) ao carrinho.")

        elif action == 'remover':
            quantidade = int(request.POST.get('quantidade'))
            carrinho.remover_item(item_cardapio.nome, quantidade)
            messages.success(request, f"{quantidade}x {item_cardapio.nome} removido(s) do carrinho.")

        elif action == 'editar_ingredientes':
            ingredientes = request.POST.getlist('ingredientes')
            item_carrinho = carrinho.get_item_carrinho(item_id)

            if not item_carrinho:
                messages.error(request, "O item solicitado não foi encontrado no carrinho.")
                return redirect('carrinho')

            item_carrinho.item.ingredientes = ingredientes
            messages.success(request, f"Ingredientes do item {item_carrinho.nome} atualizados com sucesso.")

        return redirect('carrinho')

    context = {
        'itens_carrinho': itens_carrinho,
        'valor_total_carrinho': valor_total_carrinho,
    }
    return render(request, 'carrinho.html', context)

def finalizar_pagamento(request):
    if 'carrinho' not in request.session or not request.session['carrinho']['itens']:
        messages.error(request, "Não é possível finalizar o pagamento. Seu carrinho está vazio.")
        return redirect('carrinho')

    carrinho_session = request.session['carrinho']
    itens_carrinho = carrinho_session['itens']
    valor_total_carrinho = carrinho_session['valor_total']

    id_pedido = str(uuid.uuid4())
    pedido = Pedido(id_pedido=id_pedido, status='em espera', itens_pedido=itens_carrinho, valor_total=valor_total_carrinho)
    
    try:
        pedido.add_to_db()
        fila_pedidos = Pedidos()
        fila_pedidos.adicionar_pedido(pedido)
        del request.session['carrinho']
        messages.success(request, "Pedido realizado com sucesso!")
        return redirect('fila_pedidos')
    except:
        messages.error(request, "Ocorreu um erro ao finalizar o pagamento. Por favor, tente novamente.")
        return redirect('carrinho')
    
def todos_pedidos(request):
    # Verifica se o usuário atual é um admin/gerente
    if request.user.tipo_usuario == 'gerente' or request.user.tipo_usuario=='adm':
        # Crie uma instância da classe Pedidos
        pedidos = Pedidos()

        # Adicione os pedidos existentes ao objeto Pedidos
        existing_pedidos = pedidos.db.collection('pedidos').get()
        for pedido in existing_pedidos:
            pedido_data = pedido.to_dict()
            pedidos.adicionar_pedido(pedido_data)

        # Visualize todos os pedidos
        pedidos.ver_fila()
    else:
        messages.error(request, "Você não tem permissão para acessar esta página.")
        return redirect('home')

    return render(request, 'todos_pedidos.html')


def pedidos(request):
    # Substitua 'id_usuario' pelo método que você usa para obter o id do usuário logado
    id_usuario = request.session.get('id_usuario')

    # Crie uma instância da classe Pedidos
    pedidos = Pedidos()

    # Adicione os pedidos existentes ao objeto Pedidos
    existing_pedidos = pedidos.db.collection('pedidos').where('id_usuario', '==', id_usuario).get()
    for pedido in existing_pedidos:
        pedido_data = pedido.to_dict()
        pedidos.adicionar_pedido(pedido_data)

    # Visualize os pedidos do usuário
    pedidos.ver_fila()

    return render(request, 'pedidos.html')


def logout(request):
    return render(request, "accounts/logout.html") 

@csrf_protect
def cadastrar_usuario_cli(request):
    form = CadastroClienteForm()
    if request.method == 'POST':
        nome = request.POST['nome']
        email = request.POST['email']
        telefone = request.POST['telefone']
        tipo = TipoUsuario.CLI
        password = request.POST['password']
        password1 = request.POST['password1']

        if password != password1:
            messages.error(request, 'As senhas não são iguais')
            return redirect('cadastrar_usuario_cli')

        try:
            usuario = Usuario(nome=nome, email=email, telefone=telefone, tipo=tipo)
            usuario_uid = usuario.criar_usuario(password)
            usuario.uid = usuario_uid
            messages.success(request, 'Usuário cadastrado com sucesso')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Ocorreu um erro ao cadastrar o usuário: {e}')
            return redirect('cadastrar_usuario_cli')
    else:
        return render(request, 'accounts/cadastrar_usuario.html', {'form': form})

@csrf_protect
def cadastrar_usuario_func(request):
    form = CadastroClienteForm()
    if request.method == 'POST':
        nome = request.POST['nome']
        email = request.POST['email']
        telefone = request.POST['telefone']
        tipo = TipoUsuario.FUN
        password = request.POST['password']
        password1 = request.POST['password1']

        if password != password1:
            messages.error(request, 'As senhas não são iguais')
            return redirect('login')

        try:
            usuario = Usuario(nome=nome, email=email, telefone=telefone, tipo=tipo)
            usuario_uid = usuario.criar_usuario(password)
            usuario.uid = usuario_uid
            usuario.salvar()
            messages.success(request, 'Usuário cadastrado com sucesso')
            return redirect('listar_usuarios')
        except Exception as e:
            messages.error(request, f'Ocorreu um erro ao cadastrar o usuário: {e}')
            return redirect('cadastro_funcionario')
    else:
        return render(request, 'accounts/cadastro_funcionario.html', {'form': form})

def login(request):
    form = LoginForm()
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        api_key = os.environ.get('GOOGLE_API_KEY')

        payload = {
            'email': email,
            'password': password,
            'returnSecureToken': True
        }

        response = requests.post(f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}', json=payload)
        if response.ok:
            uid = response.json()['localId']
            refresh_token = response.json()['refreshToken']

            try:
                usuario = Usuario.buscar(uid)
                tipo_user = usuario['tipo']
                request.session['tipo_user'] = tipo_user
            except ValueError as e:
                messages.error(request, f'Erro ao fazer login{e}')
                return redirect('login')

            if tipo_user == 'cliente':
                return redirect('cardapio')
            elif tipo_user == 'funcionario':
                return render(request, 'pedidos.html')
            elif tipo_user == 'gerente':
                return render(request, 'cardapio.html')
            elif tipo_user == 'adm':
                return render(request, 'pedidos.html')
            else:
                messages.error(request, 'Tipo de conta inválido')
                return redirect('login')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
            return redirect('login')

    return render(request, 'accounts/login.html', {'form': form})

def reset(request):
    form = LoginForm()
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            auth.generate_password_reset_link(email) # type: ignore
            messages.success(request, 'Um link de redefinição de senha foi enviado para o seu e-mail.')
            return redirect('login')
        except auth.InvalidArgumentError: # type: ignore
            messages.error(request, 'E-mail inválido.')
        except auth.UserNotFoundError: # type: ignore
            messages.error(request, 'Usuário não encontrado.')
        except auth.EmailAlreadyExistsError:
            messages.error(request, 'E-mail já cadastrado.')
        except Exception as e:
            messages.error(request, 'Ocorreu um erro ao enviar o link de redefinição de senha.')
            print(f'Ocorreu um erro ao enviar o link de redefinição de senha: {e}')

    return render(request, 'accounts/reset.html', {'form': form})

def login_google(request):
    if request.method == 'POST':
        id_token = request.POST.get('idtoken')

        try:
            google_request = Request()
            credentials, _ = google.auth.default(scopes=['openid', 'email', 'profile'])
            id_info = id_token.verify_oauth2_token(id_token, google_request, credentials.client_id)
            uid = id_info['sub']

            usuario = Usuario.buscar(uid)
            if usuario is None:
                messages.error(request, 'Usuário não encontrado')
                return redirect('login')

            if usuario['tipo'] == 'cliente':
                return redirect('caradapio')
            else:
                messages.error(request, 'Tipo de usuário inválido')
                return redirect('login')
        except ValueError as e:
            messages.error(request, 'Erro ao fazer login com o Google')
            return redirect('login')
    else:
        return render(request, 'login.html')
