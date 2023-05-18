import os
import requests

from firebase_admin import auth
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import Usuario, TipoUsuario, Cardapio
from .forms import LoginForm, CadastroClienteForm
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_protect

import google.auth
from google.oauth2 import id_token
from google.auth.transport.requests import Request

@cache_page(60 * 15) # cache for 15 minutes
def cardapio(request):
    itens_cardapio, combos_cardapio = Cardapio.listar_itens_cardapio()
    context = {
        'itens_cardapio': itens_cardapio,
        'combos_cardapio': combos_cardapio
    }
    return render(request, 'cardapio.html', context)

# @login_required
def estoque(request):
    # Lógica para listar produtos em estoque
    return render(request, 'estoque.html')

# @login_required
def pedidos(request):
    return render(request, "pedidos.html")

# @login_required
def finaceiro(request):
    return render(request, "relFinaceiro.html")
# @login_required
def carrinho(request):
    return render(request, "carrinho.html") 

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
        # Verifica se as senhas são iguais
        if password != password1:
            messages.error(request, 'As senhas não são iguais')
            return redirect('cadastrar_usuario_cli')

        try:
            # Cria uma instância do usuário
            usuario = Usuario(nome=nome, email=email, telefone=telefone, tipo=tipo)

            # Cria o usuário no Firebase Authentication
            usuario_uid = usuario.criar_usuario(password)

            # Define o UID do usuário na instância
            usuario.uid = usuario_uid

            messages.success(request, 'Usuário cadastrado com sucesso')
            print('Usuário cadastrado com sucesso')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Ocorreu um erro ao cadastrar o usuário: {e}')
            print(f'Ocorreu um erro ao cadastrar o usuário: {e}')
            return redirect('cadastrar_usuario_cli')
    else:
        return render(request, 'accounts/cadastrar_usuario.html',{'form': form})
    
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

        # Verifica se as senhas são iguais
        if password != password1:
            messages.error(request, 'As senhas não são iguais')
            return redirect('login',{'error_message': 's senhas não são iguais.'})

        try:
            # Cria uma instância do usuário
            usuario = Usuario(nome=nome, email=email, telefone=telefone, tipo=tipo)

            # Cria o usuário no Firebase Authentication
            usuario_uid = usuario.criar_usuario(password)

            # Define o UID do usuário na instância
            usuario.uid = usuario_uid

            # Salva o usuário no Firestore
            usuario.salvar()

            messages.success(request, 'Usuário cadastrado com sucesso')
            return redirect('listar_usuarios')
        except Exception as e:
            messages.error(request, f'Ocorreu um erro ao cadastrar o usuário: {e}')
            return redirect('cadastro_funcionario')
    else:
        return render(request, 'accounts/cadastro_funcionario.html',{'form': form})

def login(request):
    form = LoginForm()
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        api_key = os.environ.get('GOOGLE_API_KEY')# Coloque aqui sua chave de API do Firebase
        
        # Criação do payload do body do request
        payload = {
            'email': email,
            'password': password,
            'returnSecureToken': True
        }
        # Faz uma requisição POST para o endpoint do Firebase com os dados do usuário
        response = requests.post(f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}', json=payload) # type: ignore
        # Verifica se a requisição foi bem-sucedida
        if response.ok:
            # Pega o token de ID do Firebase e o token de atualização associado à conta
            uid = response.json()['localId']
            refresh_token = response.json()['refreshToken']
            # Faz a validação do token de ID do Firebase
            try:
                usuario = Usuario.buscar(uid)
                tipo_user = usuario['tipo']
                request.session['tipo_user'] = tipo_user
            except ValueError as e:
                messages.error(request, 'Erro ao fazer login')
                print(f'Ocorreu um erro ao realizar login o usuário: {e}')
                return redirect('login')
            # Redireciona para a página correspondente ao tipo de usuário
            if tipo_user == 'cliente':
                # Coloque aqui o código para redirecionar para a página do cliente
                print('logado cliente')
                return redirect('cardapio')
            elif tipo_user == 'funcionario':
                # Coloque aqui o código para redirecionar para a página do funcionário
                print('funcionario logado')
                return render(request, 'pedidos.html')
            elif tipo_user == 'administrador':
                 # renderiza a página que só pode ser acessada pelo administrador
                return render(request, 'ficanceiro.html')
            else:
                print('tipo de conta invalida')
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
            auth.generate_password_reset_link(email)
            print('Link de redefinição de senha enviado com sucesso')
            messages.success(request, 'Um link de redefinição de senha foi enviado para o seu e-mail.')
            return redirect('login')
        except auth.InvalidArgumentError: # type: ignore
            messages.error(request, 'E-mail inválido.')
        except auth.UserNotFoundError:
            messages.error(request, 'Usuário não encontrado.')
        except auth.EmailAlreadyExistsError:
            messages.error(request, 'E-mail já cadastrado.')
        except Exception as e:
            messages.error(request, 'Ocorreu um erro ao enviar o link de redefinição de senha.')
            print(f'Ocorreu um erro ao enviar o link de redefinição de senha: {e}')
    
    return render(request, 'accounts/reset.html', {'form': form})

def login_google(request):
    if request.method == 'POST':
        # Recupera o ID do token enviado pelo cliente
        id_token = request.POST.get('idtoken')

        try:
            # Verifica se o token é válido
            google_request = Request()
            credentials, _ = google.auth.default(scopes=['openid', 'email', 'profile'])
            id_info = id_token.verify_oauth2_token(id_token, google_request, credentials.client_id) # type: ignore
            uid = id_info['sub']

            # Verifica se o usuário existe no Firestore
            usuario = Usuario.buscar(uid)
            if usuario is None:
                messages.error(request, 'Usuário não encontrado')
                return redirect('login')

            # Verifica se o tipo de usuário é válido e redireciona para a página apropriada
            if usuario['tipo'] == 'cliente':
                return redirect('caradapio')
            else:
                messages.error(request, 'Tipo de usuário inválido')
                return redirect('login')
        except ValueError as e:
            messages.error(request, 'Erro ao fazer login com o Google')
            print(f'Ocorreu um erro ao realizar login com o Google: {e}')
            return redirect('login')
    else:
        return render(request, 'login.html')