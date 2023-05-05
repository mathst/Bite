from firebase_admin import credentials, auth as firebase_auth, firestore as db

from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .models import Usuario, TipoUsuario
# from .forms import ClienteCreationForm, FuncionarioCreationForm, AdministradorCreationForm
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_protect
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

# logger.debug('Debug message')
# logger.info('Info message')
# logger.warning('Warning message')
# logger.error('Error message')
# logger.critical('Critical message')

@cache_page(60 * 15) # cache for 15 minutes
def cardapio(request):
    # Lógica para listar produtos em estoque
    return render(request, 'cardapio.html')
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
def comanda(request):
    return render(request, "comanda.html") 

def index(request):
    return render(request, "index.html") 

# Autentica o usuário usando o Google
# def authenticate_with_google(request):
#     id_token = request.POST.get('id_token')

#     decoded_token = firebase_auth.verify_id_token(id_token)

#     if decoded_token is None:
#         return JsonResponse({'error': 'Invalid ID token'}, status=400)

#     email = decoded_token['email']
#     firebase_user = firebase_auth.get_user_by_email(email)

#     try:
#         user = UsuarioCustomizado.objects.get(email=email)
#     except UsuarioCustomizado.DoesNotExist:
#         user = UsuarioCustomizado(email=email, username=email)
#         user.set_unusable_password()
#         user.save()

#     if user is not None:
#         login(request, user)
#         return JsonResponse({'redirect_url': '/cardapio/'})
#     else:
#         return JsonResponse({'error': 'Failed to authenticate user'}, status=400)


@login_required
@cache_page(60 * 15) # cache for 15 minutes
def dashboard_admin(request):
    return render(request, 'dashboard_admin.html')

@login_required
def dashboard_funcionario(request):
    return render(request, 'dashboard_funcionario.html')

@csrf_protect
def cadastrar_usuario_cli(request):
    if request.method == 'POST':
        nome = request.POST['nome']
        email = request.POST['email']
        telefone = request.POST['telefone']
        tipo = TipoUsuario.CLI
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        # Verifica se as senhas são iguais
        if password != confirm_password:
            messages.error(request, 'As senhas não são iguais')
            return redirect('cadastrar_usuario')

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
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Ocorreu um erro ao cadastrar o usuário: {e}')
            return redirect('cadastrar_usuario')
    else:
        return render(request, 'cadastrar_usuario.html')
    
@csrf_protect
def cadastrar_usuario_func(request):
    if request.method == 'POST':
        nome = request.POST['nome']
        email = request.POST['email']
        telefone = request.POST['telefone']
        tipo = TipoUsuario.FUN
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        # Verifica se as senhas são iguais
        if password != confirm_password:
            messages.error(request, 'As senhas não são iguais')
            return redirect('login')

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
            return redirect('login')
    else:
        return render(request, 'cadastrar_func.html')

@csrf_protect
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        tipo = None

        try:
            uid = request.POST.get('uid')
            decoded_token = firebase_auth.verify_id_token(uid)
            tipo = decoded_token.get('tipo')
        except:
            messages.error(request, 'Erro ao fazer login')
            return render(request, 'login', {'error_message': 'Usuário ou senha inválidos.'})
            # return redirect('login')

        if tipo == 'funcionario':
            funcionario = Usuario.carregar(uid)
            if funcionario is None:
                messages.error(request, 'Funcionário não encontrado')
                return render(request, 'login', {'error_message': 'Usuário ou senha inválidos.'})
                # return redirect('login')
            request.session['user'] = funcionario.to_dict()
            return redirect('pagina-do-funcionario')
        elif tipo == 'cliente':
            cliente = Usuario.carregar(uid)
            if cliente is None:
                messages.error(request, 'Cliente não encontrado')
                return redirect('login')
            request.session['user'] = cliente.to_dict()
            return redirect('pagina-do-cliente')
        elif tipo == 'admin':
            admin = Usuario.carregar(uid)
            if admin is None:
                messages.error(request, 'Admin não encontrado')
                return redirect('login')
            request.session['user'] = admin.to_dict()
            request.session['user'] = {'email': email, 'tipo': '0'}
            return redirect('pagina-do-admin')
        else:
            messages.error(request, 'Tipo de conta inválido')
            return redirect('login')

    return render(request, 'accounts/login.html')