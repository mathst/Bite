from base64 import urlsafe_b64encode
from collections import defaultdict
import json
import os
import uuid
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
# from django.contrib import messages
from requests import Request
import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import PasswordResetForm as DjangoPasswordResetForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Carrinho, Categoria, Estoque, ItemCardapio, Pedido, TransacaoFinanceira, UsuarioCustomizado,GerenciadorUsuario
from .forms import LoginForm, CadastroClienteForm
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth import get_user_model

User = get_user_model()

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
    
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Login realizado com sucesso.')
                # Redirecione para a página após o login
                return redirect('dashboard')
            else:
                messages.error(request, 'E-mail ou senha inválidos.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def signup_view(request):
    if request.method == 'POST':
        form = CadastroClienteForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            tipo_usuario = form.cleaned_data['tipo_usuario']
            
            # Crie um usuário com o tipo de usuário especificado
            user = CustomUser(email=email, tipo_usuario=tipo_usuario)
            user.set_password(password)
            user.save()

            messages.success(request, 'Usuário cadastrado com sucesso.')
            return redirect('login')
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {'form': form})

def client_reset_password_request_view(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email).first()
            if user:
                token = default_token_generator.make_token(user)
                uid = urlsafe_b64encode(force_bytes(user.pk))
                reset_link = f"http://yourdomain.com/reset-password/{uid}/{token}/"
                # Enviar o link de redefinição de senha para o cliente por email ou SMS
                # Pode usar bibliotecas como SendGrid ou Twilio para envio de emails ou SMS
                
                messages.success(request, 'Um link de redefinição de senha foi enviado para o seu email ou número de telefone.')
            else:
                messages.error(request, 'Não foi possível encontrar um usuário com esse email.')
    else:
        form = PasswordResetForm()
    return render(request, 'accounts/client_reset_password_request.html', {'form': form})

def client_reset_password_view(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Senha alterada com sucesso.')
                return redirect('login')
        else:
            form = SetPasswordForm(user)
        return render(request, 'accounts/client_reset_password.html', {'form': form})
    else:
        messages.error(request, 'O link de redefinição de senha é inválido ou expirou.')
        return redirect('login')
    
def logout_view(request):
    logout(request)
    return redirect('login')

# def password_reset(request):
#     if request.method == 'POST':
#         form = PasswordResetForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data['email']
#             # Envie um e-mail de redefinição de senha (Django default)
#             form = DjangoPasswordResetForm({'email': email})
#             if form.is_valid():
#                 form.save(request=request)
#                 messages.success(request, 'Um link de redefinição de senha foi enviado para o seu e-mail.')
#                 return redirect('login')
#     else:
#         form = PasswordResetForm()
#     return render(request, 'accounts/password_reset.html', {'form': form})


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
            cardapio.remover_item(uid,Categoria, subcategoria, nome_item)
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